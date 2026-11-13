"""The seventeen question types a parent can write, and how each one is shown, answered and checked.

A question reaches a child only as a *presentation*: a copy with the answers removed, the options
shuffled and every option renamed with a random token. The tokens map back to the real ids only on the
server, so nothing in the browser (not even option order or ids) reveals the answer before it is checked.
(A jigsaw is the one exception by nature: the picture on each piece is where it goes.)

Every question may have a picture (a 3D sticker or a diagram, beside or instead of an uploaded image) and
an explanation. The explanation reaches the browser only with the answer (`reveal`), to be shown to a
child who did not get it right. A question may also name a subject game (games.py), a way of playing its
type: the game changes how the child answers, never how the answer is checked.
"""

from __future__ import annotations

import random
import re
import secrets
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from . import text as textutil
from .diagrams import check_diagram
from .games import check_game, game_for
from .stickers import PLACES, STICKERS, check_sticker

ID_PATTERN = r"^[A-Za-z0-9_-]{1,16}$"
IMAGE_PATTERN = re.compile(r"^/uploads/[a-f0-9]{32}\.webp$")
BLANK_PATTERN = re.compile(r"\[([^\[\]]{1,40})\]")
MAX_QUESTIONS = 60

TYPE_LABELS = {
    "single": "Pilihan tunggal",
    "multiple": "Pilih semua yang betul",
    "truefalse": "Betul atau salah",
    "text": "Taip jawapan",
    "number": "Nombor",
    "order": "Susun turutan",
    "match": "Padankan",
    "blank": "Isi tempat kosong",
    "count": "Kira dan masukkan",
    "spell": "Susun huruf",
    "sort": "Isih kumpulan",
    "missing": "Huruf hilang",
    "puzzle": "Cantum gambar",
    "blocks": "Bina nombor",
    "clock": "Laraskan jam",
    "money": "Bayar dengan wang",
    "diagram": "Label rajah",
}

# Letters a "Susun huruf" word may use: Malay and English words, written with or without capitals.
WORD_PATTERN = re.compile(r"^[A-Za-z]{2,12}$")
DECOY_LETTERS = "abcdeghiklmnoprstuy"
COUNT_MAX = 20
# Malaysian money in sen: the coins, then the notes, as a child pays with them.
MONEY = (5, 10, 20, 50, 100, 500, 1000, 5000)
MONEY_MAX = 10000
PLACES_NAMES = ("ratus", "puluh", "sa")


def new_id() -> str:
    return secrets.token_urlsafe(6)[:8]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Choice(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    text: str = Field(min_length=1, max_length=120)
    correct: bool = False
    # a picture on the option, for children who cannot read yet ("Yang mana kucing?")
    sticker: str | None = Field(default=None, max_length=24)

    @field_validator("sticker")
    @classmethod
    def _sticker(cls, value: str | None) -> str | None:
        return check_sticker(value)


class Item(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    text: str = Field(min_length=1, max_length=80)


class Pair(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    left: str = Field(min_length=1, max_length=60)
    right: str = Field(min_length=1, max_length=60)
    # a picture on the left side: match the picture to its word
    sticker: str | None = Field(default=None, max_length=24)

    @field_validator("sticker")
    @classmethod
    def _sticker(cls, value: str | None) -> str | None:
        return check_sticker(value)


def _distinct(values: list[str], message: str) -> None:
    seen = [textutil.normalize(v) for v in values]
    if len(set(seen)) != len(seen):
        raise ValueError(message)


class _Question(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    prompt: str = Field(min_length=1, max_length=300)
    image: str | None = Field(default=None, max_length=80)
    # what illustrates the question (the "gambar rajah"): a 3D sticker, or a diagram or photo (diagrams.py)
    picture: str | None = Field(default=None, max_length=24)
    # why the answer is what it is, shown to a child who got it wrong
    explain: str = Field(default="", max_length=400)
    time_limit: int = Field(default=20, ge=5, le=120)
    # a subject game to play this question in (games.py), or none for the plain way
    game: str | None = Field(default=None, max_length=24)

    @field_validator("picture")
    @classmethod
    def _picture(cls, value: str | None) -> str | None:
        if value and value not in STICKERS:
            return check_diagram(value)
        return check_sticker(value)

    @model_validator(mode="after")
    def _game_fits(self) -> _Question:
        self.game = check_game(self.game, getattr(self, "type", ""))
        return self

    @field_validator("image")
    @classmethod
    def _image(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        if not IMAGE_PATTERN.match(value):
            raise ValueError("Gambar tidak dikenali. Muat naik semula.")
        return value


class SingleQuestion(_Question):
    type: Literal["single"]
    choices: list[Choice] = Field(min_length=2, max_length=6)

    @model_validator(mode="after")
    def _check(self) -> SingleQuestion:
        _distinct([c.text for c in self.choices], "Setiap pilihan mesti berbeza.")
        if sum(c.correct for c in self.choices) != 1:
            raise ValueError("Tandakan tepat satu jawapan yang betul.")
        return self


class MultipleQuestion(_Question):
    type: Literal["multiple"]
    choices: list[Choice] = Field(min_length=3, max_length=6)
    partial: bool = True

    @model_validator(mode="after")
    def _check(self) -> MultipleQuestion:
        _distinct([c.text for c in self.choices], "Setiap pilihan mesti berbeza.")
        correct = sum(c.correct for c in self.choices)
        if correct < 1:
            raise ValueError("Tandakan sekurang-kurangnya satu jawapan yang betul.")
        if correct == len(self.choices):
            raise ValueError("Sekurang-kurangnya satu pilihan mesti salah.")
        return self


class TrueFalseQuestion(_Question):
    type: Literal["truefalse"]
    answer: bool


class TextQuestion(_Question):
    type: Literal["text"]
    answers: list[Annotated[str, Field(min_length=1, max_length=60)]] = Field(min_length=1, max_length=8)
    forgive_typo: bool = True

    @model_validator(mode="after")
    def _check(self) -> TextQuestion:
        if not all(textutil.normalize(a) for a in self.answers):
            raise ValueError("Jawapan mesti mengandungi huruf atau nombor.")
        return self


class NumberQuestion(_Question):
    type: Literal["number"]
    answer: float = Field(ge=-1_000_000_000, le=1_000_000_000)
    tolerance: float = Field(default=0, ge=0, le=1_000_000)
    unit: str = Field(default="", max_length=16)


class OrderQuestion(_Question):
    type: Literal["order"]
    # Stored in the correct order; shuffled only when shown.
    items: list[Item] = Field(min_length=3, max_length=6)

    @model_validator(mode="after")
    def _check(self) -> OrderQuestion:
        _distinct([i.text for i in self.items], "Setiap item mesti berbeza.")
        return self


class MatchQuestion(_Question):
    type: Literal["match"]
    pairs: list[Pair] = Field(min_length=2, max_length=5)

    @model_validator(mode="after")
    def _check(self) -> MatchQuestion:
        _distinct([p.left for p in self.pairs], "Setiap perkara di kiri mesti berbeza.")
        _distinct([p.right for p in self.pairs], "Setiap padanan di kanan mesti berbeza.")
        return self


class BlankQuestion(_Question):
    type: Literal["blank"]
    # "Adik [minum] susu setiap pagi." Alternatives inside one blank: [minum/meminum].
    sentence: str = Field(min_length=3, max_length=300)
    distractors: list[Annotated[str, Field(min_length=1, max_length=40)]] = Field(default_factory=list, max_length=6)
    word_bank: bool = True

    @model_validator(mode="after")
    def _check(self) -> BlankQuestion:
        blanks = self.blanks()
        if not 1 <= len(blanks) <= 4:
            raise ValueError("Tulis 1 hingga 4 tempat kosong dalam kurungan, contoh: Adik [minum] susu.")
        if any(not alts for alts in blanks):
            raise ValueError("Setiap tempat kosong mesti ada jawapan.")
        rest = BLANK_PATTERN.sub("", self.sentence)
        if "[" in rest or "]" in rest:
            raise ValueError("Kurungan [ ] tidak lengkap.")
        answers = {textutil.normalize(alt) for alts in blanks for alt in alts}
        if any(textutil.normalize(d) in answers for d in self.distractors):
            raise ValueError("Perkataan pengganggu tidak boleh sama dengan jawapan.")
        return self

    def blanks(self) -> list[list[str]]:
        return [[a.strip() for a in m.group(1).split("/") if a.strip()] for m in BLANK_PATTERN.finditer(self.sentence)]

    def parts(self) -> list[str | dict[str, int]]:
        parts: list[str | dict[str, int]] = []
        last = 0
        for index, match in enumerate(BLANK_PATTERN.finditer(self.sentence)):
            if match.start() > last:
                parts.append(self.sentence[last : match.start()])
            parts.append({"blank": index})
            last = match.end()
        if last < len(self.sentence):
            parts.append(self.sentence[last:])
        return parts


class CountQuestion(_Question):
    """Kira dan masukkan: drag (or tap) the right number of objects into a basket, a box, a bus."""

    type: Literal["count"]
    sticker: str = Field(max_length=24)
    place: str = Field(default="bakul", max_length=24)
    answer: int = Field(ge=1, le=COUNT_MAX)

    @field_validator("sticker")
    @classmethod
    def _sticker(cls, value: str) -> str:
        if not check_sticker(value):
            raise ValueError("Pilih gambar objek untuk dikira.")
        return value

    @field_validator("place")
    @classmethod
    def _place(cls, value: str) -> str:
        if value not in PLACES:
            raise ValueError("Tempat tidak dikenali.")
        return value


class SpellQuestion(_Question):
    """Susun huruf: the word's letters, mixed up, to be put back in order. A sticker or the question's
    picture shows what the word is."""

    type: Literal["spell"]
    word: str = Field(min_length=2, max_length=12)
    sticker: str | None = Field(default=None, max_length=24)
    decoys: int = Field(default=0, ge=0, le=4)

    @field_validator("word")
    @classmethod
    def _word(cls, value: str) -> str:
        if not WORD_PATTERN.match(value):
            raise ValueError("Satu perkataan sahaja, 2 hingga 12 huruf (tanpa jarak, nombor atau tanda).")
        return value

    @field_validator("sticker")
    @classmethod
    def _sticker(cls, value: str | None) -> str | None:
        return check_sticker(value)


class SortGroup(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    name: str = Field(min_length=1, max_length=30)
    sticker: str | None = Field(default=None, max_length=24)

    @field_validator("sticker")
    @classmethod
    def _sticker(cls, value: str | None) -> str | None:
        return check_sticker(value)


class SortItem(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    text: str = Field(min_length=1, max_length=40)
    sticker: str | None = Field(default=None, max_length=24)
    group: str = Field(pattern=ID_PATTERN)

    @field_validator("sticker")
    @classmethod
    def _sticker(cls, value: str | None) -> str | None:
        return check_sticker(value)


class SortQuestion(_Question):
    """Isih kumpulan: put each thing into the basket it belongs to (land or sea, fruit or vegetable)."""

    type: Literal["sort"]
    groups: list[SortGroup] = Field(min_length=2, max_length=3)
    items: list[SortItem] = Field(min_length=3, max_length=8)

    @model_validator(mode="after")
    def _check(self) -> SortQuestion:
        _distinct([g.name for g in self.groups], "Setiap kumpulan mesti berbeza namanya.")
        _distinct([i.text for i in self.items], "Setiap benda mesti berbeza.")
        ids = {g.id for g in self.groups}
        if len(ids) != len(self.groups):
            raise ValueError("Kumpulan berulang.")
        if any(i.group not in ids for i in self.items):
            raise ValueError("Setiap benda mesti masuk satu kumpulan.")
        if any(not any(i.group == g.id for i in self.items) for g in self.groups):
            raise ValueError("Setiap kumpulan mesti ada sekurang-kurangnya satu benda.")
        return self


class MissingQuestion(_Question):
    """Huruf hilang: a word with one to three letters left out; letter tiles fill the gaps."""

    type: Literal["missing"]
    word: str = Field(min_length=2, max_length=12)
    hide: list[int] = Field(min_length=1, max_length=3)
    sticker: str | None = Field(default=None, max_length=24)
    decoys: int = Field(default=2, ge=0, le=4)

    @field_validator("word")
    @classmethod
    def _word(cls, value: str) -> str:
        if not WORD_PATTERN.match(value):
            raise ValueError("Satu perkataan sahaja, 2 hingga 12 huruf (tanpa jarak, nombor atau tanda).")
        return value

    @field_validator("sticker")
    @classmethod
    def _sticker(cls, value: str | None) -> str | None:
        return check_sticker(value)

    @model_validator(mode="after")
    def _check(self) -> MissingQuestion:
        if len(set(self.hide)) != len(self.hide) or any(not 0 <= i < len(self.word) for i in self.hide):
            raise ValueError("Pilih huruf yang hendak disembunyikan.")
        if len(self.hide) >= len(self.word):
            raise ValueError("Biarkan sekurang-kurangnya satu huruf kelihatan.")
        self.hide = sorted(self.hide)
        return self


class PuzzleQuestion(_Question):
    """Cantum gambar: a picture cut into 4 or 9 pieces to put back together."""

    type: Literal["puzzle"]
    sticker: str | None = Field(default=None, max_length=24)
    grid: Literal[2, 3] = 2

    @field_validator("sticker")
    @classmethod
    def _sticker(cls, value: str | None) -> str | None:
        return check_sticker(value)

    @model_validator(mode="after")
    def _check(self) -> PuzzleQuestion:
        if not self.sticker and not self.image:
            raise ValueError("Pilih pelekat atau muat naik gambar untuk dicantum.")
        return self


class BlocksQuestion(_Question):
    """Bina nombor: make a number with hundreds, tens and ones blocks (place value)."""

    type: Literal["blocks"]
    answer: int = Field(ge=1, le=999)


class ClockQuestion(_Question):
    """Laraskan jam: turn the hands of a clock to a time, to five minutes."""

    type: Literal["clock"]
    hour: int = Field(ge=1, le=12)
    minute: int = Field(default=0, ge=0, le=55)

    @field_validator("minute")
    @classmethod
    def _minute(cls, value: int) -> int:
        if value % 5:
            raise ValueError("Minit mesti gandaan 5 (0, 5, 10 ... 55).")
        return value


class MoneyQuestion(_Question):
    """Bayar dengan wang: pay an amount exactly with Malaysian coins and notes."""

    type: Literal["money"]
    amount: int = Field(ge=5, le=MONEY_MAX)
    sticker: str | None = Field(default=None, max_length=24)

    @field_validator("amount")
    @classmethod
    def _amount(cls, value: int) -> int:
        if value % 5:
            raise ValueError("Jumlah mesti gandaan 5 sen.")
        return value

    @field_validator("sticker")
    @classmethod
    def _sticker(cls, value: str | None) -> str | None:
        return check_sticker(value)


class Spot(_Strict):
    """A place on a diagram, in percent of its width and height from the top left, and what it is."""

    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    x: float = Field(ge=0, le=100)
    y: float = Field(ge=0, le=100)
    label: str = Field(min_length=1, max_length=40)


class DiagramQuestion(_Question):
    """Label rajah: name the parts of a diagram (the heart, a cell, the states on a map) by putting each
    label on its place."""

    type: Literal["diagram"]
    diagram: str = Field(max_length=24)
    spots: list[Spot] = Field(min_length=2, max_length=6)

    @field_validator("diagram")
    @classmethod
    def _diagram(cls, value: str) -> str:
        if not check_diagram(value):
            raise ValueError("Pilih rajah untuk dilabel.")
        return value

    @model_validator(mode="after")
    def _check(self) -> DiagramQuestion:
        _distinct([s.label for s in self.spots], "Setiap label mesti berbeza.")
        for i, a in enumerate(self.spots):
            for b in self.spots[i + 1 :]:
                if abs(a.x - b.x) < 6 and abs(a.y - b.y) < 6:
                    raise ValueError("Dua tempat terlalu dekat: jarakkan sedikit supaya mudah diletak label.")
        return self


Question = Annotated[
    Union[
        SingleQuestion,
        MultipleQuestion,
        TrueFalseQuestion,
        TextQuestion,
        NumberQuestion,
        OrderQuestion,
        MatchQuestion,
        BlankQuestion,
        CountQuestion,
        SpellQuestion,
        SortQuestion,
        MissingQuestion,
        PuzzleQuestion,
        BlocksQuestion,
        ClockQuestion,
        MoneyQuestion,
        DiagramQuestion,
    ],
    Field(discriminator="type"),
]

QuestionList = TypeAdapter(list[Question])
QuestionOne = TypeAdapter(Question)


def parse_questions(raw: list[dict[str, Any]]) -> list[Any]:
    return QuestionList.validate_python(raw)


def unique_ids(questions: list[Any]) -> list[Any]:
    """Gives copied questions fresh ids so that ids stay unique within a quiz."""
    seen: set[str] = set()
    for question in questions:
        if question.id in seen:
            question.id = new_id()
        seen.add(question.id)
    return questions


@dataclass
class Outcome:
    correct: bool
    fraction: float


@dataclass
class Presentation:
    """One showing of a question. `public` goes to the browser; everything else stays here."""

    question: Any
    public: dict[str, Any]
    token_to_id: dict[str, str] = field(default_factory=dict)
    id_to_token: dict[str, str] = field(default_factory=dict)

    @property
    def type(self) -> str:
        return self.question.type

    def check(self, answer: Any) -> Outcome | None:
        """Returns None when the answer is not even the right shape (a broken or forged message)."""
        try:
            return _CHECKERS[self.type](self, answer)
        except (TypeError, ValueError, KeyError, AttributeError):
            return None

    def reveal(self) -> dict[str, Any]:
        out = _REVEALS[self.type](self)
        if self.question.explain:
            out["explain"] = self.question.explain
        return out

    def sample_answer(self, correct: bool, rng: random.Random) -> Any:
        """A well-formed answer, right or wrong. Used by the practice bots."""
        return _SAMPLES[self.type](self, correct, rng)


def _with_sticker(item: dict[str, Any], sticker: str | None) -> dict[str, Any]:
    if sticker:
        item["sticker"] = sticker
    return item


def _token(pres: Presentation, real_id: str) -> str:
    token = secrets.token_hex(3)
    while token in pres.token_to_id:
        token = secrets.token_hex(3)
    pres.token_to_id[token] = real_id
    pres.id_to_token[real_id] = token
    return token


def present(question: Any, rng: random.Random, time_limit: int | None = None) -> Presentation:
    pres = Presentation(question=question, public={})
    public: dict[str, Any] = {
        "id": question.id,
        "type": question.type,
        "label": TYPE_LABELS[question.type],
        "prompt": question.prompt,
        "image": question.image,
        "picture": question.picture,
        "timeLimit": time_limit or question.time_limit,
    }
    game = game_for(question)
    if game:
        public["game"] = game

    if question.type in ("single", "multiple"):
        choices = list(question.choices)
        rng.shuffle(choices)
        public["choices"] = [_with_sticker({"id": _token(pres, c.id), "text": c.text}, c.sticker) for c in choices]
        if question.type == "multiple":
            public["pick"] = sum(c.correct for c in question.choices)
    elif question.type == "text":
        public["maxLength"] = 60
    elif question.type == "number":
        public["unit"] = question.unit
    elif question.type == "order":
        items = list(question.items)
        while [i.id for i in items] == [i.id for i in question.items]:
            rng.shuffle(items)
        public["items"] = [{"id": _token(pres, i.id), "text": i.text} for i in items]
    elif question.type == "match":
        rights = list(question.pairs)
        rng.shuffle(rights)
        public["left"] = [_with_sticker({"id": _token(pres, "L" + p.id), "text": p.left}, p.sticker) for p in question.pairs]
        public["right"] = [{"id": _token(pres, "R" + p.id), "text": p.right} for p in rights]
    elif question.type == "blank":
        public["parts"] = question.parts()
        public["blanks"] = len(question.blanks())
        if question.word_bank:
            words = [alts[0] for alts in question.blanks()] + list(question.distractors)
            rng.shuffle(words)
            public["bank"] = words
    elif question.type == "count":
        public["sticker"] = question.sticker
        public["place"] = question.place
        # a few more than needed, so the pile itself never gives the answer away
        public["supply"] = min(COUNT_MAX, max(8, question.answer + rng.randint(2, 4)))
    elif question.type == "spell":
        word = question.word
        letters = list(word) + [rng.choice(DECOY_LETTERS) for _ in range(question.decoys)]
        if word.isupper():
            letters = [ch.upper() for ch in letters]
        order = list(range(len(letters)))
        # mixed up, never handed over already spelt (unless every letter is the same, as in "AA")
        for _ in range(30):
            rng.shuffle(order)
            if "".join(letters[i] for i in order[: len(word)]) != word:
                break
        public["tiles"] = [{"id": _token(pres, f"t{i}"), "ch": letters[i]} for i in order]
        public["length"] = len(word)
        public["sticker"] = question.sticker
    elif question.type == "sort":
        items = list(question.items)
        rng.shuffle(items)
        public["groups"] = [{"id": _token(pres, "G" + g.id), "name": g.name, "sticker": g.sticker} for g in question.groups]
        public["items"] = [{"id": _token(pres, "I" + i.id), "text": i.text, "sticker": i.sticker} for i in items]
    elif question.type == "missing":
        word = question.word
        hidden = [word[i] for i in question.hide]
        taken = {ch.casefold() for ch in hidden}
        spare = [ch for ch in DECOY_LETTERS if ch not in taken]
        rng.shuffle(spare)
        letters = hidden + spare[: question.decoys]
        if word.isupper():
            letters = [ch.upper() for ch in letters]
        order = list(range(len(letters)))
        rng.shuffle(order)
        public["tiles"] = [{"id": _token(pres, f"m{i}"), "ch": letters[i]} for i in order]
        blanks = {i: k for k, i in enumerate(question.hide)}
        public["parts"] = [{"blank": blanks[i]} if i in blanks else {"ch": ch} for i, ch in enumerate(word)]
        public["blanks"] = len(question.hide)
        public["sticker"] = question.sticker
    elif question.type == "puzzle":
        n = question.grid * question.grid
        order = list(range(n))
        while order == sorted(order):
            rng.shuffle(order)
        # each piece carries the part of the picture it shows ("cut"), which is the point of a jigsaw
        public["pieces"] = [{"id": _token(pres, f"p{i}"), "cut": i} for i in order]
        public["grid"] = question.grid
        public["sticker"] = question.sticker
    elif question.type == "blocks":
        public["places"] = list(PLACES_NAMES if question.answer >= 100 else PLACES_NAMES[1:])
    elif question.type == "money":
        public["amount"] = question.amount
        public["money"] = [m for m in MONEY if m <= max(question.amount, 50)]
        public["sticker"] = question.sticker
    elif question.type == "diagram":
        labels = list(question.spots)
        rng.shuffle(labels)
        public["diagram"] = question.diagram
        # where the places are says nothing about which label is which
        public["spots"] = [{"id": _token(pres, "S" + s.id), "x": s.x, "y": s.y} for s in question.spots]
        public["labels"] = [{"id": _token(pres, "B" + s.id), "text": s.label} for s in labels]

    pres.public = public
    return pres


# ---------------------------------------------------------------- checking


def _check_single(pres: Presentation, answer: Any) -> Outcome:
    chosen = pres.token_to_id[str(answer)]
    correct = next(c for c in pres.question.choices if c.correct).id
    return Outcome(chosen == correct, 1.0 if chosen == correct else 0.0)


def _check_multiple(pres: Presentation, answer: Any) -> Outcome:
    if not isinstance(answer, list) or not answer:
        raise ValueError
    chosen = {pres.token_to_id[str(t)] for t in answer}
    correct = {c.id for c in pres.question.choices if c.correct}
    if chosen == correct:
        return Outcome(True, 1.0)
    if not pres.question.partial:
        return Outcome(False, 0.0)
    fraction = max(0.0, (len(chosen & correct) - len(chosen - correct)) / len(correct))
    return Outcome(False, round(fraction, 3))


def _check_truefalse(pres: Presentation, answer: Any) -> Outcome:
    if not isinstance(answer, bool):
        raise TypeError
    ok = answer == pres.question.answer
    return Outcome(ok, 1.0 if ok else 0.0)


def _check_text(pres: Presentation, answer: Any) -> Outcome:
    if not isinstance(answer, str) or len(answer) > 120:
        raise TypeError
    ok = textutil.matches(answer, pres.question.answers, pres.question.forgive_typo)
    return Outcome(ok, 1.0 if ok else 0.0)


def _check_number(pres: Presentation, answer: Any) -> Outcome:
    value = textutil.parse_number(answer)
    if value is None:
        raise ValueError
    ok = abs(value - pres.question.answer) <= pres.question.tolerance + 1e-9
    return Outcome(ok, 1.0 if ok else 0.0)


def _check_order(pres: Presentation, answer: Any) -> Outcome:
    if not isinstance(answer, list) or len(answer) != len(pres.question.items):
        raise ValueError
    chosen = [pres.token_to_id[str(t)] for t in answer]
    if len(set(chosen)) != len(chosen):
        raise ValueError
    right = sum(a == b.id for a, b in zip(chosen, pres.question.items, strict=True))
    total = len(pres.question.items)
    return Outcome(right == total, round(right / total, 3))


def _check_match(pres: Presentation, answer: Any) -> Outcome:
    if not isinstance(answer, dict):
        raise TypeError
    right = 0
    used: set[str] = set()
    for left_token, right_token in answer.items():
        left = pres.token_to_id[str(left_token)]
        target = pres.token_to_id[str(right_token)]
        if not left.startswith("L") or not target.startswith("R") or target in used:
            raise ValueError
        used.add(target)
        right += left[1:] == target[1:]
    total = len(pres.question.pairs)
    return Outcome(right == total, round(right / total, 3))


def _check_blank(pres: Presentation, answer: Any) -> Outcome:
    blanks = pres.question.blanks()
    if not isinstance(answer, list) or len(answer) != len(blanks):
        raise ValueError
    right = sum(isinstance(a, str) and textutil.matches(a, alts, forgive_typo=False) for a, alts in zip(answer, blanks, strict=True))
    return Outcome(right == len(blanks), round(right / len(blanks), 3))


def _check_count(pres: Presentation, answer: Any) -> Outcome:
    if isinstance(answer, bool) or not isinstance(answer, int) or not 0 <= answer <= COUNT_MAX:
        raise ValueError
    ok = answer == pres.question.answer
    return Outcome(ok, 1.0 if ok else 0.0)


def _spell_letters(pres: Presentation) -> dict[str, str]:
    return {str(t["id"]): str(t["ch"]) for t in pres.public["tiles"]}


def _check_spell(pres: Presentation, answer: Any) -> Outcome:
    word = pres.question.word
    letters = _spell_letters(pres)
    if not isinstance(answer, list) or len(answer) != len(word) or len({str(t) for t in answer}) != len(answer):
        raise ValueError
    built = [letters[str(t)] for t in answer]
    right = sum(a.casefold() == b.casefold() for a, b in zip(built, word, strict=True))
    return Outcome(right == len(word), round(right / len(word), 3))


def _check_sort(pres: Presentation, answer: Any) -> Outcome:
    if not isinstance(answer, dict) or len(answer) != len(pres.question.items):
        raise ValueError
    home = {i.id: i.group for i in pres.question.items}
    right = 0
    seen: set[str] = set()
    for item_token, group_token in answer.items():
        item = pres.token_to_id[str(item_token)]
        group = pres.token_to_id[str(group_token)]
        if not item.startswith("I") or not group.startswith("G") or item in seen:
            raise ValueError
        seen.add(item)
        right += home[item[1:]] == group[1:]
    total = len(pres.question.items)
    return Outcome(right == total, round(right / total, 3))


def _tile_letters(pres: Presentation) -> dict[str, str]:
    return {str(t["id"]): str(t["ch"]) for t in pres.public["tiles"]}


def _check_missing(pres: Presentation, answer: Any) -> Outcome:
    q = pres.question
    letters = _tile_letters(pres)
    if not isinstance(answer, list) or len(answer) != len(q.hide) or len({str(t) for t in answer}) != len(answer):
        raise ValueError
    given = [letters[str(t)] for t in answer]
    right = sum(a.casefold() == q.word[i].casefold() for a, i in zip(given, q.hide, strict=True))
    return Outcome(right == len(q.hide), round(right / len(q.hide), 3))


def _check_puzzle(pres: Presentation, answer: Any) -> Outcome:
    n = pres.question.grid ** 2
    if not isinstance(answer, list) or len(answer) != n or len({str(t) for t in answer}) != n:
        raise ValueError
    slots = [pres.token_to_id[str(t)] for t in answer]
    right = sum(slot == f"p{i}" for i, slot in enumerate(slots))
    return Outcome(right == n, round(right / n, 3))


def _digits(number: int) -> dict[str, int]:
    return {"ratus": number // 100, "puluh": number // 10 % 10, "sa": number % 10}


def _check_blocks(pres: Presentation, answer: Any) -> Outcome:
    if not isinstance(answer, dict):
        raise TypeError
    places = pres.public["places"]
    given = {name: answer.get(name, 0) for name in PLACES_NAMES}
    if any(isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 9 for v in given.values()):
        raise ValueError
    if any(given[name] for name in PLACES_NAMES if name not in places):
        raise ValueError
    want = _digits(pres.question.answer)
    right = sum(given[name] == want[name] for name in places)
    return Outcome(right == len(places), round(right / len(places), 3))


def _check_clock(pres: Presentation, answer: Any) -> Outcome:
    if not isinstance(answer, dict):
        raise TypeError
    h, m = answer.get("h"), answer.get("m")
    if isinstance(h, bool) or isinstance(m, bool) or not isinstance(h, int) or not isinstance(m, int):
        raise TypeError
    if not 1 <= h <= 12 or not 0 <= m <= 55 or m % 5:
        raise ValueError
    right = (h == pres.question.hour) + (m == pres.question.minute)
    return Outcome(right == 2, right / 2)


def _check_money(pres: Presentation, answer: Any) -> Outcome:
    if not isinstance(answer, dict):
        raise TypeError
    total = 0
    for key, count in answer.items():
        value = int(str(key))
        if value not in pres.public["money"] or isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= 50:
            raise ValueError
        total += value * count
    ok = total == pres.question.amount
    return Outcome(ok, 1.0 if ok else 0.0)


def _check_diagram(pres: Presentation, answer: Any) -> Outcome:
    """{spot token: label token}, every place labelled, no label used twice."""
    if not isinstance(answer, dict) or len(answer) != len(pres.question.spots):
        raise ValueError
    right = 0
    seen_spots: set[str] = set()
    seen_labels: set[str] = set()
    for spot_token, label_token in answer.items():
        spot = pres.token_to_id[str(spot_token)]
        label = pres.token_to_id[str(label_token)]
        if not spot.startswith("S") or not label.startswith("B") or spot in seen_spots or label in seen_labels:
            raise ValueError
        seen_spots.add(spot)
        seen_labels.add(label)
        right += spot[1:] == label[1:]
    total = len(pres.question.spots)
    return Outcome(right == total, round(right / total, 3))


_CHECKERS = {
    "single": _check_single,
    "multiple": _check_multiple,
    "truefalse": _check_truefalse,
    "text": _check_text,
    "number": _check_number,
    "order": _check_order,
    "match": _check_match,
    "blank": _check_blank,
    "count": _check_count,
    "spell": _check_spell,
    "sort": _check_sort,
    "missing": _check_missing,
    "puzzle": _check_puzzle,
    "blocks": _check_blocks,
    "clock": _check_clock,
    "money": _check_money,
    "diagram": _check_diagram,
}


# ---------------------------------------------------------------- the correct answer, for the reveal


def _reveal_choices(pres: Presentation) -> dict[str, Any]:
    return {"correct": [pres.id_to_token[c.id] for c in pres.question.choices if c.correct]}


def _reveal_number(pres: Presentation) -> dict[str, Any]:
    q = pres.question
    value = int(q.answer) if float(q.answer).is_integer() else q.answer
    return {"correct": value, "tolerance": q.tolerance, "unit": q.unit}


def _spell_tokens(pres: Presentation) -> list[str]:
    """The tiles that spell the word, in order (the first free tile of each letter)."""
    free = list(_spell_letters(pres).items())
    tokens: list[str] = []
    for ch in pres.question.word:
        index = next(i for i, (_, letter) in enumerate(free) if letter.casefold() == ch.casefold())
        tokens.append(free.pop(index)[0])
    return tokens


def _missing_tokens(pres: Presentation) -> list[str]:
    free = list(_tile_letters(pres).items())
    tokens: list[str] = []
    for i in pres.question.hide:
        ch = pres.question.word[i]
        index = next(k for k, (_, letter) in enumerate(free) if letter.casefold() == ch.casefold())
        tokens.append(free.pop(index)[0])
    return tokens


def _pay(amount: int, money: list[int]) -> dict[str, int]:
    """The fewest coins and notes for an amount (Malaysian money is a greedy-friendly set)."""
    out: dict[str, int] = {}
    for value in sorted(money, reverse=True):
        if amount >= value:
            out[str(value)] = amount // value
            amount %= value
    return out


_REVEALS = {
    "single": _reveal_choices,
    "multiple": _reveal_choices,
    "truefalse": lambda p: {"correct": p.question.answer},
    "text": lambda p: {"correct": p.question.answers[0], "accepted": list(p.question.answers)},
    "number": _reveal_number,
    "order": lambda p: {"correct": [p.id_to_token[i.id] for i in p.question.items]},
    "match": lambda p: {"correct": {p.id_to_token["L" + x.id]: p.id_to_token["R" + x.id] for x in p.question.pairs}},
    "blank": lambda p: {"correct": [alts[0] for alts in p.question.blanks()]},
    "count": lambda p: {"correct": p.question.answer},
    "spell": lambda p: {"correct": _spell_tokens(p), "word": p.question.word},
    "sort": lambda p: {"correct": {p.id_to_token["I" + i.id]: p.id_to_token["G" + i.group] for i in p.question.items}},
    "missing": lambda p: {"correct": _missing_tokens(p), "word": p.question.word},
    "puzzle": lambda p: {"correct": [p.id_to_token[f"p{i}"] for i in range(p.question.grid**2)]},
    "blocks": lambda p: {"correct": {k: v for k, v in _digits(p.question.answer).items() if k in p.public["places"]}, "number": p.question.answer},
    "clock": lambda p: {"correct": {"h": p.question.hour, "m": p.question.minute}},
    "money": lambda p: {"correct": p.question.amount, "pay": _pay(p.question.amount, p.public["money"])},
    "diagram": lambda p: {"correct": {p.id_to_token["S" + s.id]: p.id_to_token["B" + s.id] for s in p.question.spots}},
}


# ---------------------------------------------------------------- answers for practice bots


def _sample_single(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    pool = [c for c in pres.question.choices if c.correct == correct]
    return pres.id_to_token[rng.choice(pool).id]


def _sample_multiple(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    right = [pres.id_to_token[c.id] for c in pres.question.choices if c.correct]
    if correct:
        return right
    wrong = [pres.id_to_token[c.id] for c in pres.question.choices if not c.correct]
    return right[:-1] + [rng.choice(wrong)] if len(right) > 1 else [rng.choice(wrong)]


def _sample_number(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    q = pres.question
    if correct:
        return q.answer
    return q.answer + (q.tolerance + rng.randint(1, 5)) * rng.choice([-1, 1])


def _sample_order(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    tokens = [pres.id_to_token[i.id] for i in pres.question.items]
    if not correct:
        tokens = tokens[1:] + tokens[:1]
    return tokens


def _sample_match(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    pairs = pres.question.pairs
    rights = [pres.id_to_token["R" + p.id] for p in pairs]
    if not correct:
        rights = rights[1:] + rights[:1]
    return {pres.id_to_token["L" + p.id]: r for p, r in zip(pairs, rights, strict=True)}


def _sample_blank(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    words = [alts[0] for alts in pres.question.blanks()]
    if correct:
        return words
    return [pres.question.distractors[0] if pres.question.distractors else "entah"] + words[1:]


def _sample_count(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    answer = pres.question.answer
    if correct:
        return answer
    return answer - 1 if answer > 1 and (rng.random() < 0.5 or answer == pres.public["supply"]) else answer + 1


def _sample_spell(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    tokens = _spell_tokens(pres)
    if correct:
        return tokens
    word = pres.question.word.casefold()
    for i in range(len(tokens) - 1):
        if word[i] != word[i + 1]:
            tokens[i], tokens[i + 1] = tokens[i + 1], tokens[i]
            return tokens
    letters = _spell_letters(pres)
    spare = [t for t in letters if t not in tokens and letters[t].casefold() != word[0]]
    return [spare[0], *tokens[1:]] if spare else tokens


def _sample_sort(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    groups = [g.id for g in pres.question.groups]
    out = {}
    for index, item in enumerate(pres.question.items):
        group = item.group
        if not correct and index == 0:
            group = next(g for g in groups if g != item.group)
        out[pres.id_to_token["I" + item.id]] = pres.id_to_token["G" + group]
    return out


def _sample_missing(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    tokens = _missing_tokens(pres)
    if correct:
        return tokens
    letters = _tile_letters(pres)
    first = pres.question.word[pres.question.hide[0]].casefold()
    wrong = [t for t in letters if t not in tokens and letters[t].casefold() != first]
    return [wrong[0], *tokens[1:]] if wrong else tokens[::-1]


def _sample_puzzle(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    tokens = [pres.id_to_token[f"p{i}"] for i in range(pres.question.grid**2)]
    return tokens if correct else tokens[1:] + tokens[:1]


def _sample_blocks(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    digits = {k: v for k, v in _digits(pres.question.answer).items() if k in pres.public["places"]}
    if not correct:
        digits["sa"] = (digits["sa"] + 1) % 10
    return digits


def _sample_clock(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    q = pres.question
    return {"h": q.hour, "m": q.minute if correct else (q.minute + 30) % 60}


def _sample_money(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    pay = _pay(pres.question.amount, pres.public["money"])
    if not correct:
        pay["5"] = pay.get("5", 0) + 1
    return pay


def _sample_diagram(pres: Presentation, correct: bool, rng: random.Random) -> Any:
    spots = pres.question.spots
    labels = [pres.id_to_token["B" + s.id] for s in spots]
    if not correct:
        labels = labels[1:] + labels[:1]
    return {pres.id_to_token["S" + s.id]: b for s, b in zip(spots, labels, strict=True)}


_SAMPLES = {
    "single": _sample_single,
    "multiple": _sample_multiple,
    "truefalse": lambda p, ok, rng: p.question.answer if ok else not p.question.answer,
    "text": lambda p, ok, rng: p.question.answers[0] if ok else "entah",
    "number": _sample_number,
    "order": _sample_order,
    "match": _sample_match,
    "blank": _sample_blank,
    "count": _sample_count,
    "spell": _sample_spell,
    "sort": _sample_sort,
    "missing": _sample_missing,
    "puzzle": _sample_puzzle,
    "blocks": _sample_blocks,
    "clock": _sample_clock,
    "money": _sample_money,
    "diagram": _sample_diagram,
}
