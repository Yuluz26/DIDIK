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


# ---------------------------------------------------------------- Kuiz Interaktif in one subject's games


def _single(*choices: str, game: str | None = None) -> dict:
    rows = [{"text": choices[0], "correct": True}] + [{"text": c} for c in choices[1:]]
    return {"type": "single", "prompt": "?", "choices": rows, **({"game": game} if game else {})}


def test_a_subject_deals_its_games_spreading_them_out_and_keeps_games_written_for_it() -> None:
    from didik_live.games import deal_games

    words = one(_single("a", "b", "c"))
    planets = one(_single("Musytari", "Marikh", "Bumi"))
    conductor = one(_single("Kunci besi", "Pemadam", "Kayu"))
    # Teropong only for things in the sky, Litar only for a conductor among insulators
    assert deal_games("sains", [words] * 3) == ["ramuan", "ramuan", "ramuan"]
    assert deal_games("sains", [planets, planets, conductor, conductor]) == ["ramuan", "teropong", "litar", "ramuan"]
    # a question written for one of the subject's games keeps it (if it suits it); one written for another subject does not
    mixed = [one(_single("Kunci besi", "Pemadam", game="litar")), one(_single("a", "b", game="gali")), one({"type": "clock", "prompt": "?", "hour": 3})]
    assert deal_games("sains", mixed) == ["litar", "ramuan", None]  # no Sains game tells the time
    assert deal_games("sejarah", mixed) == ["gali", "gali", None]


def test_games_that_need_their_own_kind_of_content_are_dealt_only_with_it() -> None:
    from didik_live.games import deal_games

    latin = one(_single("Ba", "Ta", "Tsa"))
    arabic = one(_single("ب", "ت", "ث"))
    assert "hijaiyah" not in deal_games("islam", [latin] * 5)
    assert deal_games("islam", [arabic] * 3) == ["kiblat", "kafilah", "hijaiyah"]

    def number(answer: float, unit: str = "") -> object:
        return one({"type": "number", "prompt": "?", "answer": answer, "unit": unit})

    assert deal_games("sains", [number(37, "°C"), number(400, "ml"), number(405, "ml"), number(-5, "")]) == ["alat", "alat", None, None]
    assert deal_games("sejarah", [number(1957), number(12000), number(2.5)]) == ["mesinmasa", None, None]

    prayers = one({"type": "match", "prompt": "?", "pairs": [{"left": "Subuh", "right": "2"}, {"left": "Maghrib", "right": "3"}]})
    words = one({"type": "match", "prompt": "?", "pairs": [{"left": "Besar", "right": "Kecil"}, {"left": "Panas", "right": "Sejuk"}]})
    assert deal_games("islam", [prayers, prayers]) == ["malaikat", "waktu"]
    assert deal_games("islam", [words, words]) == ["malaikat", "malaikat"]

    organ = one({"type": "diagram", "prompt": "?", "diagram": "rajah-organ", "spots": [{"x": 50, "y": 30, "label": "Jantung"}, {"x": 20, "y": 60, "label": "Perut"}]})
    water = one({**organ.model_dump(), "diagram": "rajah-kitaran-air"})
    assert deal_games("sains", [organ, water]) == ["tubuh", None]
    assert deal_games("sejarah", [organ]) == [None]


def test_the_subject_kinds_say_how_much_of_a_quiz_they_play_and_refuse_a_quiz_they_cannot() -> None:
    from didik_live.game.modes import MODES

    sains = MODES["interaktif-sains"]
    quiz = parse_questions(next(s for s in SUBJECT_SAMPLES if s["title"].startswith("Sains Tahap 1"))["questions"])
    info = sains.describe(quiz)
    assert info["family"] == "interaktif" and info["world"] == "interaktif" and info["subject"] == "sains"
    assert info["eligible"] == 12 and info["reason"] is None
    clocks = [one({"type": "clock", "prompt": "?", "hour": h}) for h in (1, 2)]
    assert "Sains" in sains.unplayable_reason(clocks)
    assert MODES["interaktif"].unplayable_reason(clocks) is None


def test_a_subject_room_plays_every_question_it_can_as_the_subjects_games() -> None:
    from .test_modes import answer, run, started

    async def scenario() -> None:
        room, _, _, ((ana, _), _) = await started("interaktif-islam", title="Matematik Ceria")
        mode = room.mode
        expected = mode.dealt()
        assert any(expected) and all(g is None or GAMES[g]["subject"] == "islam" for g in expected)
        seen = []
        for _ in range(mode.total):
            seat = mode.seats[ana.id]
            seen.append(seat.pres.public.get("game"))
            answer(room, ana, True)
            room.handle_player(ana, {"t": "next"})
        assert seen == expected
        room.close()

    run(scenario())



# ---------------------------------------------------------------- what a game may show (the lexicon)


def test_the_web_copy_of_the_lexicon_is_the_servers() -> None:
    from didik_live import lexicon

    assert lexicon.WEB_COPY.read_text(encoding="utf-8") == lexicon.dump(), "run: python -m didik_live.lexicon"


def test_a_game_is_never_shown_for_content_it_would_misrepresent() -> None:
    from didik_live.games import game_for

    def single(*choices: str, game: str) -> object:
        return one(_single(*choices, game=game))

    # no planets on a question about plants, no bulb lit by "the right answer"
    assert game_for(single("Klorofil", "Akar", "Batang", game="teropong")) is None
    assert game_for(single("Musytari", "Marikh", "Bumi", game="teropong")) == "teropong"
    assert game_for(single("Bateri", "Mentol", "Span", game="litar")) is None  # not a question about conductors
    assert game_for(single("Pemadam", "Kunci besi", "Kayu", game="litar")) is None  # right answer is an insulator among a conductor and an insulator
    assert game_for(single("Kunci besi", "Pemadam", "Kayu", game="litar")) == "litar"
    orbit = {"type": "order", "prompt": "?", "game": "orbit", "items": [{"text": t} for t in ("Merkurius", "Venus", "Bumi")]}
    assert game_for(one(orbit)) == "orbit"
    assert game_for(one({**orbit, "items": [{"text": t} for t in ("Bumi", "Venus", "Merkurius")]})) is None  # not their order from the Sun
    assert game_for(one({**orbit, "items": [{"text": t} for t in ("Satu", "Dua", "Tiga")]})) is None
    magnet = {
        "type": "sort", "prompt": "?", "game": "magnet",
        "groups": [{"id": "a", "name": "Ditarik magnet"}, {"id": "b", "name": "Tidak ditarik"}],
        "items": [{"text": "Paku besi", "group": "a"}, {"text": "Kayu", "group": "b"}, {"text": "Getah", "group": "b"}],
    }
    assert game_for(one(magnet)) == "magnet"
    wrong = {**magnet, "items": [{"text": "Emas", "group": "a"}, {"text": "Kayu", "group": "b"}, {"text": "Getah", "group": "b"}]}
    assert game_for(one(wrong)) is None  # gold is not magnetic: the magnet would show a lie
    cycle = {"type": "order", "prompt": "?", "game": "kitaran", "items": [{"text": t} for t in ("Telur", "Berudu", "Katak muda", "Katak dewasa")]}
    assert game_for(one(cycle)) == "kitaran"
    assert game_for(one({**cycle, "items": [{"text": t} for t in ("Isnin", "Selasa", "Rabu")]})) is None
    elements = {"type": "match", "prompt": "?", "game": "unsur", "pairs": [{"left": "Fe", "right": "Ferum"}, {"left": "O", "right": "Oksigen"}]}
    assert game_for(one(elements)) == "unsur"
    assert game_for(one({**elements, "pairs": [{"left": "Kaca", "right": "Tingkap"}, {"left": "Kayu", "right": "Meja"}]})) is None


def test_every_sample_question_written_for_a_game_is_played_as_it() -> None:
    from didik_live.games import game_for

    for sample in SUBJECT_SAMPLES:
        for question in parse_questions(sample["questions"]):
            assert game_for(question) == question.game, (sample["title"], question.prompt)


def test_the_picture_library_is_complete_licensed_and_matches_the_lexicon() -> None:
    import json

    from didik_live import lexicon

    folder = WEB / "static" / "game-assets"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))["assets"]
    keys = {m["key"] for m in manifest}
    allowed = re.compile(r"^(public domain|pd\b.*|cc0.*|cc[ -]by([ -]sa)?[ -]\d\.\d.*|no restrictions|attribution)$", re.I)
    for m in manifest:
        assert (folder / f"{m['key']}.webp").is_file(), m["key"]
        assert allowed.match(m["licence"]), (m["key"], m["licence"])
        assert m["author"] or m["licence"].lower() in ("public domain", "cc0", "no restrictions"), m["key"]
        assert m["bytes"] < 260_000, m["key"]  # sized for a phone
    assert {p.relative_to(folder).with_suffix("").as_posix() for p in folder.rglob("*.webp")} == keys
    for group, entries in lexicon.LEXICON.items():
        for entry in entries:
            assert entry["key"] is None or entry["key"] in keys, (group, entry["name"], entry["key"])
    # the web knows every picture's size
    sizes = (WEB / "src" / "lib" / "subjects" / "assets.gen.ts").read_text(encoding="utf-8")
    assert all(f"'{k}'" in sizes for k in keys)
