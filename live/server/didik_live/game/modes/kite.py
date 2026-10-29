"""Lumba Wau: everyone answers the same question; right and fast lifts your wau highest.

The same race as Lumba Sampan, upwards: a wrong answer still lifts a little, so no wau falls out of
the sky, and once or twice a game a strong wind lifts every wau together.
"""

from __future__ import annotations

from .race import RaceMode


class KiteMode(RaceMode):
    key = "wau"
    title = "Lumba Wau"
    tagline = "Jawab betul dan pantas, wau kamu terbang paling tinggi melepasi awan."
    how = "Semua jawab soalan yang sama. Betul dan laju = wau naik tinggi. Salah pun tetap naik sikit. Sesekali angin kencang menaikkan semua wau!"
    style = "Serentak"
    world = "langit"
    unit = "m"

    def on_reveal(self) -> None:
        if self.index in self.rapids_at:
            self.rapids_now = True
            for player in self.players():
                player.score += 25
                self.gained[player.id] = self.gained.get(player.id, 0) + 25
            self.room.feed("Angin kencang! Semua wau naik lebih tinggi.", "rapids")
            self.room.fx({"kind": "rapids"})
