"""Helpers for writing sample quizzes: one short call per question, in the shape the editor stores.

Every sample question has a picture (a 3D sticker or a diagram) and an explanation for a child who gets it
wrong; `game` plays it as one of the subject games (games.py).
"""

from __future__ import annotations


def _extra(question: dict, pic: str | None, why: str) -> dict:
    """Every sample question has a picture (a 3D sticker or a diagram) and an explanation for a child who got it wrong."""
    if pic:
        question["picture"] = pic
    if why:
        question["explain"] = why
    return question


def _single(prompt: str, right: str, *wrong: str, time: int = 20, pic: str | None = None, why: str = "", stickers: dict | None = None) -> dict:
    choices = [{"text": right, "correct": True}] + [{"text": w} for w in wrong]
    for choice in choices:
        if stickers and choice["text"] in stickers:
            choice["sticker"] = stickers[choice["text"]]
    return _extra({"type": "single", "prompt": prompt, "choices": choices, "time_limit": time}, pic, why)


def _multiple(prompt: str, right: list[str], wrong: list[str], time: int = 30, pic: str | None = None, why: str = "", stickers: dict | None = None) -> dict:
    choices = [{"text": r, "correct": True} for r in right] + [{"text": w} for w in wrong]
    for choice in choices:
        if stickers and choice["text"] in stickers:
            choice["sticker"] = stickers[choice["text"]]
    return _extra({"type": "multiple", "prompt": prompt, "choices": choices, "time_limit": time}, pic, why)


def _tf(prompt: str, answer: bool, time: int = 15, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "truefalse", "prompt": prompt, "answer": answer, "time_limit": time}, pic, why)


def _text(prompt: str, *answers: str, time: int = 30, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "text", "prompt": prompt, "answers": list(answers), "time_limit": time}, pic, why)


def _number(prompt: str, answer: float, unit: str = "", time: int = 25, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "number", "prompt": prompt, "answer": answer, "unit": unit, "time_limit": time}, pic, why)


def _order(prompt: str, *items: str, time: int = 40, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "order", "prompt": prompt, "items": [{"text": i} for i in items], "time_limit": time}, pic, why)


def _match(prompt: str, pairs: list[tuple], time: int = 45, pic: str | None = None, why: str = "") -> dict:
    """pairs: (left, right) or (left, right, sticker for the left)"""
    rows = [{"left": p[0], "right": p[1], **({"sticker": p[2]} if len(p) > 2 else {})} for p in pairs]
    return _extra({"type": "match", "prompt": prompt, "pairs": rows, "time_limit": time}, pic, why)


def _blank(prompt: str, sentence: str, *distractors: str, time: int = 30, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "blank", "prompt": prompt, "sentence": sentence, "distractors": list(distractors), "time_limit": time}, pic, why)


def _count(prompt: str, sticker: str, place: str, answer: int, time: int = 45, why: str = "") -> dict:
    return _extra({"type": "count", "prompt": prompt, "sticker": sticker, "place": place, "answer": answer, "time_limit": time}, None, why)


def _spell(prompt: str, word: str, sticker: str | None = None, decoys: int = 0, time: int = 45, why: str = "") -> dict:
    return _extra({"type": "spell", "prompt": prompt, "word": word, "sticker": sticker, "decoys": decoys, "time_limit": time}, None, why)


def _sort(prompt: str, groups: list[tuple[str, str | None, list[tuple[str, str | None]]]], time: int = 60, pic: str | None = None, why: str = "") -> dict:
    """groups: (name, sticker, [(thing, sticker), ...])"""
    return _extra(
        {
            "type": "sort",
            "prompt": prompt,
            "groups": [{"id": f"g{i}", "name": name, "sticker": sticker} for i, (name, sticker, _) in enumerate(groups)],
            "items": [
                {"text": text, "sticker": thing, "group": f"g{i}"} for i, (_, _, things) in enumerate(groups) for text, thing in things
            ],
            "time_limit": time,
        },
        pic,
        why,
    )


def _missing(prompt: str, word: str, hide: list[int], sticker: str | None = None, decoys: int = 2, time: int = 45, why: str = "") -> dict:
    return _extra({"type": "missing", "prompt": prompt, "word": word, "hide": hide, "sticker": sticker, "decoys": decoys, "time_limit": time}, None, why)


def _puzzle(prompt: str, sticker: str, grid: int = 2, time: int = 60, why: str = "") -> dict:
    return _extra({"type": "puzzle", "prompt": prompt, "sticker": sticker, "grid": grid, "time_limit": time}, None, why)


def _blocks(prompt: str, answer: int, time: int = 60, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "blocks", "prompt": prompt, "answer": answer, "time_limit": time}, pic, why)


def _clock(prompt: str, hour: int, minute: int = 0, time: int = 45, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "clock", "prompt": prompt, "hour": hour, "minute": minute, "time_limit": time}, pic, why)


def _money(prompt: str, amount: int, sticker: str | None = None, time: int = 60, why: str = "") -> dict:
    return _extra({"type": "money", "prompt": prompt, "amount": amount, "sticker": sticker, "time_limit": time}, None, why)


def _diagram(prompt: str, diagram: str, spots: list[tuple[float, float, str]], time: int = 75, why: str = "") -> dict:
    """spots: (x, y, label), in percent of the diagram from the top left"""
    rows = [{"x": x, "y": y, "label": label} for x, y, label in spots]
    return _extra({"type": "diagram", "prompt": prompt, "diagram": diagram, "spots": rows, "time_limit": time}, None, why)


def play(game: str, question: dict) -> dict:
    """The question, played as a subject game."""
    question["game"] = game
    return question
