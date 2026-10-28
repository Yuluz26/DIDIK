"""A live room: the host, the children, the chosen game and the messages between them.

State changes only ever happen in plain synchronous code on the event loop, so two messages can never
interleave halfway through an update. Views are sent from one loop ten times a second at most, and only
to connections whose view actually changed.

A room can be saved as plain JSON (`save`) and brought back from it (`restore`), which is how a room
survives a restart of the server: phones and the host screen reconnect on their own and find it there.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import math
import random
import time
from collections import deque
from typing import TYPE_CHECKING, Any

from ..questions import parse_questions
from . import names, plaza
from .modes import MODES
from .modes.base import now_ms
from .player import Conn, Player, dumps
from .settings import RoomSettings

if TYPE_CHECKING:
    from .manager import RoomManager

log = logging.getLogger("didik.room")

STICKERS = {"hati", "bintang", "ketawa", "tepuk", "wah", "ok", "api", "pelangi"}
MAX_BOTS = 12
SAVE_VERSION = 1
# After a restart, a running game waits (paused) for the children who were connected just before it,
# but never longer than this.
RESTART_GRACE = 20.0
RECENTLY_SEEN = 30.0


class JoinError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class Room:
    def __init__(
        self,
        manager: RoomManager,
        *,
        code: str,
        slug: str,
        host_id: int,
        quiz_id: int,
        quiz_title: str,
        questions: list[Any],
        mode_key: str,
        settings: RoomSettings,
        allow_bots: bool = True,
    ) -> None:
        self.manager = manager
        self.code = code
        self.slug = slug
        self.host_id = host_id
        self.quiz_id = quiz_id
        self.quiz_title = quiz_title
        self.questions = questions
        self.mode_key = mode_key
        self.settings = settings
        self.allow_bots = allow_bots

        self.players: dict[str, Player] = {}
        self.hosts: set[Conn] = set()
        self.phase = "lobby"
        self.locked = False
        self.mode: Any = None
        self.mode_task: asyncio.Task | None = None
        self.results: dict[str, Any] | None = None
        self.round = 1
        self.created = time.time()
        self.touched = time.monotonic()
        self.rng = random.Random()
        self.dirty = True
        # Bumped on every change; the manager saves the room when it differs from the saved one.
        self.revision = 0
        self.saved_revision = -1
        self._comeback: asyncio.Task | None = None
        self._feed: deque[dict[str, Any]] = deque(maxlen=10)
        self._feed_id = 0
        self._tasks: set[asyncio.Task] = set()
        self._closing = False
        self._last_roster = ""
        # what every view of one flush shares (see flush)
        self._memo: dict[str, Any] | None = None
        self._seq = 0

    # ------------------------------------------------------------ plumbing

    @property
    def mode_cls(self) -> Any:
        return MODES[self.mode_key]

    def spawn(self, coro: Any) -> asyncio.Task:
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    def start(self) -> None:
        self.spawn(self._flush_loop())
        self.spawn(self._bot_loop())

    def close(self, message: str = "Bilik ini sudah ditutup.") -> None:
        self._closing = True
        for task in list(self._tasks):
            task.cancel()
        notice = {"t": "closed", "message": message}
        for conn in list(self.hosts):
            conn.send(notice)
            conn.close()
        for player in self.players.values():
            player.send(notice)
            for conn in list(player.conns):
                conn.close()

    def mark_dirty(self) -> None:
        self.dirty = True
        self.revision += 1
        self.touched = time.monotonic()

    def has_people(self) -> bool:
        return bool(self.hosts) or any(p.conns and not p.is_bot for p in self.players.values())

    async def _flush_loop(self) -> None:
        while not self._closing:
            await asyncio.sleep(0.1)
            if self.dirty:
                self.dirty = False
                try:
                    self.flush()
                except Exception:  # noqa: BLE001 - one bad view must not stop the room
                    log.exception("view failed in room %s", self.code)

    def flush(self) -> None:
        # Nothing in a flush waits, so the room cannot change during it: what every view shares is
        # made once (the room's info here, the ranking and shared world in the mode).
        self._memo = {}
        if self.mode is not None:
            self.mode.view_memo = {}
        try:
            self._flush()
        finally:
            self._memo = None
            if self.mode is not None:
                self.mode.view_memo = None

    def _flush(self) -> None:
        now = now_ms()
        roster = dumps({"t": "roster", "players": self.roster()})
        roster_changed = roster != self._last_roster
        self._last_roster = roster

        if self.hosts:
            text = dumps(self.host_view())
            for conn in list(self.hosts):
                self._deliver(conn, text, now, roster if roster_changed else None)
        for player in list(self.players.values()):
            if player.is_bot or not player.conns:
                continue
            text = dumps(self.player_view(player))
            for conn in list(player.conns):
                self._deliver(conn, text, now, roster if roster_changed else None)

    def _deliver(self, conn: Conn, view: str, now: int, roster: str | None) -> None:
        if conn.closed:
            return
        if roster is not None or not conn.last_view:
            conn.send_latest("roster", roster if roster is not None else self._last_roster)
        if conn.last_view != view:
            conn.last_view = view
            conn.send_latest("view", f'{{"t":"view","now":{now},"view":{view}}}')

    def resend(self, conn: Conn) -> None:
        """A fresh connection gets everything on the next flush."""
        conn.last_view = ""
        self.mark_dirty()

    async def _bot_loop(self) -> None:
        while not self._closing:
            await asyncio.sleep(0.25)
            if self.phase == "lobby":
                self.bots_stroll()
                continue
            if self.phase != "playing" or self.mode is None:
                continue
            now = time.monotonic()
            for bot in [p for p in self.players.values() if p.is_bot]:
                try:
                    self.mode.bot_tick(bot, now)
                except Exception:  # noqa: BLE001
                    log.exception("bot failed in room %s", self.code)

    def bots_stroll(self, chance: float = plaza.BOT_STROLL_CHANCE) -> None:
        """While everyone waits, practice bots wander the square now and then, like children do."""
        for bot in [p for p in self.players.values() if p.is_bot]:
            if self.rng.random() < chance:
                self.move(bot, *plaza.stroll(self.rng, *bot.spot))

    # ------------------------------------------------------------ messages out

    def fx(self, effect: dict[str, Any], to: Player | None = None, hosts: bool = True) -> None:
        message = {"t": "fx", **effect}
        if to is not None:
            to.send(message)
        else:
            for player in self.players.values():
                if player.approved:
                    player.send(message)
        if hosts:
            for conn in list(self.hosts):
                conn.send(message)

    def broadcast_latest(self, kind: str, message: dict[str, Any]) -> None:
        """A snapshot to every approved child and every host screen (forest positions): a phone
        that is behind gets only the newest."""
        text = dumps(message)
        conns = [c for p in self.players.values() if p.approved for c in p.conns] + list(self.hosts)
        for conn in conns:
            conn.send_latest(kind, text)

    def feed(self, text: str, kind: str = "info", player: Player | None = None) -> None:
        self._feed_id += 1
        self._feed.append({"id": self._feed_id, "text": text, "kind": kind, "player": player.id if player else None})
        self.mark_dirty()

    # ------------------------------------------------------------ views

    def info(self) -> dict[str, Any]:
        memo = self._memo
        if memo is not None:
            if "info" not in memo:
                memo["info"] = self._info()
            return memo["info"]
        return self._info()

    def _info(self) -> dict[str, Any]:
        reason = self.accepting_reason()
        return {
            "code": self.code,
            "slug": self.slug,
            "quizTitle": self.quiz_title,
            "mode": self.mode_cls.describe(),
            "phase": self.phase,
            "locked": self.locked,
            "customNames": self.settings.custom_names,
            "waitingRoom": self.settings.waiting_room,
            "accepting": reason is None,
            "reason": reason,
        }

    def accepting_reason(self) -> str | None:
        if self.locked:
            return "Hos telah mengunci bilik ini."
        if self.phase == "playing" and not self.settings.late_join:
            return "Permainan sudah bermula."
        if len([p for p in self.players.values() if not p.is_bot]) >= self.settings.max_players:
            return "Bilik ini sudah penuh."
        return None

    def roster(self) -> list[dict[str, Any]]:
        memo = self._memo
        if memo is not None:
            if "roster" not in memo:
                memo["roster"] = self._roster()
            return memo["roster"]
        return self._roster()

    def _roster(self) -> list[dict[str, Any]]:
        people = sorted(self.players.values(), key=lambda p: p.joined_at)
        return [
            {k: v for k, v in p.public().items() if k != "score"} | {"approved": p.approved} for p in people
        ]

    def base_view(self) -> dict[str, Any]:
        view = {
            "room": self.info(),
            "phase": self.phase,
            "round": self.round,
            "feed": list(self._feed),
        }
        if self._comeback is not None:
            view["resuming"] = True  # paused after a restart until everyone is back
        return view

    def plaza_view(self) -> list[list[Any]]:
        """Where everyone stands in the waiting room's square: [id, x, y, facing]."""
        return [[p.id, p.spot[0], p.spot[1], p.facing] for p in self.players.values() if p.approved]

    def player_view(self, player: Player) -> dict[str, Any]:
        view = self.base_view()
        view["me"] = {**player.public(), "approved": player.approved}
        if not player.approved:
            view["phase"] = "waiting"
            return view
        if self.phase == "lobby":
            view["plaza"] = self.plaza_view()
        elif self.phase == "playing" and self.mode is not None:
            view["game"] = self.mode.player_view(player)
        elif self.phase == "ended":
            view["results"] = self.results
        return view

    def host_view(self) -> dict[str, Any]:
        view = self.base_view()
        view["host"] = True
        view["settings"] = self.settings.model_dump()
        view["botsAllowed"] = self.allow_bots
        view["modes"] = [cls.describe(self.questions) for cls in MODES.values()]
        if self.phase == "lobby":
            view["plaza"] = self.plaza_view()
        elif self.phase == "playing" and self.mode is not None:
            view["game"] = self.mode.host_view()
        elif self.phase == "ended":
            view["results"] = self.results
        return view

    # ------------------------------------------------------------ joining

    def attach_host(self, conn: Conn) -> None:
        self.hosts.add(conn)
        self.resend(conn)

    def detach(self, conn: Conn) -> None:
        self.hosts.discard(conn)
        for player in self.players.values():
            if conn in player.conns:
                player.conns.discard(conn)
                player.seen = time.time()
                self.mark_dirty()

    def rejoin(self, conn: Conn, token: str) -> Player | None:
        for player in self.players.values():
            if player.owns(token):
                # A second tab with the same token while the first is still open joins as a new child
                # (handy for testing with tabs); a reconnecting phone takes its old place back.
                if any(not c.closed for c in player.conns):
                    return None
                player.conns.add(conn)
                self.resend(conn)
                return player
        return None

    def join(self, conn: Conn | None, data: dict[str, Any], bot: bool = False) -> Player:
        reason = self.accepting_reason()
        if reason and not bot:
            raise JoinError("closed", reason)

        avatar = data.get("avatar") if data.get("avatar") in names.ANIMALS else "kancil"
        colour = data.get("colour") if data.get("colour") in names.COLOURS else self.rng.choice(names.COLOURS)
        skin = data.get("skin") if data.get("skin") in names.SKINS else self.rng.choice(names.SKINS)
        taken = {p.nickname for p in self.players.values()}
        raw = str(data.get("name") or "")
        if bot:
            nickname = names.suggest(avatar, self.rng, taken)
        elif self.settings.custom_names:
            cleaned = names.clean_nickname(raw)
            if cleaned is None:
                raise JoinError("name", "Nama ini tidak boleh digunakan. Pilih nama lain.")
            nickname = names.unique(cleaned, taken)
        else:
            nickname = names.unique(raw, taken) if self._is_suggestion(raw) else names.suggest(avatar, self.rng, taken)

        self._seq += 1
        player = Player(
            id=f"p{self._seq}",
            nickname=nickname,
            avatar=avatar,
            colour=colour,
            skin=skin,
            is_bot=bot,
            approved=bot or not self.settings.waiting_room,
            spot=plaza.arrival(self.rng, crowd=len(self.players)),
        )
        if bot:
            player.skill = self.rng.uniform(0.55, 0.85)
        if conn is not None:
            player.conns.add(conn)
            self.resend(conn)
        self.players[player.id] = player
        if player.approved and self.phase == "playing" and self.mode is not None:
            self.mode.add_player(player)
        if player.approved:
            self.fx({"kind": "joined", "player": player.id}, hosts=True)
        self.mark_dirty()
        return player

    @staticmethod
    def _is_suggestion(name: str) -> bool:
        parts = name.split(" ")
        if len(parts) != 2 or parts[0] not in names.ANIMALS.values():
            return False
        return parts[1] in names.ADJECTIVES or (parts[1].isdigit() and len(parts[1]) == 2)

    # ------------------------------------------------------------ the game

    def start_game(self) -> str | None:
        if self.phase != "lobby":
            return "Permainan sudah bermula."
        reason = self.mode_cls.unplayable_reason(self.questions)
        if reason:
            return reason
        if not [p for p in self.players.values() if p.approved]:
            return "Belum ada pemain. Kongsi pautan bilik dahulu."
        for player in self.players.values():
            player.score = 0
            player.team = None
        self.results = None
        self._feed.clear()
        self.mode = self.mode_cls(self)
        self.mode.setup()
        self.phase = "playing"
        self.mode_task = self.spawn(self._run(self.mode))
        self.fx({"kind": "start"})
        self.mark_dirty()
        return None

    async def _run(self, mode: Any) -> None:
        try:
            await mode.run()
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            log.exception("game failed in room %s", self.code)
            if self.mode is mode:
                self.finish_game()

    def finish_game(self) -> None:
        if self.phase != "playing" or self.mode is None:
            return
        self.mode.finished = True
        self.results = self.mode.results()
        self.phase = "ended"
        if self.mode_task is not None and self.mode_task is not asyncio.current_task():
            self.mode_task.cancel()
        self.fx({"kind": "ended"})
        self.mark_dirty()

    def back_to_lobby(self) -> None:
        if self.phase == "playing":
            self.finish_game()
        self.phase = "lobby"
        self.mode = None
        self.results = None
        self.round += 1
        for player in self.players.values():
            player.score = 0
            player.team = None
        self.mark_dirty()

    # ------------------------------------------------------------ messages in

    def handle_host(self, conn: Conn, msg: dict[str, Any]) -> None:
        kind = msg.get("t")
        error: str | None = None
        if kind == "start":
            error = self.start_game()
        elif kind == "pause" and self.mode is not None and self.phase == "playing":
            self._stop_waiting()
            self.mode.pause()
        elif kind == "resume" and self.mode is not None and self.phase == "playing":
            self._stop_waiting()
            self.mode.resume()
        elif kind == "skip" and self.mode is not None and self.phase == "playing":
            self.mode.skip()
        elif kind == "end":
            self.finish_game()
        elif kind == "lobby":
            self.back_to_lobby()
        elif kind == "lock":
            self.locked = bool(msg.get("on"))
            self.mark_dirty()
        elif kind == "kick":
            self.kick(str(msg.get("id")))
        elif kind == "approve":
            self.approve(str(msg.get("id")), bool(msg.get("yes", True)))
        elif kind == "bots":
            current = sum(1 for p in self.players.values() if p.is_bot)
            error = self.set_bots(current + int(msg["change"]) if isinstance(msg.get("change"), int) else msg.get("count"))
        elif kind == "settings" and self.phase == "lobby":
            error = self.update_settings(msg.get("settings"))
        elif kind == "mode" and self.phase == "lobby":
            error = self.change_mode(str(msg.get("key")))
        elif kind == "ping":
            conn.send({"t": "pong"})
        if error:
            conn.send({"t": "error", "message": error})

    def handle_player(self, player: Player, msg: dict[str, Any]) -> None:
        kind = str(msg.get("t") or "")
        if kind == "ping":
            player.send({"t": "pong"})
            return
        if kind == "sticker":
            self.sticker(player, str(msg.get("id")))
            return
        if kind == "walk":
            self.walk(player, msg.get("x"), msg.get("y"))
            return
        if not player.approved or self.phase != "playing" or self.mode is None:
            return
        self.mode.handle(player, kind, msg)

    def walk(self, player: Player, x: Any, y: Any) -> None:
        """A child tapped a spot in the waiting room's square."""
        now = time.monotonic()
        if self.phase != "lobby" or not player.approved or now - player.last_walk < plaza.WALK_EVERY:
            return
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (x, y)):
            return
        try:
            tx, ty = float(x), float(y)
        except OverflowError:
            return
        if not (math.isfinite(tx) and math.isfinite(ty)):
            return
        player.last_walk = now
        self.move(player, *plaza.clamp(tx, ty))

    def move(self, player: Player, x: float, y: float) -> None:
        if abs(x - player.spot[0]) > 0.05:
            player.facing = 1 if x > player.spot[0] else -1
        player.spot = (x, y)
        self.mark_dirty()

    def sticker(self, player: Player, sticker: str) -> None:
        now = time.monotonic()
        if sticker not in STICKERS or now - player.last_sticker < 1.2 or not player.approved:
            return
        player.last_sticker = now
        self.fx({"kind": "sticker", "player": player.id, "sticker": sticker})

    def kick(self, player_id: str) -> None:
        player = self.players.pop(player_id, None)
        if player is None:
            return
        if self.mode is not None:
            self.mode.remove_player(player)
        player.send({"t": "kicked", "message": "Hos telah mengeluarkan kamu dari bilik ini."})
        for conn in list(player.conns):
            conn.close()
        self.mark_dirty()

    def approve(self, player_id: str, yes: bool) -> None:
        player = self.players.get(player_id)
        if player is None or player.approved:
            return
        if not yes:
            self.kick(player_id)
            return
        player.approved = True
        if self.phase == "playing" and self.mode is not None:
            self.mode.add_player(player)
        self.fx({"kind": "joined", "player": player.id})
        self.mark_dirty()

    def set_bots(self, count: Any) -> str | None:
        if not self.allow_bots:
            return "Pemain bot dimatikan pada pelayan ini."
        try:
            wanted = max(0, min(MAX_BOTS, int(count)))
        except (TypeError, ValueError):
            return "Bilangan bot tidak sah."
        bots = [p for p in self.players.values() if p.is_bot]
        for bot in bots[wanted:]:
            self.kick(bot.id)
        for _ in range(wanted - len(bots)):
            self.join(None, {"avatar": self.rng.choice(list(names.ANIMALS))}, bot=True)
        self.mark_dirty()
        return None

    def update_settings(self, raw: Any) -> str | None:
        if not isinstance(raw, dict):
            return "Tetapan tidak sah."
        try:
            self.settings = RoomSettings.model_validate({**self.settings.model_dump(), **raw})
        except ValueError:
            return "Tetapan tidak sah."
        self.mark_dirty()
        return None

    def change_mode(self, key: str) -> str | None:
        if key not in MODES:
            return "Permainan tidak dikenali."
        self.mode_key = key
        self.mark_dirty()
        return None

    def picture(self, token: str) -> bytes | None:
        getter = getattr(self.mode, "picture_bytes", None)
        return getter(token) if getter else None

    def idle_for(self) -> float:
        return time.monotonic() - self.touched

    def shutdown_quietly(self) -> None:
        with contextlib.suppress(Exception):
            self.close()

    # ------------------------------------------------------------ saving and restarts

    def save(self) -> dict[str, Any]:
        """The whole room as plain JSON. The manager writes it to the database every few seconds and
        when the server stops (see RoomManager)."""
        playing = self.phase == "playing" and self.mode is not None
        return {
            "v": SAVE_VERSION,
            "code": self.code,
            "slug": self.slug,
            "host": self.host_id,
            "quiz": self.quiz_id,
            "title": self.quiz_title,
            "questions": [q.model_dump(mode="json") for q in self.questions],
            "mode": self.mode_key,
            "settings": self.settings.model_dump(),
            "phase": self.phase,
            "locked": self.locked,
            "round": self.round,
            "created": self.created,
            "saved": time.time(),
            "results": self.results,
            "feed": list(self._feed),
            "feedId": self._feed_id,
            "seq": self._seq,
            "players": [p.save() for p in self.players.values()],
            "game": self.mode.save() if playing else None,
        }

    @classmethod
    def restore(cls, manager: RoomManager, data: dict[str, Any]) -> Room:
        """A room from `save`, not started yet (see `carry_on`). If its game cannot be brought back
        (a newer version of the server changed it), the room comes back in the lobby, children and
        all, so the host can simply start again."""
        mode_key = data["mode"] if data["mode"] in MODES else next(iter(MODES))
        settings = dict(data["settings"])
        if mode_key != data["mode"] and settings.get("max_players") == 1:
            settings["max_players"] = 2
        room = cls(
            manager,
            code=data["code"],
            slug=data["slug"],
            host_id=data["host"],
            quiz_id=data["quiz"],
            quiz_title=data["title"],
            questions=parse_questions(data["questions"]),
            mode_key=mode_key,
            settings=RoomSettings.model_validate(settings),
            allow_bots=manager.allow_bots,
        )
        room.locked = bool(data["locked"])
        room.round = int(data["round"])
        room.created = float(data["created"])
        room._feed.extend(data["feed"])
        room._feed_id = int(data["feedId"])
        room._seq = int(data["seq"])
        for saved in data["players"]:
            player = Player.restore(saved)
            room.players[player.id] = player
        room.phase = data["phase"]
        room.results = data["results"]
        if mode_key != data["mode"]:
            # Keep the quiz and rejoin tokens, but discard the retired game's state.
            room.back_to_lobby()
            room.feed("Permainan lama ini telah ditamatkan. Pilih permainan baharu di lobi untuk meneruskan kuiz yang sama.", "restart")
        if room.phase == "playing":
            try:
                if data["v"] != SAVE_VERSION or mode_key != data["mode"]:
                    raise ValueError("saved by another version")
                room.mode = room.mode_cls(room)
                room.mode.load(data["game"])
            except Exception:  # noqa: BLE001 - any saved game we cannot read goes back to the lobby
                log.warning("game in room %s could not be restored; back to the lobby", room.code, exc_info=True)
                room.mode = None
                room.back_to_lobby()
                room.feed("Permainan tadi tidak dapat disambung selepas pelayan dimulakan semula. Tekan Mula untuk bermain lagi.", "restart")
        return room

    def carry_on(self, saved_at: float, host_paused: bool) -> None:
        """Starts a restored room. A game that was running stays paused until the children who were
        connected just before the restart are back, so nobody loses time to it."""
        self.start()
        if self.phase != "playing" or self.mode is None:
            return
        self.mode_task = self.spawn(self._run(self.mode))
        if host_paused:
            return  # the host paused it before the restart and will resume it
        recent = saved_at - RECENTLY_SEEN
        expected = {p.id for p in self.players.values() if not p.is_bot and p.approved and p.seen >= recent}
        self._comeback = self.spawn(self._resume_when_back(expected))

    async def _resume_when_back(self, expected: set[str]) -> None:
        end = time.monotonic() + RESTART_GRACE
        while time.monotonic() < end:
            if all(p.connected for pid in expected if (p := self.players.get(pid)) is not None):
                break
            await asyncio.sleep(0.25)
        self._comeback = None
        self.mark_dirty()
        if self.mode is not None and self.phase == "playing":
            self.mode.resume()

    def _stop_waiting(self) -> None:
        """The host paused or resumed by hand: that decides, not the wait after a restart."""
        if self._comeback is not None:
            self._comeback.cancel()
            self._comeback = None
            self.mark_dirty()

    def suspend(self) -> None:
        """Stops the room for a restart without ending it: no "closed" notice, so phones and the host
        screen keep trying to reconnect and find the saved room when the server is back."""
        self._closing = True
        for task in list(self._tasks):
            task.cancel()
        for conn in list(self.hosts):
            conn.close()
        now = time.time()
        for player in self.players.values():
            if player.conns and player.connected:
                player.seen = now
            for conn in list(player.conns):
                conn.close()
