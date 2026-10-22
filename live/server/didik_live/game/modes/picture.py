"""Teka Gambar: a hidden picture sits under sixteen tiles. After each question, tiles open (more
when more children got it right). Anyone can type a guess at any time; guessing while most tiles are
still closed earns the most.

The picture is served by a random per-round token and its name stays on the server until the
picture is finished, so peeking at the browser gives nothing away.
"""

from __future__ import annotations

import secrets
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

from ... import text as textutil
from .base import SyncMode

TILES = 16
PICTURE_DIR = Path(__file__).resolve().parents[2] / "pictures"

PICTURES = [
    ("kucing", "Kucing", ["kucing", "kucing comel", "cat"]),
    ("ikan", "Ikan", ["ikan", "fish"]),
    ("rumah", "Rumah", ["rumah", "rumah kampung", "house"]),
    ("perahu", "Perahu", ["perahu", "bot", "sampan", "kapal", "boat"]),
    ("wau", "Wau", ["wau", "layang-layang", "layang layang", "wau bulan"]),
    ("gajah", "Gajah", ["gajah", "elephant"]),
    ("payung", "Payung", ["payung", "umbrella"]),
    ("roket", "Roket", ["roket", "rocket"]),
]


@lru_cache(maxsize=None)
def picture_svg(key: str) -> bytes:
    return (PICTURE_DIR / f"{key}.svg").read_bytes()


class PictureMode(SyncMode):
    key = "teka"
    title = "Teka Gambar"
    tagline = "Setiap jawapan betul membuka petak gambar rahsia. Siapa paling cepat meneka?"
    how = "Jawab soalan untuk membuka petak. Taip nama gambar bila kamu rasa tahu. Lebih awal meneka, lebih banyak mata!"
    style = "Serentak"
    world = "galeri"
    min_questions = 4
    standings_seconds = 0.0
    saved = ("deck", "picture_index", "solved", "token", "order", "shown", "guessed", "done")

    def __init__(self, room: Any) -> None:
        super().__init__(room)
        self.cooldown: dict[str, float] = {}

    def setup(self) -> None:
        self.deck = [list(picture) for picture in PICTURES]
        self.rng.shuffle(self.deck)
        self.picture_index = -1
        self.solved: list[str] = []
        self.next_picture()

    def next_picture(self) -> None:
        self.picture_index = (self.picture_index + 1) % len(self.deck)
        self.token = secrets.token_urlsafe(12)
        self.order = list(range(TILES))
        self.rng.shuffle(self.order)
        self.shown: list[int] = []
        self.guessed: dict[str, int] = {}
        self.cooldown: dict[str, float] = {}
        self.done = False

    @property
    def current(self) -> list[Any]:
        """[key, name, accepted guesses]"""
        return self.deck[self.picture_index]

    def picture_bytes(self, token: str) -> bytes | None:
        return picture_svg(self.current[0]) if secrets.compare_digest(token, self.token) else None

    def on_question(self) -> None:
        if self.done:
            self.next_picture()

    def on_reveal(self) -> None:
        if self.done:
            return
        online = self.online()
        right = sum(1 for r in self.answers.values() if r.outcome.correct)
        share = right / len(online) if online else 0
        count = 1 + round(3 * share) if right else 1
        closed = [t for t in self.order if t not in self.shown]
        newly = closed[:count]
        self.shown.extend(newly)
        everyone_guessed = bool(online) and all(p.id in self.guessed for p in online)
        if len(self.shown) >= TILES or everyone_guessed:
            self.finish_picture()
        else:
            self.room.fx({"kind": "tiles", "opened": newly})

    def finish_picture(self) -> None:
        self.shown = list(range(TILES))
        self.done = True
        self.solved.append(self.current[1])
        self.room.fx({"kind": "picture", "name": self.current[1]})

    def handle(self, player: Any, kind: str, data: dict[str, Any]) -> None:
        if kind == "guess":
            self.act_guess(player, str(data.get("text") or "")[:40])
        else:
            super().handle(player, kind, data)

    def act_guess(self, player: Any, guess: str) -> None:
        if self.done or self.stage not in ("question", "reveal") or player.id in self.guessed or not guess.strip():
            return
        now = time.monotonic()
        if now < self.cooldown.get(player.id, 0):
            return
        if textutil.matches(guess, self.current[2]):
            hidden = TILES - len(self.shown)
            bonus = 100 + 60 * hidden
            player.score += bonus
            self.guessed[player.id] = bonus
            self.room.fx({"kind": "guess-right", "bonus": bonus, "name": self.current[1]}, to=player, hosts=False)
            self.room.fx({"kind": "guessed", "player": player.id})
            self.room.feed(f"{player.nickname} sudah meneka gambar!", "guess", player)
        else:
            self.cooldown[player.id] = now + 2.5
            self.room.fx({"kind": "guess-wrong"}, to=player, hosts=False)
        self.room.mark_dirty()

    def frame(self, player: Any | None) -> dict[str, Any]:
        view: dict[str, Any] = {
            "url": f"/api/rooms/{self.room.code}/picture/{self.token}",
            "tiles": TILES,
            "opened": sorted(self.shown),
            "done": self.done,
            "number": len(self.solved) + (0 if self.done else 1),
            "guessedCount": len(self.guessed),
            "guessers": list(self.guessed),
        }
        if self.done:
            view["name"] = self.current[1]
        if player is not None:
            view["guessed"] = player.id in self.guessed
            if player.id in self.guessed:
                view["name"] = self.current[1]
                view["bonus"] = self.guessed[player.id]
        return view

    def player_view(self, player: Any) -> dict[str, Any]:
        return {**self.question_block(player), "picture": self.frame(player)}

    def host_view(self) -> dict[str, Any]:
        return {**super().host_view(), "picture": self.frame(None)}

    def bot_tick(self, bot: Any, now: float) -> None:
        super().bot_tick(bot, now)
        if self.done or bot.id in self.guessed or self.stage not in ("question", "reveal"):
            return
        # Bots guess once enough of the picture shows, and sometimes guess wrong first.
        chance = (len(self.shown) / TILES) * bot.skill * 0.08
        if self.rng.random() < chance:
            self.act_guess(bot, self.current[2][0] if self.rng.random() < 0.8 else "entah")
