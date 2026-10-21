"""Avatars, suggested nicknames, room words and the nickname filter.

Children pick a suggested nickname by default ("Kancil Ceria"), so no real name has to be typed.
A host can allow typed nicknames; those pass through the filter below first.
"""

from __future__ import annotations

import random
import re
import unicodedata

ANIMALS = {
    "kancil": "Kancil",
    "harimau": "Harimau",
    "penyu": "Penyu",
    "enggang": "Enggang",
    "gajah": "Gajah",
    "kucing": "Kucing",
    "arnab": "Arnab",
    "beruang": "Beruang",
}

COLOURS = ["jingga", "kuning", "hijau", "biru", "ungu", "merah", "jambu", "teal"]

SKINS = ["s1", "s2", "s3", "s4", "s5"]

ADJECTIVES = [
    "Ceria", "Pantas", "Bijak", "Riang", "Berani", "Comel", "Lincah", "Gagah", "Tenang", "Ajaib",
    "Cergas", "Hebat", "Pelangi", "Kilat", "Mentari", "Lucu", "Rajin", "Bintang", "Sopan", "Tangkas",
]

SLUG_ANIMALS = [
    "harimau", "kancil", "penyu", "enggang", "gajah", "kucing", "arnab", "beruang",
    "rusa", "tupai", "katak", "merak", "helang", "ikan", "siput", "tenuk",
]
SLUG_COLOURS = ["merah", "jingga", "kuning", "hijau", "biru", "ungu", "emas", "perak", "putih", "nila", "coklat", "jambu"]

# Matched after folding look-alike characters. Longer words match inside other words; the short
# ones only as whole words, so that ordinary names containing those letters still pass.
_BLOCK_INSIDE = [
    "pukimak", "kimak", "puki", "pantat", "butoh", "konek", "lancau", "sundal", "jalang", "haramjadah",
    "bangsat", "keparat", "pepek", "pondan", "bohsia", "gampang", "lahanat", "burit", "cibai", "kanina",
    "pundek", "lanjiao", "bangang", "celaka", "fuck", "shit", "bitch", "cunt", "pussy", "asshole",
    "bastard", "slut", "whore", "nigger", "nigga", "faggot", "retard", "porn", "penis", "vagina",
]
_BLOCK_WORD = ["babi", "bodoh", "sial", "tetek", "bapuk", "mampus", "kote", "dick", "sex", "seks", "fag", "nude", "bogel"]
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "!": "i"})
_NAME_CHARS = re.compile(r"^[\w ]+$", re.UNICODE)


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower().translate(_LEET))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"(.)\1+", r"\1", text)


# Folded the same way as the names they are compared with ("asshole" becomes "ashole").
_BLOCK_INSIDE = [_fold(word) for word in _BLOCK_INSIDE]
_BLOCK_WORD = [_fold(word) for word in _BLOCK_WORD]


def is_rude(name: str) -> bool:
    folded = _fold(name)
    squashed = re.sub(r"[^a-z]", "", folded)
    if any(word in squashed for word in _BLOCK_INSIDE):
        return True
    words = set(re.findall(r"[a-z]+", folded))
    return any(word in words or word == squashed for word in _BLOCK_WORD)


def clean_nickname(raw: str) -> str | None:
    """Returns a tidy nickname, or None when it is empty, too long, oddly built or rude."""
    name = re.sub(r"\s+", " ", unicodedata.normalize("NFC", raw or "")).strip()
    if not 2 <= len(name) <= 16 or not _NAME_CHARS.match(name) or "_" in name:
        return None
    if is_rude(name):
        return None
    return name


def suggest(animal: str, rng: random.Random, taken: set[str] | None = None) -> str:
    base = ANIMALS.get(animal, "Kancil")
    taken = {t.lower() for t in (taken or set())}
    adjectives = ADJECTIVES[:]
    rng.shuffle(adjectives)
    for adjective in adjectives:
        name = f"{base} {adjective}"
        if name.lower() not in taken:
            return name
    return f"{base} {rng.randint(10, 99)}"


def unique(name: str, taken: set[str]) -> str:
    lowered = {t.lower() for t in taken}
    if name.lower() not in lowered:
        return name
    for number in range(2, 100):
        candidate = f"{name[:13]} {number}"
        if candidate.lower() not in lowered:
            return candidate
    return name


def room_slug(rng: random.Random) -> str:
    return f"{rng.choice(SLUG_ANIMALS)}-{rng.choice(SLUG_COLOURS)}-{rng.randint(10, 99)}"


def room_code(rng: random.Random) -> str:
    return f"{rng.randint(100000, 999999)}"
