"""Pasukan Warna: two teams, Harimau and Penyu, claim an island of hexagons. A right answer earns a
flag; a flag claims an empty hexagon next to your team's land, two flags take one from the other team.
The team with more land when time runs out wins; nobody is out at any point.
"""

from __future__ import annotations

from typing import Any

from ...questions import Outcome
from .base import Seat, SelfPacedMode
from .teamplay import TEAMS, TeamPlay, team_name

RADIUS = 3
DIRECTIONS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
BASES = {"harimau": (-RADIUS, 0), "penyu": (RADIUS, 0)}


def cell_key(q: int, r: int) -> str:
    return f"{q},{r}"


class TeamsMode(TeamPlay, SelfPacedMode):
    key = "pasukan"
    title = "Pasukan Warna"
    tagline = "Pasukan Harimau lawan Pasukan Penyu. Tawan petak pulau untuk pasukan kamu!"
    how = "Jawab betul untuk dapat bendera. Satu bendera menawan petak kosong di sebelah kawasan pasukanmu; dua bendera merampas petak lawan."
    style = "Pasukan"
    world = "peta"
    unit = "petak"
    saved = ("cells", "captures")

    def setup(self) -> None:
        self.cells: dict[str, str | None] = {}
        for q in range(-RADIUS, RADIUS + 1):
            for r in range(-RADIUS, RADIUS + 1):
                if abs(q + r) <= RADIUS:
                    self.cells[cell_key(q, r)] = None
        for team, (q, r) in BASES.items():
            self.cells[cell_key(q, r)] = team
        self.captures: dict[str, int] = {}
        self.split_into_teams()

    def add_player(self, player: Any) -> None:
        self.join_smaller_team(player)
        super().add_player(player)

    def new_seat(self, player: Any, seat: Seat) -> None:
        seat.extra.update(flags=0)

    # ------------------------------------------------------------ the map

    def cost(self, key: str, team: str) -> int | None:
        """Flags needed for `team` to take this hexagon, or None when it cannot be taken."""
        owner = self.cells.get(key, "missing")
        if owner == "missing" or owner == team or key in {cell_key(*b) for b in BASES.values()}:
            return None
        q, r = (int(v) for v in key.split(","))
        if not any(self.cells.get(cell_key(q + dq, r + dr)) == team for dq, dr in DIRECTIONS):
            return None
        return 1 if owner is None else 2

    def targets(self, team: str, flags: int) -> list[str]:
        return [key for key in self.cells if (c := self.cost(key, team)) is not None and c <= flags]

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct:
            return {"flags": 0}
        gained = 2 if seat.streak > 0 and seat.streak % 4 == 0 else 1
        seat.extra["flags"] += gained
        if player.team and self.targets(player.team, seat.extra["flags"]):
            seat.step = "capture"
        return {"flags": gained}

    def act(self, player: Any, seat: Seat | None, kind: str, data: dict[str, Any]) -> None:
        if seat is None or not player.team:
            return
        if kind == "keep" and seat.step == "capture":
            seat.step = "result"
            self.room.mark_dirty()
            return
        if kind != "capture" or seat.step != "capture":
            return
        key = str(data.get("cell"))
        cost = self.cost(key, player.team)
        if cost is None or cost > seat.extra["flags"]:
            return
        previous = self.cells[key]
        self.cells[key] = player.team
        seat.extra["flags"] -= cost
        self.captures[player.id] = self.captures.get(player.id, 0) + 1
        player.score = self.captures[player.id]
        if previous is not None:
            self.room.feed(f"{player.nickname} merampas satu petak untuk {team_name(player.team)}!", "steal", player)
        self.room.fx({"kind": "captured", "cell": key, "team": player.team, "player": player.id, "from": previous})
        if not self.targets(player.team, seat.extra["flags"]):
            seat.step = "result"
        self.room.mark_dirty()

    def tally(self) -> list[dict[str, Any]]:
        return [
            {
                "key": team,
                "name": name,
                "cells": sum(1 for owner in self.cells.values() if owner == team),
                "players": sum(1 for p in self.players() if p.team == team),
            }
            for team, name in TEAMS
        ]

    def world_view(self, player: Any) -> dict[str, Any]:
        bases = {cell_key(*b) for b in BASES.values()}
        view: dict[str, Any] = {
            "cells": [
                {"key": key, "q": int(key.split(",")[0]), "r": int(key.split(",")[1]), "owner": owner, "base": key in bases}
                for key, owner in self.cells.items()
            ],
            "teams": self.tally(),
        }
        if player is not None:
            seat = self.seats.get(player.id)
            flags = seat.extra["flags"] if seat else 0
            view["myTeam"] = player.team
            view["flags"] = flags
            view["targets"] = self.targets(player.team, flags) if (seat and player.team and seat.step == "capture") else []
            view["costs"] = {k: self.cost(k, player.team) for k in view["targets"]} if player.team else {}
        return view

    def results(self) -> dict[str, Any]:
        teams = sorted(
            ({"key": t["key"], "name": t["name"], "score": t["cells"], "players": t["players"]} for t in self.tally()),
            key=lambda t: -t["score"],
        )
        winner = teams[0]["key"] if teams[0]["score"] != teams[1]["score"] else None
        players = sorted(self.players(), key=lambda p: (-self.captures.get(p.id, 0), p.joined_at))
        return {
            "kind": "teams",
            "teams": teams,
            "teamUnit": "petak",
            "winner": winner,
            "players": [{"id": p.id, "score": self.captures.get(p.id, 0), "team": p.team, "rank": 1} for p in players],
        }

    def bot_step(self, bot: Any, seat: Seat) -> None:
        if seat.step == "capture" and bot.team:
            options = self.targets(bot.team, seat.extra["flags"])
            if options:
                # Prefer taking from the other team when affordable, like a cheeky child would.
                enemy = [k for k in options if self.cells[k] is not None]
                self.act(bot, seat, "capture", {"cell": self.rng.choice(enemy or options)})
            else:
                self.act(bot, seat, "keep", {})
