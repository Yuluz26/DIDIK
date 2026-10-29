"""Catalogue retirement preserves quizzes and returning players without reviving old handlers."""

import asyncio
import json

import pytest

from didik_live.game.manager import RoomManager
from didik_live.game.modes import MODES
from didik_live.game.player import dumps
from didik_live.game.room import Room

from .conftest import sample_id
from .roomkit import connection, open_room


def test_catalogue_contains_fourteen_2d_games_and_legenda():
    assert set(MODES) == {
        "lumba", "lompat", "harta", "hutan", "pasukan", "kampung", "teka", "kebun",
        "pancing", "wau", "kubu", "keretapi", "pasar", "bintang", "legenda",
    }
    assert all(mode.look == "2d" for mode in MODES.values())


@pytest.mark.parametrize("key", ["litar", "penalti", "lanun", "menara"])
def test_removed_modes_cannot_open_new_rooms(parent, key):
    quiz_id = sample_id(parent, "Haiwan di Malaysia")
    response = parent.post("/api/rooms", json={"quiz_id": quiz_id, "mode": key})
    assert response.status_code == 422


@pytest.mark.parametrize("key", ["litar", "penalti", "lanun", "menara"])
@pytest.mark.parametrize("phase", ["lobby", "playing", "ended"])
def test_retired_saved_modes_keep_the_room_and_rejoin_tokens(key, phase):
    async def scenario():
        original = open_room("lumba")
        child = original.join(connection()[0], {"avatar": "kancil"})
        child.score = 900
        saved = json.loads(dumps(original.save()))
        original.close()
        saved.update(mode=key, phase=phase, game={"obsolete": True}, results={"obsolete": True})
        saved["settings"]["max_players"] = 1  # a solo room of a retired game reopens as a party room

        restored = Room.restore(RoomManager(), saved)
        assert restored.phase == "lobby" and restored.mode is None and restored.results is None
        assert restored.mode_key in MODES and restored.mode_key != "legenda"
        assert restored.settings.max_players == 2
        assert (restored.code, restored.slug, restored.quiz_id) == (saved["code"], saved["slug"], saved["quiz"])
        assert len(restored.questions) == len(original.questions)
        returning = restored.rejoin(connection()[0], child.token)
        assert returning is not None and returning.id == child.id and returning.score == 0
        assert "telah ditamatkan" in restored.base_view()["feed"][-1]["text"]
        restored.close()

    asyncio.run(scenario())
