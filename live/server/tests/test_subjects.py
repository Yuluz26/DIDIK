"""The subject games (Sains, Sejarah, Pendidikan Islam) and the diagrams: the server's lists, the web's lists,
the pictures and the sample quizzes stay the same set, and a game only plays the types it knows."""

from __future__ import annotations

import random
import re
from collections import Counter
from pathlib import Path

import pytest
from pydantic import ValidationError

from didik_live.diagrams import DIAGRAMS
from didik_live.games import GAMES
from didik_live.questions import QuestionOne, parse_questions, present
from didik_live.samples_subjects import SUBJECT_SAMPLES

WEB = Path(__file__).resolve().parents[2] / "web"


def one(raw: dict):
    return QuestionOne.validate_python(raw)


def web_games() -> dict[str, tuple[str, set[str]]]:
    source = (WEB / "src" / "lib" / "subjects" / "games.ts").read_text(encoding="utf-8")
    rows = re.findall(r"G\('([a-z]+)', '[^']*', '([a-z]+)', \[([^\]]*)\]", source)
    return {key: (subject, set(re.findall(r"'([a-z]+)'", types))) for key, subject, types in rows}


def test_web_and_server_know_the_same_games_and_what_they_play() -> None:
    web = web_games()
    assert set(web) == set(GAMES)
    for key, game in GAMES.items():
        assert web[key] == (game["subject"], set(game["types"])), key


def test_each_subject_has_twelve_games_and_each_has_its_component() -> None:
    per_subject = Counter(game["subject"] for game in GAMES.values())
    assert per_subject == {"sains": 12, "sejarah": 12, "islam": 12}
    folder = WEB / "src" / "lib" / "subjects"
    names = {p.stem.lower() for subject in per_subject for p in (folder / subject).glob("*.svelte")}
    assert set(GAMES) <= names


def test_web_and_server_know_the_same_diagrams_and_each_has_its_picture_and_credit() -> None:
    source = (WEB / "src" / "lib" / "diagrams.ts").read_text(encoding="utf-8")
    assert set(re.findall(r"key: '(rajah-[a-z-]+)'", source)) == DIAGRAMS
    folder = WEB / "static" / "rajah"
    assert {p.stem for p in folder.glob("*.webp")} == DIAGRAMS
    credits = (folder / "CREDITS.txt").read_text(encoding="utf-8")
    for key in DIAGRAMS:
        assert key in credits, key


def test_a_game_only_plays_the_types_it_knows() -> None:
    plain = {"type": "single", "prompt": "?", "choices": [{"text": "a", "correct": True}, {"text": "b"}]}
    assert one({**plain, "game": "ramuan"}).game == "ramuan"
    with pytest.raises(ValidationError):
        one({**plain, "game": "orbit"})  # orbit plays order questions
    with pytest.raises(ValidationError):
        one({**plain, "game": "tiada"})


def test_a_diagram_can_be_a_questions_picture_and_unknown_pictures_are_refused() -> None:
    plain = {"type": "truefalse", "prompt": "?", "answer": True}
    assert one({**plain, "picture": "rajah-kaabah"}).picture == "rajah-kaabah"
    with pytest.raises(ValidationError):
        one({**plain, "picture": "rajah-tiada"})


def test_diagram_labels_are_checked_place_by_place() -> None:
    raw = {
        "type": "diagram",
        "prompt": "Labelkan.",
        "diagram": "rajah-organ",
        "spots": [{"x": 53, "y": 29, "label": "Jantung"}, {"x": 27, "y": 33, "label": "Paru-paru"}, {"x": 74, "y": 45, "label": "Perut"}],
    }
    pres = present(one(raw), random.Random(2))
    right = pres.reveal()["correct"]
    assert pres.check(right).correct
    spots = list(right)
    swapped = {**right, spots[0]: right[spots[1]], spots[1]: right[spots[0]]}
    assert not pres.check(swapped).correct
    # places too close together cannot be told apart on a phone
    with pytest.raises(ValidationError):
        one({**raw, "spots": [{"x": 50, "y": 50, "label": "A"}, {"x": 51, "y": 51, "label": "B"}]})
    with pytest.raises(ValidationError):
        one({**raw, "diagram": "rajah-tiada"})


def test_each_subject_sample_plays_all_twelve_of_its_games_with_explanations() -> None:
    by_subject: dict[str, list[str]] = {}
    for sample in SUBJECT_SAMPLES:
        questions = parse_questions(sample["questions"])
        games = [q.game for q in questions]
        subjects = {GAMES[g]["subject"] for g in games}
        assert len(subjects) == 1 and sorted(games) == sorted(k for k, g in GAMES.items() if g["subject"] in subjects), sample["title"]
        by_subject.setdefault(subjects.pop(), []).append(sample["title"])
        for q in questions:
            assert q.explain.strip(), (sample["title"], q.prompt)
        # "not every question needs a diagram, but some do": every quiz has a few pictures or diagrams
        pictured = [q for q in questions if q.picture or q.type == "diagram"]
        assert len(pictured) >= 2, sample["title"]
    # Tahap 1 (Tahun 1-3), Tahap 2 (Tahun 4-6) and Menengah (Tingkatan 1-5) for each subject
    assert {k: len(v) for k, v in by_subject.items()} == {"sains": 3, "sejarah": 3, "islam": 3}
