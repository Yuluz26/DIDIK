"""The numbers on the dashboard. Days and hours follow the owner's clock (AdminSettings.timezone)."""

from __future__ import annotations

import time
from collections import Counter
from datetime import UTC, date, datetime, time as dtime, timedelta, tzinfo
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..activity import aware, iso
from ..game.manager import RoomManager
from ..game.modes import MODES
from ..models import ActivityEvent, Quiz, User
from ..seed import DEMO_EMAIL, LIBRARY_EMAIL

SYSTEM_EMAILS = (DEMO_EMAIL, LIBRARY_EMAIL)
PERIODS = (7, 14, 30, 90)


def real_users():
    return User.email.not_in(SYSTEM_EMAILS)


def real_quizzes():
    return Quiz.is_sample.is_(False)


def _day_start(day: date, tz: tzinfo) -> datetime:
    return datetime.combine(day, dtime.min, tzinfo=tz).astimezone(UTC)


def _bucket(values: list[datetime], tz: tzinfo, days: list[str]) -> list[int]:
    counts = Counter(aware(v).astimezone(tz).strftime("%Y-%m-%d") for v in values)
    return [counts.get(day, 0) for day in days]


def _event_days(db: Session, kind: str, first: str, days: list[str]) -> list[int]:
    rows = dict(
        db.execute(
            select(ActivityEvent.day, func.count()).where(ActivityEvent.kind == kind, ActivityEvent.day >= first).group_by(ActivityEvent.day)
        ).all()
    )
    return [rows.get(day, 0) for day in days]


def _metric(series: list[int], total: int, days: int) -> dict[str, Any]:
    """`series` covers the previous period and this one, oldest first."""
    now, before = series[days:], series[:days]
    return {"total": total, "period": sum(now), "previous": sum(before), "series": now}


def overview(db: Session, tz: tzinfo, days: int) -> dict[str, Any]:
    days = days if days in PERIODS else 14
    today = datetime.now(tz).date()
    span = [(today - timedelta(days=offset)).isoformat() for offset in range(days * 2 - 1, -1, -1)]  # previous + this period
    first = span[0]
    since = _day_start(date.fromisoformat(first), tz)

    users = db.scalars(select(User.created_at).where(real_users(), User.created_at >= since)).all()
    quizzes = db.scalars(select(Quiz.created_at).where(real_quizzes(), Quiz.created_at >= since)).all()
    parents_total = db.scalar(select(func.count()).select_from(User).where(real_users())) or 0
    quizzes_total = db.scalar(select(func.count()).select_from(Quiz).where(real_quizzes())) or 0

    this_period = span[days:]
    modes = db.execute(
        select(ActivityEvent.subject, func.count())
        .where(ActivityEvent.kind == "room.opened", ActivityEvent.day >= this_period[0])
        .group_by(ActivityEvent.subject)
        .order_by(func.count().desc())
    ).all()
    played = db.execute(
        select(ActivityEvent.subject, func.count())
        .where(ActivityEvent.kind == "player.joined", ActivityEvent.day >= this_period[0])
        .group_by(ActivityEvent.subject)
        .order_by(func.count().desc())
    ).all()

    return {
        "days": days,
        "from": this_period[0],
        "to": this_period[-1],
        "parents": _metric(_bucket(users, tz, span), parents_total, days),
        "quizzes": _metric(_bucket(quizzes, tz, span), quizzes_total, days),
        "students": _metric(_event_days(db, "player.joined", first, span), 0, days),
        "games": _metric(_event_days(db, "game.finished", first, span), 0, days),
        "rooms": _metric(_event_days(db, "room.opened", first, span), 0, days),
        "modes": [{"key": key or "?", "title": _title(key), "count": count} for key, count in modes],
        "studentsByMode": [{"key": key or "?", "title": _title(key), "count": count} for key, count in played],
        "heatmap": heatmap(db, today),
        "recentUsers": [user_row(u, 0) for u in db.scalars(select(User).where(real_users()).order_by(User.id.desc()).limit(6)).all()],
        "recentQuizzes": [
            {"id": q.id, "title": q.title, "owner": q.owner.name, "questions": len(q.questions), "createdAt": iso(q.created_at)}
            for q in db.scalars(select(Quiz).where(real_quizzes()).order_by(Quiz.id.desc()).limit(6)).all()
        ],
    }


def _title(key: str | None) -> str:
    mode = MODES.get(key or "")
    return mode.title if mode else (key or "?")


def heatmap(db: Session, today: date) -> dict[str, Any]:
    """Children joining, by weekday (Monday first) and hour, over the last four weeks."""
    first = (today - timedelta(days=27)).isoformat()
    grid = [[0] * 24 for _ in range(7)]
    for day, hour, count in db.execute(
        select(ActivityEvent.day, ActivityEvent.hour, func.count())
        .where(ActivityEvent.kind == "player.joined", ActivityEvent.day >= first)
        .group_by(ActivityEvent.day, ActivityEvent.hour)
    ):
        grid[date.fromisoformat(day).weekday()][hour] += count
    return {"grid": grid, "max": max((max(row) for row in grid), default=0), "weeks": 4}


def user_row(user: User, quizzes: int) -> dict[str, Any]:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "createdAt": iso(user.created_at),
        "lastLoginAt": iso(user.last_login_at),
        "disabled": user.disabled_at is not None,
        "system": user.email in SYSTEM_EMAILS,
        "quizzes": quizzes,
    }


# ---------------------------------------------------------------- live


def host_names(db: Session, ids: set[int], known: dict[int, str]) -> dict[int, str]:
    missing = ids - known.keys()
    if missing:
        for user_id, name in db.execute(select(User.id, User.name).where(User.id.in_(missing))):
            known[user_id] = name
    return known


def live(rooms: RoomManager, names: dict[int, str]) -> dict[str, Any]:
    """Rooms open right now and the children in them. Read on the event loop, where rooms change."""
    now = time.time()
    items = []
    online = 0
    children = 0
    for room in list(rooms.by_code.values()):
        humans = [p for p in room.players.values() if not p.is_bot]
        here = sum(1 for p in humans if p.connected)
        online += here
        children += len(humans)
        items.append(
            {
                "code": room.code,
                "mode": room.mode_key,
                "modeTitle": room.mode_cls.title,
                "quiz": room.quiz_title,
                "host": names.get(room.host_id, "?"),
                "hostId": room.host_id,
                "phase": room.phase,
                "locked": room.locked,
                "players": len(humans),
                "online": here,
                "age": int(now - room.created),
            }
        )
    items.sort(key=lambda r: (-r["online"], r["age"]))
    return {"at": iso(datetime.now(UTC)), "rooms": items, "online": online, "children": children}


def room_detail(rooms: RoomManager, code: str, names: dict[int, str]) -> dict[str, Any] | None:
    room = rooms.by_code.get(code)
    if room is None:
        return None
    base = live(rooms, names)["rooms"]
    summary = next((r for r in base if r["code"] == code), {})
    people = sorted((p for p in room.players.values() if not p.is_bot), key=lambda p: p.joined_at)
    return summary | {
        "people": [
            {"id": p.id, "name": p.nickname, "avatar": p.avatar, "online": p.connected, "approved": p.approved, "score": p.score}
            for p in people
        ]
    }
