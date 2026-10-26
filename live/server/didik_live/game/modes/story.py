"""DIDIK Legenda: five Malaysian folklore worlds, driven by a parent's ten quiz questions.

The same mode runs with one child or with friends. Children have their own hearts
and journey; friends in the same realm share a five-hit boss. No answer keys are
ever sent before the answer is checked on the server.
"""
from __future__ import annotations

import asyncio
import math
import time
from typing import Any

from ...questions import Outcome, present
from .base import Seat, SelfPacedMode

HEARTS = 12  # Half hearts: 12 = six hearts, 3 = one-and-a-half.
BOSS_HEARTS = 5
SPEED = 3.8
TICK = 1 / 12
FOES = (5.0, 8.5, 12.0, 15.5, 19.0)
BOSS_X = 21.5
ELEMENTS = ("api", "angin", "petir", "tanah", "air")
HEROES = ("tuah", "jebat", "teja", "mahsuri", "saadong", "bendahara")
REALMS = (
    {"key": "chini", "title": "Tasik Chini", "boss": "Naga Chini", "element": "petir",
     "subtitle": "Di bawah kabus tasik, seekor naga menjaga rahsia lama."},
    {"key": "lupar", "title": "Batang Lupar", "boss": "Bujang Senang", "element": "api",
     "subtitle": "Sungai berarus gelap menyimpan bayang sang buaya legenda."},
    {"key": "larut", "title": "Hutan Larut", "boss": "Gajah Rimba", "element": "angin",
     "subtitle": "Gajah penjaga rimba menggegarkan denai hujan."},
    {"key": "kancil", "title": "Rimba Bayangan", "boss": "Sang Kancil Bayangan", "element": "tanah",
     "subtitle": "Akal si kancil diuji oleh jelmaan bayangnya sendiri."},
    {"key": "ledang", "title": "Gunung Ledang", "boss": "Penunggu Kabus", "element": "air",
     "subtitle": "Puncak berkabus menyimpan ujian terakhir para pendekar."},
)
# Fantasy interpretations inspired by regional folktales, not historical assertions.


class StoryMode(SelfPacedMode):
    key = "legenda"
    title = "Legenda: Story Mode"
    tagline = "Jelajah lima dunia legenda Melayu. Jawab soalan, tukar senjata elemen, tumbangkan boss!"
    how = "Bergerak ke arah halangan, jawab lima soalan, pilih senjata dan lawan boss. Main solo atau bersama kawan."
    style = "Pengembaraan RPG"
    pace = "roam"
    world = "legenda"
    look = "2d"
    unit = "mata"
    needs = "(apa-apa jenis)"
    min_questions = 10
    intro_seconds = 3.0
    saved = ("positions", "boss_hp")
    STORY_SECONDS = 55 * 60

    def __init__(self, room: Any) -> None:
        super().__init__(room)
        self.inputs: dict[str, tuple[float, float, float]] = {}
        self.ticker: asyncio.Task | None = None

    def setup(self) -> None:
        self.positions: dict[str, list[float]] = {}
        self.boss_hp: dict[str, int] = {str(i): BOSS_HEARTS for i in range(len(REALMS))}

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra = {
            "realm": 0, "phase": "obstacles", "obstacle": 0, "boss_turn": 0,
            "hearts": HEARTS, "weapon": "api", "weapons": False,
            "hero": "tuah", "cleared": [], "finished": False,
        }
        seat.step = "explore"
        self.positions[player.id] = [2.5, 10.0]

    def seat(self, player: Any) -> Seat:
        seat = self.seats.get(player.id)
        if seat is None:
            seat = self.seats[player.id] = Seat()
            self.new_seat(player, seat)
        return seat

    async def run(self) -> None:
        self.ticker = asyncio.create_task(self.tick_forever())
        try:
            if self.stage == "intro":
                await self.wait(self.intro_seconds)
                self.stage = "play"
                for player in self.players():
                    self.seat(player)
                self.room.mark_dirty()
            await self.wait(self.STORY_SECONDS, done=self.goal_reached)
            self.room.finish_game()
        finally:
            if self.ticker:
                self.ticker.cancel()

    def goal_reached(self) -> bool:
        players = self.players()
        return bool(players) and all(self.seat(p).extra["finished"] for p in players)

    def add_player(self, player: Any) -> None:
        if self.stage == "play":
            self.seat(player)

    def remove_player(self, player: Any) -> None:
        self.inputs.pop(player.id, None)
        self.positions.pop(player.id, None)
        self.seats.pop(player.id, None)

    def handle(self, player: Any, kind: str, data: dict[str, Any]) -> None:
        if self.stage != "play" or self.paused:
            return
        if kind == "move":
            try:
                dx, dy = float(data.get("dx", 0)), float(data.get("dy", 0))
            except (TypeError, ValueError):
                return
            if not math.isfinite(dx) or not math.isfinite(dy):
                return
            size = max(1.0, math.hypot(dx, dy))
            self.inputs[player.id] = (max(-1, min(1, dx / size)), max(-1, min(1, dy / size)), time.monotonic())
        else:
            super().handle(player, kind, data)

    async def tick_forever(self) -> None:
        last_sent = 0.0
        while not self.finished:
            await asyncio.sleep(TICK)
            if self.stage != "play" or self.paused:
                continue
            moved = False
            now = time.monotonic()
            for pid, (dx, dy, seen) in list(self.inputs.items()):
                seat = self.seats.get(pid)
                pos = self.positions.get(pid)
                if not seat or not pos or seat.step != "explore" or now - seen > 0.24:
                    continue
                extra = seat.extra
                if extra["finished"]:
                    continue
                boundary = BOSS_X if extra["phase"] == "boss" else FOES[min(4, extra["obstacle"])]
                before = pos[:]
                pos[0] = max(1.5, min(boundary - 0.65, pos[0] + dx * SPEED * TICK))
                pos[1] = max(7.5, min(12.0, pos[1] + dy * SPEED * TICK))
                moved |= before != pos
            if moved and now - last_sent >= 0.09:
                last_sent = now
                self.broadcast_positions()
                self.room.mark_dirty()

    def broadcast_positions(self) -> None:
        self.room.broadcast_latest("pos", {
            "t": "pos",
            "p": [[pid, round(x, 2), round(y, 2), 1] for pid, (x, y) in self.positions.items()],
        })

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if seat is None:
            return
        extra = seat.extra
        if kind == "hero" and seat.step == "explore" and data.get("hero") in HEROES:
            extra["hero"] = data["hero"]
        elif kind == "element" and extra["weapons"] and data.get("element") in ELEMENTS:
            extra["weapon"] = data["element"]
        elif kind == "retry" and seat.step == "dead":
            realm, hero = extra["realm"], extra["hero"]
            # A checkpoint retry never rewinds teammates' shared boss damage.
            self.new_seat(player, seat)
            extra.update(realm=realm, hero=hero, cleared=list(range(realm)))
            self.inputs.pop(player.id, None)
        elif kind == "engage" and seat.step == "explore" and not extra["finished"]:
            target = BOSS_X if extra["phase"] == "boss" else FOES[min(4, extra["obstacle"])]
            pos = self.positions.get(player.id, [0, 0])
            if abs(pos[0] - target) > 1.6:
                player.send({"t": "error", "message": "Berjalan lebih dekat kepada musuh dahulu."})
                return
            if extra["phase"] == "boss" and self.boss_hp[str(extra["realm"])] == 0:
                self.advance_realm(player, seat)
            else:
                self.deal_story(seat)
        else:
            return
        self.room.mark_dirty()

    def deal_story(self, seat: Seat) -> None:
        extra = seat.extra
        # Parents may create just ten questions. Reuse the same ten in later
        # realms, rotating the starting point when more questions are provided.
        start = extra["realm"] * 10
        if extra["phase"] == "obstacles":
            offset = extra["obstacle"]
        else:
            offset = 5 + (extra["boss_turn"] % 5)
        index = (start + offset) % len(self.questions)
        q = self.questions[index]
        seat.last_index = index
        seat.pres = present(q, self.rng, self.scaled(q.time_limit))
        seat.step = "question"
        seat.result = None
        self.inputs.pop(self.player_id_for(seat), None)

    def player_id_for(self, seat: Seat) -> str:
        return next((pid for pid, candidate in self.seats.items() if candidate is seat), "")

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any]:
        extra = seat.extra
        hit = bool(outcome.correct)
        extra["hearts"] = min(HEARTS, extra["hearts"] + 1) if hit else max(0, extra["hearts"] - 3)
        phase = extra["phase"]
        reward: dict[str, Any] = {"hearts": extra["hearts"], "phase": phase, "element": extra["weapon"]}
        if phase == "obstacles":
            extra["obstacle"] += 1
            if hit:
                player.score += 100
            else:
                self.room.fx({"kind": "story-hurt", "player": player.id, "realm": extra["realm"]})
        else:
            extra["boss_turn"] += 1
            if hit:
                key = str(extra["realm"])
                if self.boss_hp[key] > 0:
                    self.boss_hp[key] -= 1
                    strong = extra["weapon"] == REALMS[extra["realm"]]["element"]
                    player.score += 135 if strong else 100
                    reward.update(hit=True, bossHearts=self.boss_hp[key], bonus=strong)
                    self.room.fx({"kind": "story-hit", "player": player.id, "element": extra["weapon"],
                                  "realm": extra["realm"], "left": self.boss_hp[key]})
            else:
                self.room.fx({"kind": "story-hurt", "player": player.id, "realm": extra["realm"]})
        if extra["hearts"] == 0:
            reward["defeated"] = True
        return reward

    def act_next(self, player: Any) -> None:
        seat = self.seats.get(player.id)
        if not seat or seat.step != "result":
            return
        extra = seat.extra
        seat.pres = None
        seat.result = None
        if extra["hearts"] <= 0:
            seat.step = "dead"
        elif extra["phase"] == "obstacles" and extra["obstacle"] >= 5:
            extra["phase"] = "boss"
            extra["weapons"] = True
            self.positions[player.id] = [16.5, 10.0]
            seat.step = "explore"
            self.room.fx({"kind": "story-weapons", "player": player.id})
        elif extra["phase"] == "boss" and self.boss_hp[str(extra["realm"])] <= 0:
            self.advance_realm(player, seat)
        else:
            seat.step = "explore"
            self.positions[player.id] = [
                max(2.5, (BOSS_X if extra["phase"] == "boss" else FOES[extra["obstacle"]]) - 1.25),
                10.0,
            ]
        self.broadcast_positions()
        self.room.mark_dirty()

    def advance_realm(self, player: Any, seat: Seat) -> None:
        extra = seat.extra
        old = extra["realm"]
        if old not in extra["cleared"]:
            extra["cleared"].append(old)
        extra["realm"] += 1
        player.score += 350
        if extra["realm"] >= len(REALMS):
            extra["finished"] = True
            seat.step = "victory"
            self.room.fx({"kind": "story-victory", "player": player.id})
        else:
            extra.update(phase="obstacles", obstacle=0, boss_turn=0, hearts=HEARTS,
                         weapon="api", weapons=False)
            self.positions[player.id] = [2.5, 10.0]
            seat.step = "explore"
            self.room.fx({"kind": "story-world", "player": player.id, "realm": extra["realm"]})
        self.broadcast_positions()
        self.room.mark_dirty()

    def seat_view(self, player: Any) -> dict[str, Any]:
        result = super().seat_view(player)
        seat = self.seats.get(player.id)
        if seat:
            result["story"] = dict(seat.extra)
        return result

    def player_view(self, player: Any) -> dict[str, Any]:
        view = super().player_view(player)
        view["length"] = self.STORY_SECONDS
        return view

    def host_view(self) -> dict[str, Any]:
        view = super().host_view()
        view["length"] = self.STORY_SECONDS
        return view

    def world_view(self, player: Any | None) -> dict[str, Any]:
        if player is None:
            roster = self.players()
            leader = max(roster, key=lambda p: self.seat(p).extra["realm"]) if roster else None
            realm = min(self.seat(leader).extra["realm"], 4) if leader else 0
        else:
            realm = min(self.seat(player).extra["realm"], 4)
        peers = [
            {"id": p.id, "hero": self.seat(p).extra["hero"],
             "hearts": self.seat(p).extra["hearts"],
             "pos": self.positions.get(p.id, [2.5, 10.0])}
            for p in self.players()
            if min(self.seat(p).extra["realm"], 4) == realm
        ]
        return {
            "realm": realm,
            "total": len(REALMS),
            "scene": REALMS[realm],
            "bossHearts": self.boss_hp[str(realm)],
            "bossMax": BOSS_HEARTS,
            "foes": FOES,
            "bossX": BOSS_X,
            "players": peers,
        }

    def bot_step(self, bot: Any, seat: Seat) -> None:
        if seat.step == "explore":
            extra = seat.extra
            x = BOSS_X if extra["phase"] == "boss" else FOES[min(4, extra["obstacle"])]
            self.positions[bot.id] = [x - 0.8, 10.0]
            self.act(bot, seat, "engage", {})
        elif seat.step == "dead":
            self.act(bot, seat, "retry", {})

    def results(self) -> dict[str, Any]:
        rows = sorted(self.players(), key=lambda p: (-len(self.seat(p).extra["cleared"]), -p.score))
        return {"kind": "coop", "players": [
            {"id": p.id, "score": p.score, "rank": i + 1} for i, p in enumerate(rows)
        ], "summary": "Lima dunia legenda Melayu telah dijelajah."}
