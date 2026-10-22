"""Sepakan Penalti: Pasukan Harimau against Pasukan Penyu, one penalty each for every question.

Everyone answers the same question. A team's kick goes in when its share of right answers is at least
the other team's; a lower share is saved by the keeper or hits the post, and a team with no right
answers at all misses. Shares rather than head counts, so a smaller team is not behind from the
start. A draw on goals goes to the team with more right answers over the match.

Every child still earns points of their own (right and fast), which decide the podium beside the
team result.
"""

from __future__ import annotations

from typing import Any

from .base import SyncMode, dense_ranks
from .teamplay import TEAMS, TeamPlay, rival, team_name

AIMS = ("kiri", "tengah", "kanan")


class PenaltyMode(TeamPlay, SyncMode):
    key = "penalti"
    title = "Sepakan Penalti"
    tagline = "Pasukan Harimau lawan Pasukan Penyu. Jawapan betul pasukan menjadi sepakan ke gawang."
    how = "Setiap soalan, kedua-dua pasukan menyepak satu penalti. Pasukan yang lebih ramai menjawab betul (ikut peratus ahli) menjaringkan gol; jika sama, kedua-duanya gol."
    style = "Pasukan"
    world = "stadium"
    look = "3d"
    reveal_seconds = 7.0

    def setup(self) -> None:
        self.split_into_teams()
        self.goals = {team: 0 for team, _ in TEAMS}
        self.rights = {team: 0 for team, _ in TEAMS}
        self.rounds: list[dict[str, Any]] = []

    def show_standings(self) -> bool:
        return False  # the scoreboard is always on screen

    def add_player(self, player: Any) -> None:
        self.join_smaller_team(player)

    def on_reveal(self) -> None:
        shares: dict[str, float] = {}
        for team, _ in TEAMS:
            members = [p for p in self.online() if p.team == team]
            right = sum(1 for p in members if (r := self.answers.get(p.id)) is not None and r.outcome.correct)
            self.rights[team] += right
            shares[team] = right / len(members) if members else 0.0

        order = [team for team, _ in TEAMS]
        if len(self.rounds) % 2:
            order.reverse()  # the teams take turns to kick first, as in a real shootout
        kicks = []
        for team in order:
            kicks.append(self.kick(team, shares[team], shares[rival(team)]))
        self.rounds.append({"kicks": kicks})

        scorers = [team_name(k["team"]) for k in kicks if k["result"] == "gol"]
        if len(scorers) == 2:
            self.room.feed("Dua-dua pasukan menjaringkan gol!", "goal")
        elif scorers:
            self.room.feed(f"Gol untuk {scorers[0]}!", "goal")

    def kick(self, team: str, mine: float, theirs: float) -> dict[str, Any]:
        """Where the ball goes and where the keeper dives, decided here so every screen shows the
        same kick."""
        if mine > 0 and mine >= theirs:
            result = "gol"
            aim = self.rng.choice(AIMS)
            dive = self.rng.choice([a for a in AIMS if a != aim])
            self.goals[team] += 1
        elif mine > 0:
            result = self.rng.choice(("selamat", "selamat", "tiang"))
            aim = self.rng.choice(("kiri", "kanan") if result == "tiang" else AIMS)
            dive = aim if result == "selamat" else self.rng.choice(AIMS)
        else:
            result = self.rng.choice(("selamat", "luar"))
            aim = self.rng.choice(AIMS)
            dive = aim if result == "selamat" else self.rng.choice(AIMS)
        return {"team": team, "share": round(mine, 2), "result": result, "aim": aim, "dive": dive}

    def match(self) -> dict[str, Any]:
        return {
            "teams": [
                {"key": team, "name": name, "goals": self.goals[team], "players": len(self.members(team))}
                for team, name in TEAMS
            ],
            "rounds": self.rounds,
        }

    def player_view(self, player: Any) -> dict[str, Any]:
        return {**self.question_block(player), "match": {**self.match(), "myTeam": player.team}}

    def host_view(self) -> dict[str, Any]:
        return {**super().host_view(), "match": self.match()}

    def results(self) -> dict[str, Any]:
        teams = sorted(
            (
                {"key": team, "name": name, "score": self.goals[team], "players": len(self.members(team))}
                for team, name in TEAMS
            ),
            key=lambda t: (-t["score"], -self.rights[t["key"]]),
        )
        first, second = teams
        note = None
        if first["score"] != second["score"]:
            winner: str | None = first["key"]
        elif self.rights[first["key"]] != self.rights[second["key"]]:
            winner = first["key"]
            note = f"Seri {first['score']}-{second['score']}; menang atas jumlah jawapan betul."
        else:
            winner = None
        players = sorted(self.players(), key=lambda p: (-p.score, p.joined_at))
        ranks = dense_ranks([(p.id, p.score) for p in players])
        return {
            "kind": "teams",
            "teams": teams,
            "teamUnit": "gol",
            "winner": winner,
            "note": note,
            "players": [{"id": p.id, "score": p.score, "team": p.team, "rank": ranks[p.id]} for p in players],
        }
