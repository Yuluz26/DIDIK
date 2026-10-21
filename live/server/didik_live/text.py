"""Comparing typed answers the way a patient teacher would: ignore case, accents, spacing and
punctuation, and forgive one slip of the finger in longer words."""

from __future__ import annotations

import re
import unicodedata

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = _PUNCT.sub(" ", text.lower())
    return _SPACE.sub(" ", text).strip()


def distance(a: str, b: str, limit: int = 2) -> int:
    """Edit distance where swapping two neighbouring letters ("hijua") counts as one slip
    (optimal string alignment), stopping early once it is certainly above `limit`."""
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    before: list[int] = []
    previous = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        current = [i]
        for j in range(1, len(b) + 1):
            value = min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (a[i - 1] != b[j - 1]))
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                value = min(value, before[j - 2] + 1)
            current.append(value)
        if min(current) > limit:
            return limit + 1
        before, previous = previous, current
    return previous[-1]


def matches(given: str, accepted: list[str], forgive_typo: bool = True) -> bool:
    answer = normalize(given)
    if not answer:
        return False
    for option in accepted:
        target = normalize(option)
        if answer == target or answer.replace(" ", "") == target.replace(" ", ""):
            return True
        if forgive_typo and len(target) >= 4 and distance(answer, target, 1) <= 1:
            return True
    return False


def parse_number(text: str | int | float) -> float | None:
    """Accepts 7, "7", "3,5" and "3.5"; returns None for anything that is not one number."""
    if isinstance(text, bool):
        return None
    if isinstance(text, (int, float)):
        return float(text)
    cleaned = text.strip().replace(" ", "").replace(",", ".")
    if not re.fullmatch(r"-?\d+(\.\d+)?", cleaned):
        return None
    return float(cleaned)
