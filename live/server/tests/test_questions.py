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
    {"type": "missing", "prompt": "Lengkapkan.", "word": "kucing", "hide": [3, 1], "sticker": "kucing"},
    {"type": "puzzle", "prompt": "Cantumkan.", "sticker": "kucing", "grid": 3},
    {"type": "blocks", "prompt": "Bina 345.", "answer": 345},
    {"type": "clock", "prompt": "Pukul 3.30.", "hour": 3, "minute": 30},
    {"type": "money", "prompt": "Bayar RM2.50.", "amount": 250, "sticker": "aiskrim"},
    {
        "type": "diagram",
        "prompt": "Labelkan organ.",
        "diagram": "rajah-organ",
        "spots": [{"x": 53, "y": 29, "label": "Jantung"}, {"x": 27, "y": 33, "label": "Paru-paru"}, {"x": 74, "y": 45, "label": "Perut"}],
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
        {"type": "missing", "prompt": "?", "word": "ikan", "hide": [0, 1, 2, 3]},
        {"type": "missing", "prompt": "?", "word": "ikan", "hide": [7]},
        {"type": "puzzle", "prompt": "?"},
        {"type": "blocks", "prompt": "?", "answer": 1000},
        {"type": "clock", "prompt": "?", "hour": 3, "minute": 7},
        {"type": "clock", "prompt": "?", "hour": 13},
        {"type": "money", "prompt": "?", "amount": 12},
        {"type": "single", "prompt": "?", "picture": "bukan-pelekat", "choices": [{"text": "a", "correct": True}, {"text": "b"}]},
        {"type": "single", "prompt": "?", "choices": [{"text": "a", "correct": True, "sticker": "x"}, {"text": "b"}]},
    ],
)
def test_broken_questions_are_refused(raw: dict) -> None:
    with pytest.raises(ValidationError):
        one(raw)


def test_samples_are_valid_and_cover_every_type() -> None:
    seen = set()
    for sample in SAMPLES:
        seen |= {q.type for q in parse_questions(sample["questions"])}
    assert seen == {
        "single", "multiple", "truefalse", "text", "number", "order", "match", "blank",
        "count", "spell", "sort", "missing", "puzzle", "blocks", "clock", "money", "diagram",
    }


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


def test_the_explanation_comes_only_with_the_answer() -> None:
    raw = {**EVERY_TYPE[0], "picture": "epal", "explain": "Tiga tambah empat ialah tujuh."}
    pres = present(one(raw), random.Random(1))
    assert pres.public["picture"] == "epal"
    assert "tujuh" not in json.dumps(pres.public)
    assert pres.reveal()["explain"] == "Tiga tambah empat ialah tujuh."
    assert "explain" not in present(one(EVERY_TYPE[0]), random.Random(1)).reveal()


def test_pictures_ride_on_choices_and_on_the_left_of_pairs() -> None:
    pres = present(one({"type": "single", "prompt": "Yang mana kucing?", "choices": [
        {"text": "Kucing", "sticker": "kucing", "correct": True}, {"text": "Ikan", "sticker": "ikan"}, {"text": "Tiada"}]}), random.Random(2))
    shown = {c["text"]: c.get("sticker") for c in pres.public["choices"]}
    assert shown == {"Kucing": "kucing", "Ikan": "ikan", "Tiada": None}
    match = present(one({"type": "match", "prompt": "Padankan.", "pairs": [
        {"left": "Kucing", "right": "Meow", "sticker": "kucing"}, {"left": "Lembu", "right": "Moo"}]}), random.Random(2))
    assert [i.get("sticker") for i in match.public["left"]] == ["kucing", None]


def test_missing_letters_fill_their_gaps_in_order() -> None:
    pres = present(one(EVERY_TYPE[11]), random.Random(3))
    assert pres.public["blanks"] == 2
    assert [p.get("ch") for p in pres.public["parts"]] == ["k", None, "c", None, "n", "g"]
    letters = {t["id"]: t["ch"] for t in pres.public["tiles"]}
    u = next(t for t, ch in letters.items() if ch == "u")
    i = next(t for t, ch in letters.items() if ch == "i")
    assert pres.check([u, i]).correct
    swapped = pres.check([i, u])
    assert not swapped.correct and swapped.fraction == 0.0
    # decoys never repeat a hidden letter, so each gap has one right tile
    assert sorted(ch for ch in letters.values() if ch in "ui") == ["i", "u"]


def test_puzzle_is_never_handed_over_solved_and_scores_each_piece() -> None:
    question = one(EVERY_TYPE[12])
    for seed in range(30):
        pres = present(question, random.Random(seed))
        assert [p["cut"] for p in pres.public["pieces"]] != list(range(9))
    by_cut = {p["cut"]: p["id"] for p in pres.public["pieces"]}
    solved = [by_cut[i] for i in range(9)]
    assert pres.check(solved).correct
    two_swapped = solved[:]
    two_swapped[0], two_swapped[1] = two_swapped[1], two_swapped[0]
    assert pres.check(two_swapped).fraction == round(7 / 9, 3)
    assert pres.check(solved[:-1]) is None


def test_blocks_count_hundreds_tens_and_ones() -> None:
    pres = present(one(EVERY_TYPE[13]), random.Random(1))
    assert pres.check({"ratus": 3, "puluh": 4, "sa": 5}).correct
    assert pres.check({"ratus": 3, "puluh": 4, "sa": 4}).fraction == 0.667
    assert pres.check({"ratus": 3, "puluh": 4, "sa": 15}) is None  # a column holds at most nine
    small = present(one({"type": "blocks", "prompt": "39", "answer": 39}), random.Random(1))
    assert small.public["places"] == ["puluh", "sa"]
    assert small.check({"puluh": 3, "sa": 9}).correct
    assert small.check({"ratus": 1, "puluh": 3, "sa": 9}) is None  # no hundreds column was shown


def test_clock_and_money() -> None:
    clock = present(one(EVERY_TYPE[14]), random.Random(1))
    assert clock.check({"h": 3, "m": 30}).correct
    assert clock.check({"h": 6, "m": 30}).fraction == 0.5
    assert clock.check({"h": 3, "m": 31}) is None
    money = present(one(EVERY_TYPE[15]), random.Random(1))
    assert money.public["money"] == [5, 10, 20, 50, 100]
    assert money.check({"100": 1, "50": 3}).correct  # any way of making RM2.50 will do
    assert not money.check({"100": 2}).correct
    assert money.check({"500": 1}) is None  # no RM5 note for a RM2.50 ice cream
    assert money.reveal()["pay"] == {"100": 2, "50": 1}


def test_every_sample_question_has_a_picture_and_an_explanation() -> None:
    for sample in SAMPLES:
        for question in parse_questions(sample["questions"]):
            where = (sample["title"], question.prompt)
            assert question.explain.strip(), where
            # a subject game draws its own scene (a lab, a dig, a compass), and a diagram is its own picture
            pictured = question.picture or getattr(question, "sticker", None) or question.type in ("blocks", "clock", "diagram") or question.game
            assert pictured, where


def test_library_samples_are_brought_up_to_date_and_copies_are_left_alone(tmp_path) -> None:
    from didik_live.db import Database
    from didik_live.models import Quiz, User
    from didik_live.seed import LIBRARY_EMAIL, refresh_samples, seed_library

    db = Database(f"sqlite:///{tmp_path / 'lib.db'}")
    db.create_all()
    with db.sessions() as session:
        assert seed_library(session) == len(SAMPLES)
        library = session.query(User).filter_by(email=LIBRARY_EMAIL).one()
        old = session.query(Quiz).filter_by(owner_id=library.id, title="Haiwan di Malaysia").one()
        # an older version of the sample, without explanations
        old.questions = [{k: v for k, v in q.items() if k != "explain"} for q in old.questions]
        parent = User(name="Ibu", email="ibu@contoh.test", password_hash="!")
        session.add(parent)
        session.flush()
        mine = Quiz(owner_id=parent.id, title="Haiwan di Malaysia", description="Salinan saya", questions=old.questions, is_sample=False)
        session.add(mine)
        session.commit()

        assert refresh_samples(session, library) == 1
        assert all(q["explain"] for q in old.questions)
        assert not any(q.get("explain") for q in mine.questions)  # a parent's copy is theirs
        assert refresh_samples(session, library) == 0  # nothing left to change
