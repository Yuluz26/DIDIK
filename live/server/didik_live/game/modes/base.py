"""What every game shares.

Two shapes cover all the games:

- `SyncMode`: everyone answers the same question at the same time; the server opens it, closes it
  when time is up (or everyone has answered), shows the answer, and moves on.
- `SelfPacedMode`: each child gets their own stream of questions for a few minutes; a right
  answer earns something to spend in the game world (a shovel, water, a flag).

A game only decides what answers *do*. Checking, timing, pausing, streaks and the practice bots
live here, so every game is fair in the same way.

A running game is saved with its room every few seconds (see `save`), so restarting the server does
not end it: the room comes back with the game where it was, paused until the children are back.
"""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from ...questions import Outcome, Presentation, present
from ..settings import TIMING_SCALE

if TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


def now_ms() -> int:
    return int(time.time() * 1000)


def dense_ranks(scores: list[tuple[str, float]]) -> dict[str, int]:
    """1, 2, 2, 4: players with the same score share a place."""
    ranks: dict[str, int] = {}
    previous = None
    for position, (pid, score) in enumerate(scores, 1):
        if score != previous:
            rank = position
            previous = score
        ranks[pid] = rank
    return ranks


class BaseMode:
    key: ClassVar[str] = ""
    title: ClassVar[str] = ""
    tagline: ClassVar[str] = ""
    how: ClassVar[str] = ""
    style: ClassVar[str] = ""
    pace: ClassVar[str] = "sync"
    world: ClassVar[str] = ""
    # Presentation metadata retained for API compatibility; all supported modes are 2D.
    look: ClassVar[str] = "2d"
    # What a score counts, shown beside every number (mata, m, syiling, petak...).
    unit: ClassVar[str] = "mata"
    min_questions: ClassVar[int] = 1
    needs: ClassVar[str] = ""
    intro_seconds: ClassVar[float] = 4.0
    # The game's own state, saved with the room: names of attributes that hold plain JSON (text keys,
    # lists, numbers, text, None). Everything a game sets up in `setup` belongs here, except what can
    # start afresh after a restart (live joystick input, cooldowns of a second or two).
    saved: ClassVar[tuple[str, ...]] = ()

    @classmethod
    def accepts(cls, question: Any) -> bool:
        return True

    @classmethod
    def unplayable_reason(cls, questions: list[Any]) -> str | None:
        count = sum(1 for q in questions if cls.accepts(q))
        if count >= cls.min_questions:
            return None
        kind = f" {cls.needs}" if cls.needs else ""
        return f"Perlukan sekurang-kurangnya {cls.min_questions} soalan{kind}."

    @classmethod
    def describe(cls, questions: list[Any] | None = None) -> dict[str, Any]:
        info: dict[str, Any] = {
            "key": cls.key,
            "title": cls.title,
            "tagline": cls.tagline,
            "how": cls.how,
            "style": cls.style,
            "pace": cls.pace,
            "world": cls.world,
            "look": cls.look,
            "unit": cls.unit,
            "needs": cls.needs,
        }
        if questions is not None:
            info["eligible"] = sum(1 for q in questions if cls.accepts(q))
            info["reason"] = cls.unplayable_reason(questions)
        return info

    def __init__(self, room: Room) -> None:
        # set by the room around a flush, so what all views share is made once (see `shared`)
        self.view_memo: dict[Any, Any] | None = None
        self.room = room
        self.settings = room.settings
        self.rng = random.Random()
        self.questions = [q for q in room.questions if self.accepts(q)]
        if self.settings.shuffle:
            self.rng.shuffle(self.questions)
        self.stage = "intro"
        self.deadline = 0.0
        self.deadline_epoch = 0
        self.paused_left: float | None = None
        # Set by `load`: the time the saved stage still had, used by the first wait after a restart.
        self.carry_over: float | None = None
        self.finished = False
        self._skip = False

    # ------------------------------------------------------------ lifecycle hooks

    def setup(self) -> None:
        """Called once when the host presses Mula, before `run`."""

    async def run(self) -> None:
        raise NotImplementedError

    def add_player(self, player: Player) -> None:
        """A child who joins after the start (late join or approved from the waiting room)."""

    def remove_player(self, player: Player) -> None:
        """A child removed by the host."""

    def handle(self, player: Player, kind: str, data: dict[str, Any]) -> None:
        if kind == "answer":
            self.act_answer(player, data.get("a"))

    def act_answer(self, player: Player, answer: Any) -> None:
        raise NotImplementedError

    def bot_tick(self, bot: Player, now: float) -> None:
        """Called a few times a second for every practice bot."""

    # ------------------------------------------------------------ time

    def scaled(self, seconds: float) -> int:
        return max(3, round(seconds * TIMING_SCALE[self.settings.timing]))

    @property
    def paused(self) -> bool:
        return self.paused_left is not None

    def _set_deadline(self, seconds: float) -> None:
        self.deadline = time.monotonic() + seconds
        self.deadline_epoch = now_ms() + int(seconds * 1000)

    def pause(self) -> None:
        if not self.paused and not self.finished:
            self.paused_left = max(0.0, self.deadline - time.monotonic())
            self.room.mark_dirty()

    def resume(self) -> None:
        if self.paused:
            self._set_deadline(self.paused_left or 0.0)
            self.paused_left = None
            self.room.mark_dirty()

    def skip(self) -> None:
        self._skip = True

    async def wait(self, seconds: float, done: Any = None) -> None:
        """Waits `seconds` of unpaused time, or until the host skips, or until `done()` is true.
        A stage that starts while the game is paused keeps its whole time for after the pause."""
        if self.carry_over is not None:
            seconds, self.carry_over = self.carry_over, None
        if self.paused:
            self.paused_left = seconds
        self._set_deadline(seconds)
        self._skip = False
        self.room.mark_dirty()
        while True:
            if self._skip:
                self._skip = False
                return
            if self.paused:
                await asyncio.sleep(0.1)
                continue
            if done is not None and done():
                return
            if time.monotonic() >= self.deadline:
                return
            await asyncio.sleep(0.05)

    def clock(self) -> dict[str, Any]:
        if self.paused:
            return {"paused": True, "left": int((self.paused_left or 0) * 1000)}
        return {"paused": False, "deadline": self.deadline_epoch}

    def time_left(self) -> float:
        if self.paused:
            return self.paused_left or 0.0
        return max(0.0, self.deadline - time.monotonic())

    # ------------------------------------------------------------ people

    def players(self) -> list[Player]:
        return [p for p in self.room.players.values() if p.approved]

    def online(self) -> list[Player]:
        return [p for p in self.players() if p.connected]

    def name(self, player_id: str) -> str:
        player = self.room.players.get(player_id)
        return player.nickname if player else "Seseorang"

    # ------------------------------------------------------------ saving

    def save(self) -> dict[str, Any]:
        """Everything needed to carry on after a restart, as plain JSON. Questions are kept as their
        places in the room's quiz, so the saved game shows them in the same order."""
        place = {id(q): i for i, q in enumerate(self.room.questions)}
        return {
            "questions": [place[id(q)] for q in self.questions],
            "stage": self.stage,
            "left": round(self.time_left(), 2),
            "paused": self.paused,
            "own": {name: getattr(self, name) for name in self.saved},
        }

    def load(self, state: dict[str, Any]) -> None:
        """The other half of `save`, used instead of `setup`. The game comes back paused with the
        time it had left; the room resumes it when the children are back."""
        self.questions = [self.room.questions[i] for i in state["questions"]]
        self.stage = state["stage"]
        self.paused_left = self.carry_over = float(state["left"])
        self._set_deadline(self.paused_left)
        for name in self.saved:
            setattr(self, name, state["own"][name])

    def save_pres(self, pres: Presentation | None) -> dict[str, Any] | None:
        if pres is None:
            return None
        place = next(i for i, q in enumerate(self.room.questions) if q is pres.question)
        return {"q": place, "public": pres.public, "tokens": pres.token_to_id}

    def load_pres(self, data: dict[str, Any] | None) -> Presentation | None:
        if data is None:
            return None
        tokens = {str(k): str(v) for k, v in data["tokens"].items()}
        return Presentation(
            question=self.room.questions[data["q"]],
            public=data["public"],
            token_to_id=tokens,
            id_to_token={v: k for k, v in tokens.items()},
        )

    # ------------------------------------------------------------ results

    def leaders(self, limit: int = 10) -> list[dict[str, Any]]:
        return self.shared(("leaders", limit), lambda: self._leaders(limit))

    def _leaders(self, limit: int) -> list[dict[str, Any]]:
        players = sorted(self.players(), key=lambda p: (-p.score, p.joined_at))
        ranks = dense_ranks([(p.id, p.score) for p in players])
        return [{"id": p.id, "score": p.score, "rank": ranks[p.id]} for p in players[:limit]]

    def rank_of(self, player: Player) -> int:
        ranks = self.shared(
            "ranks", lambda: dense_ranks([(p.id, p.score) for p in sorted(self.players(), key=lambda p: (-p.score, p.joined_at))])
        )
        return ranks.get(player.id, len(ranks) + 1)

    def shared(self, key: Any, make: Callable[[], Any]) -> Any:
        """What every child's view has in common (the ranking, the shared world), made once per flush
        of the room instead of once per child. Outside a flush it is simply made."""
        memo = self.view_memo
        if memo is None:
            return make()
        if key not in memo:
            memo[key] = make()
        return memo[key]

    def results(self) -> dict[str, Any]:
        players = sorted(self.players(), key=lambda p: (-p.score, p.joined_at))
        ranks = dense_ranks([(p.id, p.score) for p in players])
        return {"kind": "solo", "players": [{"id": p.id, "score": p.score, "rank": ranks[p.id]} for p in players]}

    # ------------------------------------------------------------ views

    def player_view(self, player: Player) -> dict[str, Any]:
        raise NotImplementedError

    def host_view(self) -> dict[str, Any]:
        raise NotImplementedError


# ================================================================ everyone together


@dataclass
class Answered:
    outcome: Outcome
    elapsed: float
    answer: Any


class SyncMode(BaseMode):
    pace = "sync"
    reveal_seconds: ClassVar[float] = 5.0
    standings_seconds: ClassVar[float] = 4.0

    def __init__(self, room: Room) -> None:
        super().__init__(room)
        if self.settings.question_limit:
            self.questions = self.questions[: self.settings.question_limit]
        self.index = -1
        self.pres: Presentation | None = None
        self.answers: dict[str, Answered] = {}
        self.streaks: dict[str, int] = {}
        self.gained: dict[str, int] = {}
        self._bot_plan: dict[str, float] = {}

    @property
    def total(self) -> int:
        return len(self.questions)

    async def run(self) -> None:
        # Written as steps from the current stage, so a game restored after a restart carries on
        # from the stage it was saved in (a restored clock starts paused at the time it had left).
        if self.stage == "intro":
            await self.wait(self.intro_seconds)
            self.open_question(0)
        while True:
            if self.stage == "question":
                await self.wait(self.limit, done=self.all_answered)
                self.close_question()
            if self.stage == "reveal":
                await self.wait(self.reveal_seconds)
                if self.standings_seconds and self.index < self.total - 1 and self.show_standings():
                    self.stage = "standings"
            if self.stage == "standings":
                await self.wait(self.standings_seconds)
            if self.index >= self.total - 1:
                break
            self.open_question(self.index + 1)
        self.room.finish_game()

    @property
    def limit(self) -> float:
        return float(self.pres.public["timeLimit"]) if self.pres else 20.0

    def open_question(self, index: int) -> None:
        self.index = index
        question = self.questions[index]
        self.pres = present(question, self.rng, self.scaled(question.time_limit))
        self.answers = {}
        self.gained = {}
        self._bot_plan = {}
        self.stage = "question"
        self.on_question()

    def close_question(self) -> None:
        self.stage = "reveal"
        self.score_question()
        self.on_reveal()
        self.room.mark_dirty()

    def elapsed(self) -> float:
        """How much of the question's own clock has run: pauses and restarts do not count against a
        child's speed."""
        return max(0.0, self.limit - self.time_left())

    def show_standings(self) -> bool:
        return True

    def all_answered(self) -> bool:
        online = self.online()
        return bool(online) and all(p.id in self.answers for p in online)

    def act_answer(self, player: Player, answer: Any) -> None:
        if self.stage != "question" or self.pres is None or player.id in self.answers or self.paused:
            return
        outcome = self.pres.check(answer)
        if outcome is None:
            player.send({"t": "error", "message": "Jawapan tidak dapat dibaca. Cuba lagi."})
            return
        self.answers[player.id] = Answered(outcome, self.elapsed(), answer)
        self.room.mark_dirty()

    def points_for(self, player: Player, record: Answered | None, limit: float) -> int:
        """Quizizz-style: 500 for a right answer, up to 500 more for speed, a little for a streak."""
        if record is None:
            return 0
        if record.outcome.correct:
            speed = max(0.0, 1 - record.elapsed / max(limit, 1))
            streak_bonus = 50 * min(max(self.streaks.get(player.id, 0) - 1, 0), 4)
            return 500 + round(500 * speed) + streak_bonus
        return round(300 * record.outcome.fraction)

    def score_question(self) -> None:
        limit = self.limit
        for player in self.players():
            record = self.answers.get(player.id)
            if record and record.outcome.correct:
                self.streaks[player.id] = self.streaks.get(player.id, 0) + 1
            else:
                self.streaks[player.id] = 0
            points = self.points_for(player, record, limit)
            player.score += points
            self.gained[player.id] = points

    def on_question(self) -> None:
        """Game hook: a question has just opened."""

    def on_reveal(self) -> None:
        """Game hook: answers are scored; move boats, sink platforms, open tiles."""

    def save(self) -> dict[str, Any]:
        return {
            **super().save(),
            "index": self.index,
            "pres": self.save_pres(self.pres),
            "answers": {
                pid: [r.outcome.correct, r.outcome.fraction, round(r.elapsed, 3), r.answer]
                for pid, r in self.answers.items()
            },
            "streaks": self.streaks,
            "gained": self.gained,
        }

    def load(self, state: dict[str, Any]) -> None:
        super().load(state)
        self.index = int(state["index"])
        self.pres = self.load_pres(state["pres"])
        self.answers = {
            pid: Answered(Outcome(bool(correct), float(fraction)), float(elapsed), answer)
            for pid, (correct, fraction, elapsed, answer) in state["answers"].items()
        }
        self.streaks = dict(state["streaks"])
        self.gained = dict(state["gained"])

    def stats(self) -> dict[str, int]:
        """How many chose each option, for the host's reveal."""
        if self.pres is None:
            return {}
        counts: dict[str, int] = {}
        for record in self.answers.values():
            answer = record.answer
            if self.pres.type == "truefalse":
                key = "true" if answer is True else "false"
                counts[key] = counts.get(key, 0) + 1
            elif self.pres.type == "single":
                counts[str(answer)] = counts.get(str(answer), 0) + 1
            elif self.pres.type == "multiple" and isinstance(answer, list):
                for token in answer:
                    counts[str(token)] = counts.get(str(token), 0) + 1
        return counts

    def question_block(self, player: Player | None) -> dict[str, Any]:
        block: dict[str, Any] = {
            "stage": self.stage,
            "index": self.index,
            "total": self.total,
            "clock": self.clock(),
        }
        if self.stage in ("question", "reveal") and self.pres is not None:
            block["question"] = self.pres.public
        if self.stage == "reveal" and self.pres is not None:
            pres = self.pres
            block["reveal"] = self.shared("reveal", pres.reveal)
            block["stats"] = self.shared("stats", self.stats)
            block["correctCount"] = self.shared("correct", lambda: sum(1 for r in self.answers.values() if r.outcome.correct))
        if self.stage in ("question", "reveal"):
            block["answeredCount"] = len(self.answers)
            block["playerCount"] = self.shared("online", lambda: len(self.online()))
        if player is not None:
            record = self.answers.get(player.id)
            block["answered"] = record is not None
            if record is not None:
                block["myAnswer"] = record.answer
            if self.stage == "reveal":
                block["result"] = {
                    "correct": bool(record and record.outcome.correct),
                    "fraction": record.outcome.fraction if record else 0.0,
                    "missed": record is None,
                    "points": self.gained.get(player.id, 0),
                }
            block["streak"] = self.streaks.get(player.id, 0)
            block["score"] = player.score
            block["rank"] = self.rank_of(player)
        if self.stage == "standings":
            block["standings"] = [
                {**row, "gained": self.gained.get(row["id"], 0)} for row in self.leaders(5)
            ]
        return block

    def player_view(self, player: Player) -> dict[str, Any]:
        return self.question_block(player)

    def host_view(self) -> dict[str, Any]:
        return {**self.question_block(None), "leaders": self.leaders(10)}

    def bot_tick(self, bot: Player, now: float) -> None:
        if self.stage != "question" or self.pres is None or bot.id in self.answers or self.paused:
            return
        plan = self._bot_plan.get(bot.id)
        if plan is None:
            self._bot_plan[bot.id] = now + self.rng.uniform(1.5, max(2.0, self.limit * 0.55))
            return
        if now >= plan:
            self.act_answer(bot, self.pres.sample_answer(self.rng.random() < bot.skill, self.rng))


# ================================================================ everyone at their own pace


@dataclass
class Seat:
    """One child's place in a self-paced game."""

    deck: list[int] = field(default_factory=list)
    pres: Presentation | None = None
    step: str = "question"
    result: dict[str, Any] | None = None
    streak: int = 0
    answered: int = 0
    correct: int = 0
    last_index: int | None = None
    bot_at: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)


class SelfPacedMode(BaseMode):
    pace = "self"

    def __init__(self, room: Room) -> None:
        super().__init__(room)
        self.seats: dict[str, Seat] = {}

    async def run(self) -> None:
        if self.stage == "intro":
            await self.wait(self.intro_seconds)
            self.stage = "play"
            for player in self.players():
                self.seat(player)
            self.on_play()
        await self.wait(self.settings.minutes * 60, done=self.goal_reached)
        self.room.finish_game()

    def save(self) -> dict[str, Any]:
        return {**super().save(), "seats": {pid: self.save_seat(seat) for pid, seat in self.seats.items()}}

    def load(self, state: dict[str, Any]) -> None:
        super().load(state)
        self.seats = {pid: self.load_seat(data) for pid, data in state["seats"].items()}

    def save_seat(self, seat: Seat) -> dict[str, Any]:
        return {
            "deck": seat.deck,
            "pres": self.save_pres(seat.pres),
            "step": seat.step,
            "result": seat.result,
            "streak": seat.streak,
            "answered": seat.answered,
            "correct": seat.correct,
            "last": seat.last_index,
            "extra": seat.extra,
        }

    def load_seat(self, data: dict[str, Any]) -> Seat:
        return Seat(
            deck=list(data["deck"]),
            pres=self.load_pres(data["pres"]),
            step=data["step"],
            result=data["result"],
            streak=data["streak"],
            answered=data["answered"],
            correct=data["correct"],
            last_index=data["last"],
            extra=dict(data["extra"]),
        )

    def on_play(self) -> None:
        """Game hook: the clock has started."""

    def goal_reached(self) -> bool:
        return False

    def add_player(self, player: Player) -> None:
        if self.stage == "play":
            self.seat(player)

    def seat(self, player: Player) -> Seat:
        seat = self.seats.get(player.id)
        if seat is None:
            seat = self.seats[player.id] = Seat()
            self.new_seat(player, seat)
            self.deal(seat)
        return seat

    def new_seat(self, player: Player, seat: Seat) -> None:
        """Game hook: set up a child's own game state (their island, their garden)."""

    def deal(self, seat: Seat) -> None:
        if not seat.deck:
            seat.deck = list(range(len(self.questions)))
            self.rng.shuffle(seat.deck)
            # Never the same question twice in a row when the deck starts over.
            if len(seat.deck) > 1 and seat.deck[-1] == seat.last_index:
                seat.deck[0], seat.deck[-1] = seat.deck[-1], seat.deck[0]
        index = seat.deck.pop()
        seat.last_index = index
        question = self.questions[index]
        seat.pres = present(question, self.rng, self.scaled(question.time_limit))
        seat.step = "question"
        seat.result = None

    def handle(self, player: Player, kind: str, data: dict[str, Any]) -> None:
        if self.stage != "play":
            return
        if kind == "answer":
            self.act_answer(player, data.get("a"))
        elif kind == "next":
            self.act_next(player)
        else:
            self.act(player, self.seats.get(player.id), kind, data)

    def act(self, player: Player, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        """Game hook: actions other than answering (dig, plant, capture...)."""

    def act_answer(self, player: Player, answer: Any) -> None:
        seat = self.seats.get(player.id)
        if seat is None or seat.step != "question" or seat.pres is None or self.paused:
            return
        outcome = seat.pres.check(answer)
        if outcome is None:
            player.send({"t": "error", "message": "Jawapan tidak dapat dibaca. Cuba lagi."})
            return
        seat.answered += 1
        if outcome.correct:
            seat.correct += 1
            seat.streak += 1
        else:
            seat.streak = 0
        seat.step = "result"
        reward = self.reward(player, seat, outcome)
        seat.result = {
            "correct": outcome.correct,
            "fraction": outcome.fraction,
            "reveal": seat.pres.reveal(),
            "answer": answer,
            "reward": reward,
        }
        self.room.mark_dirty()

    def reward(self, player: Player, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        """Game hook: what this answer earns. May move the seat to a game step (e.g. "dig")."""
        return None

    def act_next(self, player: Player) -> None:
        seat = self.seats.get(player.id)
        if seat is not None and seat.step == "result":
            self.deal(seat)
            self.room.mark_dirty()

    def seat_view(self, player: Player) -> dict[str, Any]:
        seat = self.seats.get(player.id)
        if seat is None:
            return {"step": "wait"}
        view: dict[str, Any] = {
            "step": seat.step,
            "streak": seat.streak,
            "answered": seat.answered,
            "correct": seat.correct,
        }
        if seat.step in ("question", "result") and seat.pres is not None:
            view["question"] = seat.pres.public
        if seat.step != "question":
            view["result"] = seat.result
        return view

    def player_view(self, player: Player) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "clock": self.clock(),
            "length": self.settings.minutes * 60,
            "seat": self.seat_view(player),
            "score": player.score,
            "rank": self.rank_of(player),
            "world": self.world_view(player),
        }

    def host_view(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "clock": self.clock(),
            "length": self.settings.minutes * 60,
            "leaders": self.leaders(10),
            "world": self.world_view(None),
        }

    def world_view(self, player: Player | None) -> dict[str, Any]:
        """Game hook: the shared or personal world (island, village, map) for this viewer."""
        return {}

    # ------------------------------------------------------------ practice bots

    def bot_tick(self, bot: Player, now: float) -> None:
        if self.stage != "play" or self.paused:
            return
        seat = self.seats.get(bot.id)
        if seat is None or now < seat.bot_at:
            return
        if seat.step == "question" and seat.pres is not None:
            self.act_answer(bot, seat.pres.sample_answer(self.rng.random() < bot.skill, self.rng))
            seat.bot_at = now + self.rng.uniform(0.8, 1.6)
        elif seat.step == "result":
            self.act_next(bot)
            seat.bot_at = now + self.rng.uniform(1.5, 4.0)
        else:
            self.bot_step(bot, seat)
            seat.bot_at = now + self.rng.uniform(0.7, 1.5)

    def bot_step(self, bot: Player, seat: Seat) -> None:
        """Game hook: what a bot does in a game step (dig a tile, capture a hex...)."""
