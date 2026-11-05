from __future__ import annotations

import json
import random

import pytest
from pydantic import ValidationError

from didik_live.questions import QuestionOne, parse_questions, present
from didik_live.seed import SAMPLES
from didik_live.text import matches, normalize, parse_number


def one(raw: dict):
    return QuestionOne.validate_python(raw)


EVERY_TYPE = [
    {"type": "single", "prompt": "3 + 4?", "choices": [{"text": "7", "correct": True}, {"text": "6"}, {"text": "8"}]},
    {"type": "multiple", "prompt": "Genap?", "choices": [{"text": "2", "correct": True}, {"text": "4", "correct": True}, {"text": "7"}]},
    {"type": "truefalse", "prompt": "Penyu bertelur di pantai.", "answer": True},
    {"type": "text", "prompt": "Warna daun?", "answers": ["hijau"]},
    {"type": "number", "prompt": "Kaki labah-labah?", "answer": 8},
    {"type": "order", "prompt": "Susun.", "items": [{"text": "Telur"}, {"text": "Ulat"}, {"text": "Kepompong"}]},
    {"type": "match", "prompt": "Padankan.", "pairs": [{"left": "Besar", "right": "Kecil"}, {"left": "Panas", "right": "Sejuk"}]},
    {"type": "blank", "prompt": "Isi.", "sentence": "Adik [minum] susu.", "distractors": ["makan"]},
    {"type": "count", "prompt": "Masukkan 7 ekor ayam ke dalam bas.", "sticker": "ayam", "place": "bas", "answer": 7},
    {"type": "spell", "prompt": "Eja.", "word": "buku", "sticker": "buku", "decoys": 2},
    {
        "type": "sort",
        "prompt": "Darat atau laut?",
        "groups": [{"id": "darat", "name": "Darat"}, {"id": "laut", "name": "Laut"}],
        "items": [
            {"text": "Kucing", "sticker": "kucing", "group": "darat"},
            {"text": "Ikan", "sticker": "ikan", "group": "laut"},
            {"text": "Ketam", "group": "laut"},
        ],
    },
]


@pytest.mark.parametrize("raw", EVERY_TYPE, ids=lambda r: r["type"])
def test_the_public_copy_never_carries_the_answer(raw: dict) -> None:
    question = one(raw)
    pres = present(question, random.Random(1))
    text = json.dumps(pres.public)

    assert '"correct"' not in text and '"answer"' not in text and '"answers"' not in text
    # Option ids are replaced by tokens, so stored ids (and their order) say nothing.
    for real_id in pres.token_to_id.values():
        assert real_id not in text
    if raw["type"] == "blank":
        assert "minum" in pres.public["bank"]  # the word bank is the point of the question


@pytest.mark.parametrize("raw", EVERY_TYPE, ids=lambda r: r["type"])
def test_every_type_accepts_the_right_answer_and_refuses_a_wrong_one(raw: dict) -> None:
    rng = random.Random(7)
    pres = present(one(raw), rng)

    right = pres.check(pres.sample_answer(True, rng))
    wrong = pres.check(pres.sample_answer(False, rng))

    assert right is not None and right.correct and right.fraction == 1.0
    assert wrong is not None and not wrong.correct


@pytest.mark.parametrize("raw", EVERY_TYPE, ids=lambda r: r["type"])
def test_garbage_answers_are_refused_not_crashed_on(raw: dict) -> None:
    pres = present(one(raw), random.Random(3))
    for junk in (None, 5, "x" * 500, {"a": 1}, ["nope"], [[1]], "true"):
        outcome = pres.check(junk)
        assert outcome is None or not outcome.correct


def test_order_is_never_shown_already_solved() -> None:
    question = one(EVERY_TYPE[5])
    for seed in range(50):
        pres = present(question, random.Random(seed))
        shown = [pres.token_to_id[i["id"]] for i in pres.public["items"]]
        assert shown != [i.id for i in question.items]


def test_partial_credit_for_choose_all_and_matching() -> None:
    pres = present(one(EVERY_TYPE[1]), random.Random(1))
    tokens = {c["text"]: c["id"] for c in pres.public["choices"]}
    half = pres.check([tokens["2"]])
    assert half is not None and not half.correct and half.fraction == 0.5

    noisy = pres.check([tokens["2"], tokens["7"]])
    assert noisy is not None and noisy.fraction == 0.0

    match = present(one(EVERY_TYPE[6]), random.Random(1))
    left = {i["text"]: i["id"] for i in match.public["left"]}
    right = {i["text"]: i["id"] for i in match.public["right"]}
    outcome = match.check({left["Besar"]: right["Kecil"], left["Panas"]: right["Kecil"]})
    assert outcome is None  # one right side used twice is not a real answer
    outcome = match.check({left["Besar"]: right["Kecil"]})
    assert outcome is not None and outcome.fraction == 0.5


def test_typed_answers_forgive_case_accents_spacing_and_one_slip() -> None:
    assert normalize("  Hijau!! ") == "hijau"
    assert matches("HIJAU", ["hijau"])
    assert matches("hijua", ["hijau"])  # one transposition
    assert matches("Gunung  kinabalu", ["Gunung Kinabalu"])
    assert not matches("biru", ["hijau"])
    assert not matches("ab", ["ac"])  # too short to forgive
    assert not matches("hijua", ["hijau"], forgive_typo=False)


def test_numbers_accept_commas_and_tolerance() -> None:
    assert parse_number("3,5") == 3.5
    assert parse_number(" 12 ") == 12
    assert parse_number("12a") is None
    assert parse_number(True) is None

    pres = present(one({"type": "number", "prompt": "Anggar", "answer": 10, "tolerance": 2}), random.Random(1))
    assert pres.check("12").correct
    assert not pres.check("12.5").correct


def test_blank_alternatives_and_validation() -> None:
    pres = present(one({"type": "blank", "prompt": "Isi", "sentence": "Dia sangat [cerdik/bijak]."}), random.Random(1))
    assert pres.check(["Bijak"]).correct
    assert pres.public["parts"] == ["Dia sangat ", {"blank": 0}, "."]

    with pytest.raises(ValidationError):
        one({"type": "blank", "prompt": "Isi", "sentence": "Tiada tempat kosong."})
    with pytest.raises(ValidationError):
        one({"type": "blank", "prompt": "Isi", "sentence": "Adik [minum] susu.", "distractors": ["Minum"]})


@pytest.mark.parametrize(
    "raw",
    [
        {"type": "single", "prompt": "?", "choices": [{"text": "a", "correct": True}, {"text": "b", "correct": True}]},
        {"type": "single", "prompt": "?", "choices": [{"text": "a"}, {"text": "A ", "correct": True}]},
        {"type": "multiple", "prompt": "?", "choices": [{"text": "a", "correct": True}, {"text": "b", "correct": True}, {"text": "c", "correct": True}]},
        {"type": "text", "prompt": "?", "answers": ["!!"]},
        {"type": "order", "prompt": "?", "items": [{"text": "a"}, {"text": "b"}]},
        {"type": "match", "prompt": "?", "pairs": [{"left": "a", "right": "x"}, {"left": "b", "right": "x"}]},
        {"type": "single", "prompt": "?", "image": "https://evil.example/x.png", "choices": [{"text": "a", "correct": True}, {"text": "b"}]},
        {"type": "truefalse", "prompt": "?", "answer": True, "time_limit": 2},
        {"type": "count", "prompt": "?", "sticker": "../../etc/passwd", "answer": 3},
        {"type": "count", "prompt": "?", "sticker": "ayam", "place": "almari", "answer": 3},
        {"type": "count", "prompt": "?", "sticker": "ayam", "answer": 21},
        {"type": "spell", "prompt": "?", "word": "dua kata"},
        {"type": "spell", "prompt": "?", "word": "a"},
        {"type": "sort", "prompt": "?", "groups": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}],
         "items": [{"text": "x", "group": "a"}, {"text": "y", "group": "a"}, {"text": "z", "group": "a"}]},
        {"type": "sort", "prompt": "?", "groups": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}],
         "items": [{"text": "x", "group": "a"}, {"text": "y", "group": "b"}, {"text": "z", "group": "c"}]},
    ],
)
def test_broken_questions_are_refused(raw: dict) -> None:
    with pytest.raises(ValidationError):
        one(raw)


def test_samples_are_valid_and_cover_every_type() -> None:
    seen = set()
    for sample in SAMPLES:
        seen |= {q.type for q in parse_questions(sample["questions"])}
    assert seen == {"single", "multiple", "truefalse", "text", "number", "order", "match", "blank", "count", "spell", "sort"}


# ---------------------------------------------------------------- the hands-on types


def test_count_gives_a_pile_bigger_than_the_answer_and_wants_a_whole_number() -> None:
    question = one(EVERY_TYPE[8])
    for seed in range(30):
        pres = present(question, random.Random(seed))
        assert question.answer < pres.public["supply"] <= 20
    assert pres.check(7).correct
    assert not pres.check(6).correct
    assert pres.check(True) is None and pres.check("7") is None and pres.check(7.5) is None and pres.check(99) is None
    assert pres.reveal() == {"correct": 7}


def test_spell_is_never_handed_over_spelt_and_any_tile_of_a_letter_will_do() -> None:
    question = one(EVERY_TYPE[9])
    for seed in range(40):
        pres = present(question, random.Random(seed))
        tiles = pres.public["tiles"]
        assert len(tiles) == 4 + 2 and pres.public["length"] == 4
        assert "".join(t["ch"] for t in tiles[:4]) != "buku"
    letters = {t["id"]: t["ch"] for t in tiles}
    u_tiles = [t for t, ch in letters.items() if ch == "u"]
    b = next(t for t, ch in letters.items() if ch == "b")
    k = next(t for t, ch in letters.items() if ch == "k")
    # either "u" tile can go in either "u" place
    assert pres.check([b, u_tiles[1], k, u_tiles[0]]).correct
    assert pres.check([b, u_tiles[0], k, u_tiles[1]]).correct
    assert pres.check([b, u_tiles[0], k, u_tiles[0]]) is None  # one tile used twice
    swapped = pres.check([u_tiles[0], b, k, u_tiles[1]])
    assert not swapped.correct and swapped.fraction == 0.5
    assert pres.reveal()["word"] == "buku"


def test_spell_capitals_follow_the_word_and_checking_ignores_case() -> None:
    pres = present(one({"type": "spell", "prompt": "Eja.", "word": "IKAN", "decoys": 3}), random.Random(2))
    assert all(t["ch"].isupper() for t in pres.public["tiles"])
    assert pres.check(pres.sample_answer(True, random.Random(1))).correct


def test_sort_scores_each_thing_in_its_basket() -> None:
    pres = present(one(EVERY_TYPE[10]), random.Random(4))
    items = {i["text"]: i["id"] for i in pres.public["items"]}
    groups = {g["name"]: g["id"] for g in pres.public["groups"]}
    right = {items["Kucing"]: groups["Darat"], items["Ikan"]: groups["Laut"], items["Ketam"]: groups["Laut"]}
    assert pres.check(right).correct
    one_off = {**right, items["Ketam"]: groups["Darat"]}
    outcome = pres.check(one_off)
    assert not outcome.correct and outcome.fraction == 0.667
    assert pres.check({items["Kucing"]: groups["Darat"]}) is None  # every thing must be placed
    assert pres.check({**right, items["Kucing"]: items["Ikan"]}) is None  # a thing is not a basket
    assert pres.reveal()["correct"] == right
