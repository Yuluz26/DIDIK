"""Lompat!: our answer to ZEP's OX quiz. Answers are islands in a pond; every child hops their animal
onto one and can change their mind until time runs out. Then the wrong islands sink.

Falling in costs a heart, never the game: a child with no hearts left becomes a fish who keeps
answering, and two right answers in a row put them back on land.
"""

from __future__ import annotations

import time
from typing import Any

from .base import Answered, SyncMode

HEARTS = 3


class JumpMode(SyncMode):
    key = "lompat"
    title = "Lompat!"
    tagline = "Lompat ke pulau jawapan sebelum masa tamat. Pulau yang salah tenggelam!"
    how = "Ketik pulau jawapan. Kamu boleh tukar sebelum masa tamat. Salah = jatuh ke air dan hilang satu hati."
    style = "Serentak"
    world = "kolam"
    needs = "Betul/Salah atau pilihan 2 hingga 4"
    min_questions = 3
    standings_seconds = 0.0
    saved = ("hearts", "fish_run", "picks", "fell", "revived")

    @classmethod
    def accepts(cls, question: Any) -> bool:
        return question.type == "truefalse" or (question.type == "single" and 2 <= len(question.choices) <= 4)

    def setup(self) -> None:
        self.hearts: dict[str, int] = {}
        self.fish_run: dict[str, int] = {}
        self.picks: dict[str, str] = {}
        self.fell: list[str] = []
        self.revived: list[str] = []

    def hearts_of(self, player_id: str) -> int:
        return self.hearts.setdefault(player_id, HEARTS)

    def pads(self) -> list[dict[str, str]]:
        if self.pres is None:
            return []
        if self.pres.type == "truefalse":
            return [{"id": "true", "text": "Betul"}, {"id": "false", "text": "Salah"}]
        return [{"id": c["id"], "text": c["text"]} for c in self.pres.public["choices"]]

    def on_question(self) -> None:
        self.picks = {}
        self.fell = []
        self.revived = []

    def all_answered(self) -> bool:
        return False  # children may still change islands; act_pick shortens the clock instead

    def handle(self, player: Any, kind: str, data: dict[str, Any]) -> None:
        if kind in ("pick", "answer"):
            self.act_pick(player, str(data.get("pad", data.get("a"))))

    def act_pick(self, player: Any, pad: str) -> None:
        if self.stage != "question" or self.pres is None or self.paused:
            return
        if pad not in {p["id"] for p in self.pads()}:
            return
        answer: Any = (pad == "true") if self.pres.type == "truefalse" else pad
        outcome = self.pres.check(answer)
        if outcome is None:
            return
        self.picks[player.id] = pad
        self.answers[player.id] = Answered(outcome, self.elapsed(), answer)
        online = self.online()
        if online and all(p.id in self.picks for p in online) and self.deadline - time.monotonic() > 3:
            self._set_deadline(3)  # everyone has landed: three more seconds to change their mind
        self.room.mark_dirty()

    def act_answer(self, player: Any, answer: Any) -> None:
        self.act_pick(player, "true" if answer is True else "false" if answer is False else str(answer))

    def points_for(self, player: Any, record: Answered | None, limit: float) -> int:
        if record is None or not record.outcome.correct:
            return 0
        fish = self.hearts_of(player.id) == 0
        streak = min(max(self.streaks.get(player.id, 0) - 1, 0), 4) * 20
        return (50 if fish else 100) + streak

    def on_reveal(self) -> None:
        for player in self.players():
            record = self.answers.get(player.id)
            right = bool(record and record.outcome.correct)
            hearts = self.hearts_of(player.id)
            if hearts == 0:
                self.fish_run[player.id] = self.fish_run.get(player.id, 0) + 1 if right else 0
                if self.fish_run[player.id] >= 2:
                    self.hearts[player.id] = 1
                    self.fish_run[player.id] = 0
                    self.revived.append(player.id)
                    self.room.feed(f"{player.nickname} naik semula ke darat!", "revive", player)
            elif not right:
                self.hearts[player.id] = hearts - 1
                self.fell.append(player.id)
                if hearts - 1 == 0:
                    self.room.feed(f"{player.nickname} jadi ikan. Jawab betul dua kali untuk naik semula!", "fish", player)
        survivors = sum(1 for p in self.players() if self.hearts_of(p.id) > 0)
        self.room.fx({"kind": "sink", "fell": self.fell, "survivors": survivors})

    def pond(self) -> dict[str, Any]:
        reveal = self.stage == "reveal" and self.pres is not None
        correct: list[str] = []
        if reveal:
            truth = self.pres.reveal()["correct"]
            correct = ["true" if truth else "false"] if self.pres.type == "truefalse" else list(truth)
        return {
            "pads": self.pads(),
            "picks": self.picks if self.stage in ("question", "reveal") else {},
            "hearts": {p.id: self.hearts_of(p.id) for p in self.players()},
            "correctPads": correct,
            "fell": self.fell if reveal else [],
            "revived": self.revived if reveal else [],
        }

    def player_view(self, player: Any) -> dict[str, Any]:
        return {**self.question_block(player), "pond": self.shared("pond", self.pond), "myPick": self.picks.get(player.id)}

    def host_view(self) -> dict[str, Any]:
        return {**super().host_view(), "pond": self.pond()}

    def results(self) -> dict[str, Any]:
        results = super().results()
        for row in results["players"]:
            row["hearts"] = self.hearts_of(row["id"])
        return results

    def bot_tick(self, bot: Any, now: float) -> None:
        if self.stage != "question" or self.pres is None or self.paused:
            return
        plan = self._bot_plan.get(bot.id)
        if plan is None:
            self._bot_plan[bot.id] = now + self.rng.uniform(1.0, 4.0)
            return
        if now >= plan and bot.id not in self.picks:
            answer = self.pres.sample_answer(self.rng.random() < bot.skill, self.rng)
            self.act_answer(bot, answer)
            # Some bots change their mind once, like children do.
            if self.rng.random() < 0.25:
                self._bot_plan[bot.id] = now + self.rng.uniform(1.0, 2.5)
                self._bot_plan[f"{bot.id}:switch"] = 1.0
        elif now >= plan and self._bot_plan.pop(f"{bot.id}:switch", None):
            others = [p["id"] for p in self.pads() if p["id"] != self.picks.get(bot.id)]
            if others:
                self.act_pick(bot, self.rng.choice(others))
