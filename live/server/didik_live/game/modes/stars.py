"""Kejar Bintang: two teams, Harimau and Penyu, catch falling stars. Every right answer catches a star
for your team (three in a row, two); every ten stars light up a constellation in the team's half of
the night sky. The team with more stars when time runs out wins; every child adds to it.
"""

from __future__ import annotations

from typing import Any

from ...questions import Outcome
from .base import Seat, SelfPacedMode, dense_ranks
from .teamplay import TEAMS, TeamPlay, team_name

PER_CONSTELLATION = 10
CONSTELLATIONS = ["Bulan Sabit", "Wau Bulan", "Perahu", "Gasing", "Bunga Raya", "Burung Enggang", "Ketupat", "Keris"]


class StarsMode(TeamPlay, SelfPacedMode):
    key = "bintang"
    title = "Kejar Bintang"
    tagline = "Pasukan Harimau lawan Pasukan Penyu. Tangkap bintang jatuh dan nyalakan buruj di langit!"
    how = "Setiap jawapan betul menangkap bintang untuk pasukan kamu (tiga betul berturut-turut, dua bintang). Setiap sepuluh bintang menyalakan satu buruj. Pasukan dengan bintang paling banyak menang."
    style = "Pasukan"
    world = "malam"
    unit = "bintang"
    saved = ("stars",)

    def setup(self) -> None:
        self.stars: dict[str, int] = {team: 0 for team, _ in TEAMS}
        self.split_into_teams()

    def add_player(self, player: Any) -> None:
        self.join_smaller_team(player)
        super().add_player(player)

    def reward(self, player: Any, seat: Seat, outcome: Outcome) -> dict[str, Any] | None:
        if not outcome.correct or not player.team:
            return {"stars": 0}
        caught = 2 if seat.streak >= 3 else 1
        before = self.stars[player.team] // PER_CONSTELLATION
        self.stars[player.team] += caught
        player.score += caught
        lit = self.stars[player.team] // PER_CONSTELLATION
        if lit > before and lit <= len(CONSTELLATIONS):
            self.room.feed(f"{team_name(player.team)} menyalakan buruj {CONSTELLATIONS[lit - 1]}!", "star", player)
        self.room.fx({"kind": "star", "team": player.team, "by": player.id, "caught": caught})
        return {"stars": caught}

    def tally(self) -> list[dict[str, Any]]:
        return [
            {
                "key": team,
                "name": name,
                "stars": self.stars.get(team, 0),
                "lit": min(len(CONSTELLATIONS), self.stars.get(team, 0) // PER_CONSTELLATION),
                "players": sum(1 for p in self.players() if p.team == team),
            }
            for team, name in TEAMS
        ]

    def world_view(self, player: Any) -> dict[str, Any]:
        view: dict[str, Any] = {"teams": self.shared("tally", self.tally), "constellations": CONSTELLATIONS, "per": PER_CONSTELLATION}
        if player is not None:
            view["myTeam"] = player.team
            view["mine"] = player.score
        return view

    def results(self) -> dict[str, Any]:
        teams = sorted(({"key": t["key"], "name": t["name"], "score": t["stars"], "players": t["players"]} for t in self.tally()), key=lambda t: -t["score"])
        winner = teams[0]["key"] if teams[0]["score"] != teams[1]["score"] else None
        players = sorted(self.players(), key=lambda p: (-p.score, p.joined_at))
        ranks = dense_ranks([(p.id, p.score) for p in players])
        return {
            "kind": "teams",
            "teams": teams,
            "teamUnit": "bintang",
            "winner": winner,
            "players": [{"id": p.id, "score": p.score, "team": p.team, "rank": ranks[p.id]} for p in players],
        }
