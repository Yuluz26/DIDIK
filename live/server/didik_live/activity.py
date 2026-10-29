"""What happens on the site, told to the owner's control room.

Anything that matters (a parent signs up, a quiz is written, a room opens, a child joins, a game ends) calls
`bus.emit(...)`. It may be called from any thread, costs a queue put, and never blocks: a background task
writes the events to the database in batches and hands them to the dashboards that are open.

Without a control room (no DIDIK_ADMIN_* settings) the app has a `NullBus`, and nothing is recorded: children
are not logged on a site whose owner has no use for it.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import queue
import threading
import time
from collections.abc import Hashable
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import delete

from .db import Database
from .models import ActivityEvent, AdminNotification, AdminOtp, AdminSession

log = logging.getLogger("didik.activity")

KEEP_DAYS = 90
LISTENER_BACKLOG = 200


def zone(name: str) -> tzinfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, OSError):
        # A server without a time zone database still keeps the owner's clock (Malaysia has no daylight saving).
        log.warning("Zon masa %s tidak dijumpai; menggunakan UTC+8.", name)
        return timezone(timedelta(hours=8))


def _device(agent: str) -> str:
    """"Chrome di Linux": enough to recognise one's own browser in a notification, without the user-agent string."""
    browser = next((name for mark, name in (("Edg/", "Edge"), ("Chrome/", "Chrome"), ("Firefox/", "Firefox"), ("Safari/", "Safari")) if mark in agent), "Pelayar")
    system = next((name for mark, name in (("iPhone", "iOS"), ("iPad", "iOS"), ("Android", "Android"), ("Windows", "Windows"), ("Mac OS", "macOS"), ("Linux", "Linux")) if mark in agent), "")
    return f"{browser} di {system}" if system else browser


def aware(value: datetime) -> datetime:
    """SQLite hands datetimes back without their zone; everything stored here is UTC."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def iso(value: datetime | None) -> str | None:
    return aware(value).isoformat().replace("+00:00", "Z") if value else None


def event_out(row: ActivityEvent) -> dict[str, Any]:
    return {"id": row.id, "at": iso(row.at), "kind": row.kind, "summary": row.summary, "data": row.data or {}}


def notification_out(row: AdminNotification) -> dict[str, Any]:
    return {
        "id": row.id,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
        "title": row.title,
        "body": row.body,
        "level": row.level,
        "source": row.source,
        "pinned": row.pinned,
        "read": row.read_at is not None,
    }


class NullBus:
    """The bus of a site with no control room: every call does nothing."""

    def emit(self, kind: str, summary: str, *, subject: str | None = None, coalesce: tuple[Hashable, float] | None = None, **data: Any) -> None:
        return None

    def publish(self, message: dict[str, Any]) -> None:
        return None


class AdminBus(NullBus):
    def __init__(self, database: Database, timezone_name: str) -> None:
        self.database = database
        self.tz = zone(timezone_name)
        self._pending: queue.SimpleQueue[dict[str, Any]] = queue.SimpleQueue()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._wake: asyncio.Event | None = None
        self._task: asyncio.Task | None = None
        self._stopping = False
        self._listeners: set[asyncio.Queue[dict[str, Any]]] = set()
        self._recent: dict[Hashable, float] = {}
        self._lock = threading.Lock()
        self._housekept = 0.0

    # ------------------------------------------------------------ writing events (any thread)

    def emit(self, kind: str, summary: str, *, subject: str | None = None, coalesce: tuple[Hashable, float] | None = None, **data: Any) -> None:
        """Records one event. With `coalesce=(key, seconds)`, the same kind and key within that time is skipped
        (a quiz saved every few seconds is one event, a flood of wrong codes is one line)."""
        if coalesce is not None and self._seen_lately((kind, coalesce[0]), coalesce[1]):
            return
        self._pending.put({"at": datetime.now(UTC), "kind": kind, "subject": subject, "summary": summary[:200], "data": data})
        self._poke()

    def publish(self, message: dict[str, Any]) -> None:
        """Tells the open dashboards something that is not an event (a notification was edited). Any thread."""
        loop = self._loop
        if loop is not None:
            with contextlib.suppress(RuntimeError):
                loop.call_soon_threadsafe(self._broadcast, message)

    def _seen_lately(self, key: Hashable, seconds: float) -> bool:
        now = time.monotonic()
        with self._lock:
            if now - self._recent.get(key, -1e9) < seconds:
                return True
            self._recent[key] = now
            if len(self._recent) > 5000:
                self._recent = {k: t for k, t in self._recent.items() if now - t < 600}
        return False

    def _poke(self) -> None:
        loop, wake = self._loop, self._wake
        if loop is not None and wake is not None:
            with contextlib.suppress(RuntimeError):  # the loop has closed: the server is stopping
                loop.call_soon_threadsafe(wake.set)

    # ------------------------------------------------------------ dashboards listening (event loop)

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        listener: asyncio.Queue[dict[str, Any]] = asyncio.Queue(LISTENER_BACKLOG)
        self._listeners.add(listener)
        return listener

    def unsubscribe(self, listener: asyncio.Queue[dict[str, Any]]) -> None:
        self._listeners.discard(listener)

    def _broadcast(self, message: dict[str, Any]) -> None:
        for listener in self._listeners:
            if listener.full():
                with contextlib.suppress(asyncio.QueueEmpty):
                    listener.get_nowait()  # a dashboard that stopped reading loses its oldest news, not the server's memory
            with contextlib.suppress(asyncio.QueueFull):
                listener.put_nowait(message)

    # ------------------------------------------------------------ the writer

    def start(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._wake = asyncio.Event()
        self._stopping = False
        self._task = asyncio.create_task(self._run())
        if not self._pending.empty():
            self._wake.set()

    async def stop(self) -> None:
        """Writes what is still waiting, then ends."""
        self._stopping = True
        if self._task is not None and self._wake is not None:
            self._wake.set()
            await self._task
            self._task = None

    async def _run(self) -> None:
        assert self._wake is not None
        while True:
            await self._wake.wait()
            self._wake.clear()
            await self._drain()
            if self._stopping and self._pending.empty():
                return

    async def _drain(self) -> None:
        events: list[dict[str, Any]] = []
        while True:
            try:
                events.append(self._pending.get_nowait())
            except queue.Empty:
                break
        if not events:
            return
        try:
            stored, notes = await asyncio.to_thread(self._store, events)
        except Exception:  # noqa: BLE001 - one bad batch must not stop the next
            log.exception("%d peristiwa tidak dapat disimpan", len(events))
            return
        for item in stored:
            self._broadcast({"t": "event", "event": item})
        for note in notes:
            self._broadcast({"t": "notification", "notification": note})

    def _store(self, events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        with self.database.sessions() as db:
            rows = []
            for event in events:
                local = event["at"].astimezone(self.tz)
                row = ActivityEvent(
                    at=event["at"],
                    kind=event["kind"],
                    subject=event["subject"],
                    summary=event["summary"],
                    data=event["data"],
                    day=local.strftime("%Y-%m-%d"),
                    hour=local.hour,
                )
                db.add(row)
                rows.append(row)
            db.flush()
            notes = [note for row in rows for note in self._rules(row)]
            db.add_all(notes)
            db.flush()
            self._housekeeping(db)
            db.commit()
            return [event_out(row) for row in rows], [notification_out(note) for note in notes]

    @staticmethod
    def _rules(row: ActivityEvent) -> list[AdminNotification]:
        """The events the owner should hear about without looking: they also become notifications."""
        data = row.data or {}
        if row.kind == "user.signup":
            return [AdminNotification(title="Ibu bapa baharu", body=f"{data.get('name', '?')} ({data.get('email', '?')}) baru mendaftar.", level="info", source="system")]
        if row.kind == "admin.signin" and data.get("newIp"):
            return [AdminNotification(title="Log masuk admin dari alamat baharu", body=f"{data.get('ip', '?')} · {_device(str(data.get('agent', '')))}", level="warning", source="system")]
        return []

    def _housekeeping(self, db: Any) -> None:
        now = time.monotonic()
        if now - self._housekept < 3600:
            return
        self._housekept = now
        current = datetime.now(UTC)
        db.execute(delete(ActivityEvent).where(ActivityEvent.at < current - timedelta(days=KEEP_DAYS)))
        db.execute(delete(AdminOtp).where(AdminOtp.expires_at < current - timedelta(days=1)))
        db.execute(delete(AdminSession).where(AdminSession.expires_at < current - timedelta(days=30)))
