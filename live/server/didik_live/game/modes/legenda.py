"""Legenda: Story Mode. Five Malaysian folklore worlds as a turn-based JRPG, driven by the parent's quiz.

Nobody walks: the heroes travel on their own, every enemy on the road starts a battle, and a child's
only moves are answering questions and, at the boss, choosing an element. The browser only animates
what this module decides.

Each child follows the same steps (`Seat.step`):

    select -> intro -> travel -> encounter -> question -> result -> clear -> travel ... (5 enemies)
    -> unlock -> gather -> reveal -> question -> result -> (wait) -> ... -> worldclear -> intro ...
    -> victory

and, when the hearts run out, `fallen` until the child taps Cuba lagi.

- Hearts are counted in halves: 12 is six hearts. A right answer heals one half (never above twelve);
  a wrong one is an attack nobody can dodge, three halves.
- On the road a wrong answer does not clear the enemy: it attacks, and the child gets another
  question for the same enemy. Five enemies cleared unlock the five elements.
- The boss of a world has five bars, shared by the children fighting it together (a `raid`). Each
  right answer is one hit, exactly one bar, whatever the element; a wrong answer never hurts the boss.
  The element only changes the attack the browser plays, and its weakness earns bonus points.
- A boss fight runs in rounds: each child answers one question per round, and the next round opens
  when everyone in the fight has answered (or the round's time is up). A fast child cannot beat the
  boss alone while friends are still reading. Before the fight, children wait at the boss gate for
  friends still on the road in the same world, for a minute at most.
- Falling keeps the checkpoint: the enemies already cleared, the unlocked elements, and the damage the
  boss has taken (friends' hits are never undone).
- Ten questions are enough: each child draws from their own shuffled deck of the whole quiz, reshuffled
  when it runs out, never the same question twice in a row, with the options reshuffled every time.

Every step change bumps the seat's `ev`; a `next` that names an older `ev` (a double tap, a message
from before a reconnect) is ignored.

The worlds and bosses are fantasy inspired by regional folklore, not claims about the legends.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, ClassVar

from ...questions import Outcome
from .base import Seat, SelfPacedMode

log = logging.getLogger("didik.legenda")

HEARTS = 12
HEAL = 1
HURT = 3
ENCOUNTERS = 5
BOSS_BARS = 5
ELEMENTS = ("api", "angin", "petir", "tanah", "air")
HEROES = ("tuah", "mahsuri")
# How long children wait at the boss gate for friends, and how long a boss round stays open.
GATHER_SECONDS = 60.0
ROUND_SECONDS = 45.0
# Steps where the browser plays a cinematic and then sends `next`.
CINEMATIC = ("intro", "travel", "encounter", "clear", "unlock", "reveal", "worldclear")

WORLDS: tuple[dict[str, str], ...] = (
    {
        "key": "chini",
        "title": "Tasik Chini",
        "boss": "Naga Chini",
        "weak": "petir",
        "foe": "Pengawal Teratai",
        "intro": "Kabus pagi menyelubungi tasik teratai. Di dasarnya, Naga Chini menjaga rahsia lama.",
        "clear": "Naga Chini tunduk. Teratai kembali mekar di seluruh tasik.",
    },
    {
        "key": "lupar",
        "title": "Batang Lupar",
        "boss": "Bujang Senang",
        "weak": "api",
        "foe": "Penjaga Bakau",
        "intro": "Senja di sungai Sarawak. Rumah panjang terdiam; sang buaya legenda sedang menunggu.",
        "clear": "Bujang Senang kembali ke dasar sungai. Perahu boleh berlayar semula.",
    },
    {
        "key": "larut",
        "title": "Hutan Larut",
        "boss": "Gajah Rimba",
        "weak": "angin",
        "foe": "Roh Paku Pakis",
        "intro": "Hutan hujan yang tua dan tebal. Langkah Gajah Rimba menggegarkan denai.",
        "clear": "Gajah Rimba memberi laluan. Cahaya matahari menembusi kanopi.",
    },
    {
        "key": "kancil",
        "title": "Rimba Bayangan",
        "boss": "Sang Kancil Bayangan",
        "weak": "tanah",
        "foe": "Pelita Sesat",
        "intro": "Bulan ungu di atas rimba. Sang Kancil Bayangan menguji akal sesiapa yang lalu.",
        "clear": "Ilusi pecah. Rimba Bayangan kembali tenang di bawah bulan.",
    },
    {
        "key": "ledang",
        "title": "Gunung Ledang",
        "boss": "Penunggu Kabus",
        "weak": "air",
        "foe": "Bayu Kabus",
        "intro": "Jambatan batu di puncak berkabus. Penunggu Kabus menanti ujian terakhir.",
        "clear": "Kabus terangkat dari puncak. Lima dunia legenda telah bebas!",
    },
)


def now_ms() -> int:
    return int(time.time() * 1000)


class LegendaMode(SelfPacedMode):
    key = "legenda"
    title = "Hikayat Lima Alam"
    tagline = "Wira kamu mengembara lima alam legenda Melayu. Jawab soalan untuk menyerang!"
    how = (
        "Wira berjalan sendiri. Setiap musuh membuka pertarungan: jawapan betul menyerang dan memulihkan "
        "separuh hati, jawapan salah kena serangan. Lima musuh membuka lima senjata elemen untuk melawan boss."
    )
    style = "Pengembaraan"
    pace = "self"
    world = "legenda"
    unit = "mata"
    needs = "(apa-apa jenis)"
    min_questions = 10
    saved: ClassVar[tuple[str, ...]] = ("raids", "active", "raid_seq")
    STORY_SECONDS = 90 * 60

    def __init__(self, room: Any) -> None:
        super().__init__(room)
        self.raids: dict[str, dict[str, Any]] = {}
        # The fight each world is running now, which late arrivals join.
        self.active: dict[str, str] = {}
        self.raid_seq = 0
        # Monotonic deadlines, rebuilt after a restart: per raid (round) and per world (gate).
        self.round_ends: dict[str, float] = {}
        self.gate_ends: dict[int, float] = {}
        self.pulse: asyncio.Task | None = None

    # ------------------------------------------------------------ lifecycle

    def setup(self) -> None:
        self.raids = {}
        self.active = {}
        self.raid_seq = 0

    def load(self, state: dict[str, Any]) -> None:
        super().load(state)
        later = time.monotonic() + ROUND_SECONDS
        self.round_ends = {rid: later for rid, raid in self.raids.items() if raid["hp"] > 0}

    async def run(self) -> None:
        self.pulse = asyncio.create_task(self.keep_time())
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
            self.pulse.cancel()

    async def keep_time(self) -> None:
        """Opens boss gates and boss rounds whose wait is over, a few times a second."""
        while not self.finished:
            await asyncio.sleep(0.25)
            if self.stage != "play" or self.paused:
                continue
            try:
                self.tick(time.monotonic())
            except Exception:  # noqa: BLE001 - one bad tick must not stop the story
                log.exception("tick failed in room %s", self.room.code)

    def pause(self) -> None:
        if not self.paused:
            self._paused_at = time.monotonic()
        super().pause()

    def resume(self) -> None:
        if self.paused:
            gap = time.monotonic() - getattr(self, "_paused_at", time.monotonic())
            self.round_ends = {k: v + gap for k, v in self.round_ends.items()}
            self.gate_ends = {k: v + gap for k, v in self.gate_ends.items()}
        super().resume()

    def goal_reached(self) -> bool:
        players = self.players()
        return bool(players) and all(self.seat(p).extra["finished"] for p in players)

    # ------------------------------------------------------------ seats

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra = {
            "hero": None,
            "world": 0,
            "phase": "road",
            "cleared": 0,
            "hearts": HEARTS,
            "elements": False,
            "element": "api",
            "raid": None,
            "ev": 0,
            "worlds": [],
            "falls": 0,
            "hits": 0,
            "finished": False,
        }
        seat.step = "select"

    def seat(self, player: Any) -> Seat:
        seat = self.seats.get(player.id)
        if seat is None:
            seat = self.seats[player.id] = Seat()
            self.new_seat(player, seat)
        return seat

    def go(self, seat: Seat, step: str) -> None:
        seat.step = step
        seat.extra["ev"] += 1
        if step not in ("question", "result"):
            seat.pres = None
            seat.result = None
        self.room.mark_dirty()

    def ask(self, seat: Seat) -> None:
        """Deals the seat's next question as a new step (see `SelfPacedMode.deal`). When the deck runs
        out and is shuffled again, the last few questions shown go to its far end, so a question
        never comes back within a few turns of itself."""
        if not seat.deck:
            seat.deck = list(range(len(self.questions)))
            self.rng.shuffle(seat.deck)
            recent = seat.extra.setdefault("recent", [])
            # The deck is dealt from its end: recent questions first in the list come out last.
            seat.deck.sort(key=lambda i: 0 if i in recent else 1)
        self.deal(seat)
        recent = seat.extra.setdefault("recent", [])
        recent.append(seat.last_index)
        del recent[: max(0, len(recent) - max(1, len(self.questions) // 3))]
        seat.extra["ev"] += 1
        self.room.mark_dirty()

    def remove_player(self, player: Any) -> None:
        self.seats.pop(player.id, None)
        for raid in self.raids.values():
            if player.id in raid["members"]:
                raid["members"].remove(player.id)
            if player.id in raid["answered"]:
                raid["answered"].remove(player.id)

    # ------------------------------------------------------------ messages

    def handle(self, player: Any, kind: str, data: dict[str, Any]) -> None:
        if self.stage != "play" or self.paused:
            return
        seat = self.seats.get(player.id)
        if seat is None:
            return
        ev = data.get("ev")
        if ev is not None and ev != seat.extra["ev"]:
            return  # a double tap, or a message about a step that has already moved on
        if kind == "answer":
            self.choose_element(seat, data.get("el"))
            self.act_answer(player, data.get("a"))
        elif kind == "next":
            self.act_next(player)
        elif kind == "hero":
            self.choose_hero(seat, data.get("hero"))
        elif kind == "element":
            self.choose_element(seat, data.get("element"))
        elif kind == "retry":
            self.retry(player, seat)

    def choose_hero(self, seat: Seat, hero: Any) -> None:
        if seat.step == "select" and hero in HEROES:
            seat.extra["hero"] = hero
            self.go(seat, "intro")

    def choose_element(self, seat: Seat, element: Any) -> None:
        if seat.extra["elements"] and element in ELEMENTS and element != seat.extra["element"]:
            seat.extra["element"] = element
            self.room.mark_dirty()

    def act_next(self, player: Any) -> None:
        seat = self.seats.get(player.id)
        if seat is None:
            return
        extra = seat.extra
        step = seat.step
        if step == "intro":
            self.go(seat, "travel")
        elif step == "travel":
            self.go(seat, "encounter")
        elif step == "encounter":
            self.ask(seat)
        elif step == "result":
            self.after_result(player, seat)
        elif step == "clear":
            if extra["cleared"] >= ENCOUNTERS:
                extra["elements"] = True
                self.go(seat, "unlock")
                self.room.fx({"kind": "story-unlock", "player": player.id}, to=player, hosts=False)
            else:
                self.go(seat, "travel")
        elif step == "unlock":
            extra["phase"] = "boss"
            self.go(seat, "gather")
            self.gate_ends.setdefault(extra["world"], time.monotonic() + GATHER_SECONDS)
            self.tick(time.monotonic())
        elif step == "reveal":
            raid = self.raids.get(extra["raid"] or "")
            if raid is None or raid["hp"] <= 0:
                self.world_won(player, seat)
            elif player.id in raid["answered"]:
                self.go(seat, "wait")
            else:
                self.ask(seat)
        elif step == "worldclear":
            self.next_world(player, seat)

    def after_result(self, player: Any, seat: Seat) -> None:
        extra = seat.extra
        if extra["hearts"] <= 0:
            extra["falls"] += 1
            self.go(seat, "fallen")
            return
        if extra["phase"] == "road":
            if seat.result and seat.result["correct"]:
                self.go(seat, "clear")
            else:
                self.ask(seat)  # the same enemy, a new question
            return
        raid = self.raids.get(extra["raid"] or "")
        if raid is None or raid["hp"] <= 0:
            self.world_won(player, seat)
        elif player.id in raid["answered"]:
            self.go(seat, "wait")
        else:
            self.ask(seat)

    def retry(self, player: Any, seat: Seat) -> None:
        if seat.step != "fallen":
            return
        extra = seat.extra
        extra["hearts"] = HEARTS
        if extra["phase"] == "road":
            self.go(seat, "encounter")
        else:
            raid = self.raids.get(extra["raid"] or "")
            if raid is None or raid["hp"] <= 0:
                self.world_won(player, seat)
            else:
                self.go(seat, "reveal")

    # ------------------------------------------------------------ answers

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any]:
        extra = seat.extra
        world = WORLDS[extra["world"]]
        right = bool(outcome.correct)
        before = extra["hearts"]
        extra["hearts"] = min(HEARTS, before + HEAL) if right else max(0, before - HURT)
        extra["ev"] += 1
        reward: dict[str, Any] = {
            "phase": extra["phase"],
            "hearts": extra["hearts"],
            "change": extra["hearts"] - before,
            "element": extra["element"],
        }
        if extra["phase"] == "road":
            if right:
                extra["cleared"] += 1
                player.score += 100
                reward["points"] = 100
            reward["cleared"] = extra["cleared"]
            return reward

        raid = self.raids.get(extra["raid"] or "")
        if raid is None:
            return reward
        if player.id not in raid["answered"]:
            raid["answered"].append(player.id)
        if right and raid["hp"] > 0:
            raid["hp"] -= 1
            extra["hits"] += 1
            weak = extra["element"] == world["weak"]
            points = 150 + (50 if weak else 0)
            player.score += points
            raid["log"].append({"by": player.id, "element": extra["element"], "weak": weak, "left": raid["hp"]})
            raid["log"] = raid["log"][-12:]
            reward.update(hit=True, weak=weak, points=points, bossHp=raid["hp"])
            self.room.fx({"kind": "story-hit", "player": player.id, "raid": raid["id"],
                          "element": extra["element"], "left": raid["hp"]})
            if raid["hp"] == 0:
                self.defeat_boss(raid)
        else:
            reward["bossHp"] = raid["hp"]
        self.maybe_next_round(raid, time.monotonic())
        return reward

    # ------------------------------------------------------------ the boss

    def tick(self, now: float) -> None:
        # Boss gates: open when nobody else in that world is still on the road, or when time is up.
        waiting: dict[int, list[str]] = {}
        for pid, seat in self.seats.items():
            if seat.step == "gather":
                waiting.setdefault(seat.extra["world"], []).append(pid)
        for world, pids in waiting.items():
            key = str(world)
            raid = self.raids.get(self.active.get(key, ""))
            if raid is not None and raid["hp"] > 0:
                for pid in pids:
                    self.enlist(raid, pid)
                continue
            if self.on_the_road(world) and now < self.gate_ends.get(world, now):
                continue
            raid = self.open_raid(world)
            for pid in pids:
                self.enlist(raid, pid)
            self.gate_ends.pop(world, None)
        for raid in list(self.raids.values()):
            if raid["hp"] > 0:
                self.maybe_next_round(raid, now)

    def on_the_road(self, world: int) -> bool:
        """Someone online in this world has not reached its boss gate yet."""
        for player in self.online():
            seat = self.seats.get(player.id)
            if seat is None or seat.extra["finished"] or seat.extra["world"] != world:
                continue
            if seat.extra["phase"] == "road" or seat.step in ("unlock", "select"):
                return True
        return False

    def open_raid(self, world: int) -> dict[str, Any]:
        self.raid_seq += 1
        rid = f"r{self.raid_seq}"
        raid = {"id": rid, "world": world, "hp": BOSS_BARS, "round": 1, "members": [], "answered": [],
                "log": [], "opened": now_ms()}
        self.raids[rid] = raid
        self.active[str(world)] = rid
        self.round_ends[rid] = time.monotonic() + self.scaled(ROUND_SECONDS)
        self.room.mark_dirty()
        return raid

    def enlist(self, raid: dict[str, Any], pid: str) -> None:
        seat = self.seats[pid]
        if pid not in raid["members"]:
            raid["members"].append(pid)
        seat.extra["raid"] = raid["id"]
        self.go(seat, "reveal")

    def fighting(self, raid: dict[str, Any]) -> list[str]:
        """Members who can still answer this round: online, and not fallen."""
        out = []
        for pid in raid["members"]:
            player = self.room.players.get(pid)
            seat = self.seats.get(pid)
            if player is None or seat is None or not player.connected or seat.step == "fallen":
                continue
            out.append(pid)
        return out

    def maybe_next_round(self, raid: dict[str, Any], now: float) -> None:
        if raid["hp"] <= 0:
            return
        fighting = self.fighting(raid)
        everyone = bool(fighting) and all(pid in raid["answered"] for pid in fighting)
        if not everyone and now < self.round_ends.get(raid["id"], now):
            return
        if not raid["answered"] and not everyone:
            # Nobody answered before the time ran out: give the round more time rather than skip it.
            self.round_ends[raid["id"]] = now + self.scaled(ROUND_SECONDS)
            return
        raid["round"] += 1
        raid["answered"] = []
        self.round_ends[raid["id"]] = now + self.scaled(ROUND_SECONDS)
        for pid in raid["members"]:
            seat = self.seats.get(pid)
            if seat is not None and seat.step == "wait":
                self.ask(seat)
        self.room.mark_dirty()

    def defeat_boss(self, raid: dict[str, Any]) -> None:
        self.round_ends.pop(raid["id"], None)
        if self.active.get(str(raid["world"])) == raid["id"]:
            del self.active[str(raid["world"])]
        for pid in raid["members"]:
            seat = self.seats.get(pid)
            if seat is not None and seat.step in ("question", "wait"):
                player = self.room.players.get(pid)
                if player is not None:
                    self.world_won(player, seat)
        self.room.mark_dirty()

    def world_won(self, player: Any, seat: Seat) -> None:
        extra = seat.extra
        if extra["world"] not in extra["worlds"]:
            extra["worlds"].append(extra["world"])
            player.score += 300
        self.go(seat, "worldclear")

    def next_world(self, player: Any, seat: Seat) -> None:
        extra = seat.extra
        extra["world"] += 1
        if extra["world"] >= len(WORLDS):
            extra["world"] = len(WORLDS) - 1
            extra["finished"] = True
            self.go(seat, "victory")
            self.room.fx({"kind": "story-victory", "player": player.id})
            return
        extra.update(phase="road", cleared=0, hearts=HEARTS, elements=False, element="api", raid=None)
        self.go(seat, "intro")

    # ------------------------------------------------------------ views

    def raid_view(self, raid: dict[str, Any] | None) -> dict[str, Any] | None:
        if raid is None:
            return None
        return {
            "id": raid["id"],
            "hp": raid["hp"],
            "max": BOSS_BARS,
            "round": raid["round"],
            "members": raid["members"],
            "answered": raid["answered"],
            "log": raid["log"][-4:],
            "ends": now_ms() + int(max(0.0, self.round_ends.get(raid["id"], 0) - time.monotonic()) * 1000)
            if raid["hp"] > 0 and not self.paused else None,
        }

    def peer(self, pid: str) -> dict[str, Any]:
        extra = self.seats[pid].extra
        return {"id": pid, "hero": extra["hero"], "hearts": extra["hearts"], "step": self.seats[pid].step,
                "element": extra["element"], "world": extra["world"], "cleared": extra["cleared"]}

    def seat_view(self, player: Any) -> dict[str, Any]:
        view = super().seat_view(player)
        seat = self.seats.get(player.id)
        if seat is None:
            return view
        extra = seat.extra
        raid = self.raids.get(extra["raid"] or "")
        view["story"] = {k: extra[k] for k in ("hero", "world", "phase", "cleared", "hearts", "elements",
                                               "element", "ev", "worlds", "falls", "hits", "finished")}
        view["raid"] = self.raid_view(raid) if extra["phase"] == "boss" else None
        if seat.step == "gather":
            world = extra["world"]
            view["gather"] = {
                "behind": sum(1 for p in self.online() if p.id in self.seats and p.id != player.id
                              and self.seats[p.id].extra["world"] == world
                              and self.seats[p.id].extra["phase"] == "road"),
                "ends": now_ms() + int(max(0.0, self.gate_ends.get(world, 0) - time.monotonic()) * 1000),
            }
        return view

    def world_view(self, player: Any | None) -> dict[str, Any]:
        if player is None:
            return {"worlds": WORLDS, "heroes": HEROES, "elements": ELEMENTS}
        seat = self.seats.get(player.id)
        world = seat.extra["world"] if seat else 0
        # Only this child's own hero is drawn on their battlefield, so no other heroes are sent.
        return {"scene": WORLDS[world], "index": world, "total": len(WORLDS),
                "party": len(self.players()) > 1, "encounters": ENCOUNTERS, "maxHearts": HEARTS}

    def player_view(self, player: Any) -> dict[str, Any]:
        view = super().player_view(player)
        view["length"] = self.STORY_SECONDS
        return view

    def host_view(self) -> dict[str, Any]:
        view = super().host_view()
        view["length"] = self.STORY_SECONDS
        view["party"] = [self.peer(pid) | {"worlds": self.seats[pid].extra["worlds"]} for pid in self.seats]
        view["raids"] = [self.raid_view(r) | {"world": r["world"]} for r in self.raids.values() if r["hp"] > 0]
        return view

    def results(self) -> dict[str, Any]:
        rows = sorted(self.players(), key=lambda p: (-len(self.seat(p).extra["worlds"]), -p.score, p.joined_at))
        best = max((len(self.seat(p).extra["worlds"]) for p in rows), default=0)
        if best >= len(WORLDS):
            headline = "Lima dunia legenda telah dibebaskan!"
        elif best:
            headline = f"{best} daripada {len(WORLDS)} dunia legenda dibebaskan."
        else:
            headline = "Pengembaraan baru bermula. Cuba lagi untuk menewaskan boss pertama!"
        return {
            "kind": "coop",
            "players": [{"id": p.id, "score": p.score, "rank": i + 1} for i, p in enumerate(rows)],
            "headline": headline,
            "note": "Setiap jawapan betul menyerang; setiap boss memerlukan lima serangan.",
            "complete": best >= len(WORLDS),
        }

    # ------------------------------------------------------------ practice bots

    def bot_tick(self, bot: Any, now: float) -> None:
        if self.stage != "play" or self.paused:
            return
        seat = self.seats.get(bot.id)
        if seat is None or now < seat.bot_at:
            return
        seat.bot_at = now + self.rng.uniform(0.9, 2.2)
        if seat.step == "select":
            self.choose_hero(seat, self.rng.choice(HEROES))
        elif seat.step in CINEMATIC or seat.step == "result":
            self.act_next(bot)
        elif seat.step == "question" and seat.pres is not None:
            if seat.extra["elements"]:
                self.choose_element(seat, self.rng.choice(ELEMENTS))
            self.act_answer(bot, seat.pres.sample_answer(self.rng.random() < bot.skill, self.rng))
        elif seat.step == "fallen":
            self.retry(bot, seat)
