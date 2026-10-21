"""The eight question types a parent can write, and how each one is shown, answered and checked.

A question reaches a child only as a *presentation*: a copy with the answers removed, the options
shuffled and every option renamed with a random token. The tokens map back to the real ids only on the
server, so nothing in the browser (not even option order or ids) reveals the answer before it is checked.
"""

from __future__ import annotations

import random
import re
import secrets
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from . import text as textutil

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
}


def new_id() -> str:
    return secrets.token_urlsafe(6)[:8]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Choice(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    text: str = Field(min_length=1, max_length=120)
    correct: bool = False


class Item(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    text: str = Field(min_length=1, max_length=80)


class Pair(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    left: str = Field(min_length=1, max_length=60)
    right: str = Field(min_length=1, max_length=60)


def _distinct(values: list[str], message: str) -> None:
    seen = [textutil.normalize(v) for v in values]
    if len(set(seen)) != len(seen):
        raise ValueError(message)


class _Question(_Strict):
    id: str = Field(default_factory=new_id, pattern=ID_PATTERN)
    prompt: str = Field(min_length=1, max_length=300)
    image: str | None = Field(default=None, max_length=80)
    time_limit: int = Field(default=20, ge=5, le=120)

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
        return _REVEALS[self.type](self)

    def sample_answer(self, correct: bool, rng: random.Random) -> Any:
        """A well-formed answer, right or wrong. Used by the practice bots."""
        return _SAMPLES[self.type](self, correct, rng)


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
        "timeLimit": time_limit or question.time_limit,
    }

    if question.type in ("single", "multiple"):
        choices = list(question.choices)
        rng.shuffle(choices)
        public["choices"] = [{"id": _token(pres, c.id), "text": c.text} for c in choices]
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
        public["left"] = [{"id": _token(pres, "L" + p.id), "text": p.left} for p in question.pairs]
        public["right"] = [{"id": _token(pres, "R" + p.id), "text": p.right} for p in rights]
    elif question.type == "blank":
        public["parts"] = question.parts()
        public["blanks"] = len(question.blanks())
        if question.word_bank:
            words = [alts[0] for alts in question.blanks()] + list(question.distractors)
            rng.shuffle(words)
            public["bank"] = words

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


_CHECKERS = {
    "single": _check_single,
    "multiple": _check_multiple,
    "truefalse": _check_truefalse,
    "text": _check_text,
    "number": _check_number,
    "order": _check_order,
    "match": _check_match,
    "blank": _check_blank,
}


# ---------------------------------------------------------------- the correct answer, for the reveal


def _reveal_choices(pres: Presentation) -> dict[str, Any]:
    return {"correct": [pres.id_to_token[c.id] for c in pres.question.choices if c.correct]}


def _reveal_number(pres: Presentation) -> dict[str, Any]:
    q = pres.question
    value = int(q.answer) if float(q.answer).is_integer() else q.answer
    return {"correct": value, "tolerance": q.tolerance, "unit": q.unit}


_REVEALS = {
    "single": _reveal_choices,
    "multiple": _reveal_choices,
    "truefalse": lambda p: {"correct": p.question.answer},
    "text": lambda p: {"correct": p.question.answers[0], "accepted": list(p.question.answers)},
    "number": _reveal_number,
    "order": lambda p: {"correct": [p.id_to_token[i.id] for i in p.question.items]},
    "match": lambda p: {"correct": {p.id_to_token["L" + x.id]: p.id_to_token["R" + x.id] for x in p.question.pairs}},
    "blank": lambda p: {"correct": [alts[0] for alts in p.question.blanks()]},
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


_SAMPLES = {
    "single": _sample_single,
    "multiple": _sample_multiple,
    "truefalse": lambda p, ok, rng: p.question.answer if ok else not p.question.answer,
    "text": lambda p, ok, rng: p.question.answers[0] if ok else "entah",
    "number": _sample_number,
    "order": _sample_order,
    "match": _sample_match,
    "blank": _sample_blank,
}
