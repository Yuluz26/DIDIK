"""Two teams, Harimau and Penyu, shared by every team game (Pasukan Warna, Sepakan Penalti).

Children are dealt into teams at random when the host presses Mula, alternately so the sizes never
differ by more than one, and a child who joins later goes to the smaller team.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..player import Player

TEAMS = [("harimau", "Pasukan Harimau"), ("penyu", "Pasukan Penyu")]


def team_name(team: str) -> str:
    return dict(TEAMS)[team]


def rival(team: str) -> str:
    return TEAMS[1][0] if team == TEAMS[0][0] else TEAMS[0][0]


class TeamPlay:
    """Mixed into a game mode; expects `self.players()` and `self.rng` from `BaseMode`."""

    players: Any
    rng: Any

    def split_into_teams(self) -> None:
        players = self.players()
        self.rng.shuffle(players)
        for index, player in enumerate(players):
            player.team = TEAMS[index % 2][0]

    def join_smaller_team(self, player: Player) -> None:
        sizes = {team: sum(1 for p in self.players() if p.team == team and p.id != player.id) for team, _ in TEAMS}
        player.team = min(sizes, key=lambda team: sizes[team])

    def members(self, team: str) -> list[Player]:
        return [p for p in self.players() if p.team == team]
