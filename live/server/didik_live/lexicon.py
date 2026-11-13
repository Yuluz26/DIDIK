"""What the words of an answer are, for the subject games.

A subject game shows real things: Teropong Angkasa shows Mars when an answer says "Marikh", Litar Elektrik
lights its bulb only for something that conducts. So both sides need to know what an answer's words mean:
the server, to give a game only to a question it suits (games.py), and the web, to show the right picture
and behave the right way. This file is that knowledge, once. The web reads the copy written by

    python -m didik_live.lexicon

into web/src/lib/subjects/lexicon.gen.json; a test keeps the copy the same as this file.

Each entry: the picture it shows (a key of web/static/game-assets, or None), the words that mean it (Malay
first, as a child would read them; a few English and older spellings), its name, and what the games need
to know about it. Words are matched whole and without regard to case; the first entry that matches wins,
so the more particular entries come first.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------- the sky (Teropong Angkasa, Orbit Planet)
# order: place from the Sun (planets only). kind: what it is, said under the eyepiece.
SPACE: list[dict[str, Any]] = [
    {"key": "space/milkyway-core", "words": "bima sakti|milky way", "name": "Bima Sakti", "kind": "galaksi", "wide": True},
    {"key": "space/andromeda", "words": "andromeda", "name": "Galaksi Andromeda", "kind": "galaksi"},
    {"key": "space/sombrero", "words": "sombrero", "name": "Galaksi Sombrero", "kind": "galaksi", "wide": True},
    {"key": "space/lmc", "words": "awan magellan besar|awan magellan|magellan", "name": "Awan Magellan Besar", "kind": "galaksi"},
    {"key": "space/polaris", "words": "bintang utara|bintang kutub|polaris", "name": "Bintang Utara", "kind": "bintang"},
    {"key": "space/comet", "words": "komet halley|komet|comet", "name": "Komet", "kind": "komet", "wide": True},
    {"key": "space/sun", "words": "matahari|suria", "name": "Matahari", "kind": "bintang", "order": 0},
    {"key": "space/mercury", "words": "utarid|merkuri|merkurius|mercury", "name": "Utarid", "kind": "planet", "order": 1},
    {"key": "space/venus", "words": "zuhrah|venus|kejora", "name": "Zuhrah", "kind": "planet", "order": 2},
    {"key": "space/earth", "words": "bumi", "name": "Bumi", "kind": "planet", "order": 3},
    {"key": "space/mars", "words": "marikh|mars", "name": "Marikh", "kind": "planet", "order": 4},
    {"key": "space/jupiter", "words": "musytari|jupiter", "name": "Musytari", "kind": "planet", "order": 5},
    {"key": "space/saturn", "words": "zuhal|saturnus|saturn", "name": "Zuhal", "kind": "planet", "order": 6, "wide": True},
    {"key": "space/uranus", "words": "uranus", "name": "Uranus", "kind": "planet", "order": 7},
    {"key": "space/neptune", "words": "neptun|neptune", "name": "Neptun", "kind": "planet", "order": 8},
    {"key": "space/moon", "words": "bulan", "name": "Bulan", "kind": "satelit semula jadi"},
    {"key": "space/star", "words": "sirius|bintang", "name": "Bintang", "kind": "bintang"},
]



def _m(key: str | None, words: str, name: str, conducts: bool | None, magnetic: bool | None, state: str) -> dict[str, Any]:
    return {"key": key, "words": words, "name": name, "conducts": conducts, "magnetic": magnetic, "state": state}


# ---------------------------------------------------------------- materials (Litar Elektrik, Magnet Ajaib, Balang Jirim)
# conducts: lets an electric current through (a bulb in series lights). magnetic: pulled by a magnet (iron,
# steel, nickel, cobalt). None where it depends on what the thing is made of (a coin, a spoon) or on what
# is dissolved in it (water): the games are not given a question that turns on such a thing.
# state: at room temperature.
MATERIALS: list[dict[str, Any]] = [
    _m(None, "oksigen|nitrogen|karbon dioksida|hidrogen|helium", "Gas", False, False, "gas"),
    _m("mat/plastic", "[a-z]+ plastik", "Plastik", False, False, "pepejal"),
    _m("mat/wood", "[a-z]+ kayu", "Kayu", False, False, "pepejal"),
    _m("mat/glass", "[a-z]+ kaca", "Kaca", False, False, "pepejal"),
    _m("mat/paper-clip", "klip kertas", "Klip kertas keluli", True, True, "pepejal"),
    _m("mat/key", "kunci besi|kunci keluli|anak kunci besi", "Kunci besi", True, True, "pepejal"),
    _m("mat/key", "anak kunci|kunci", "Kunci logam", True, None, "pepejal"),
    _m("mat/nail", "paku besi|paku|skru|jarum", "Paku besi", True, True, "pepejal"),
    _m("mat/scissors", "gunting", "Gunting keluli", True, True, "pepejal"),
    _m("mat/foil", "kerajang aluminium|tin aluminium|aluminium", "Aluminium", True, False, "pepejal"),
    _m("mat/copper", "wayar kuprum|dawai kuprum|kuprum|tembaga", "Kuprum", True, False, "pepejal"),
    _m("mat/ring", "cincin emas|emas|cincin", "Emas", True, False, "pepejal"),
    _m(None, "perak|argentum", "Perak", True, False, "pepejal"),
    _m(None, "nikel", "Nikel", True, True, "pepejal"),
    _m(None, "kobalt", "Kobalt", True, True, "pepejal"),
    _m("mat/coins", "duit syiling|syiling", "Duit syiling", True, None, "pepejal"),
    _m("mat/spoon", "sudu besi|sudu keluli", "Sudu besi", True, True, "pepejal"),
    _m("mat/spoon", "sudu logam|sudu", "Sudu logam", True, None, "pepejal"),
    _m("mat/pencil", "grafit pensel|grafit|mata pensel", "Grafit", True, False, "pepejal"),
    _m("mat/eraser", "getah pemadam|pemadam", "Pemadam getah", False, False, "pepejal"),
    _m("mat/rubber-band", "gelang getah|getah", "Getah", False, False, "pepejal"),
    _m("mat/wood", "pensel kayu|pembaris kayu|batang aiskrim|kayu|papan", "Kayu", False, False, "pepejal"),
    _m("mat/feather", "bulu ayam|bulu pelepah|bulu", "Bulu", False, False, "pepejal"),
    _m("mat/glass", "gelas kaca|kaca|gelas", "Kaca", False, False, "pepejal"),
    _m("mat/straw", "penyedut minuman|penyedut", "Penyedut plastik", False, False, "pepejal"),
    _m("mat/plastic", "pembaris plastik|botol plastik|plastik", "Plastik", False, False, "pepejal"),
    _m("mat/sponge", "span", "Span", False, False, "pepejal"),
    _m("mat/cotton", "kapas|kain", "Kapas", False, False, "pepejal"),
    _m("mat/rope", "tali|benang", "Tali", False, False, "pepejal"),
    _m("mat/brick", "batu bata|bata", "Batu bata", False, False, "pepejal"),
    _m("mat/pebble", "batu kecil|batu", "Batu", False, False, "pepejal"),
    _m(None, "kertas|kadbod", "Kertas", False, False, "pepejal"),
    _m("mat/nail", "besi|keluli|ferum", "Besi", True, True, "pepejal"),
    _m("mat/ice", "ketulan ais|ais", "Ais", None, False, "pepejal"),
    _m("mat/salt", "natrium klorida|garam", "Garam", None, False, "pepejal"),
    _m("mat/sugar", "gula", "Gula", False, False, "pepejal"),
    _m("mat/mercury", "merkuri|raksa", "Merkuri", True, False, "cecair"),
    _m("mat/milk", "susu", "Susu", None, False, "cecair"),
    _m("mat/oil", "minyak masak|minyak", "Minyak", False, False, "cecair"),
    _m("mat/honey", "madu", "Madu", None, False, "cecair"),
    _m("mat/steam", "wap air|wap|stim", "Wap air", None, False, "gas"),
    _m("mat/balloon", "udara dalam belon|udara|belon", "Udara", False, False, "gas"),
    _m("mat/smoke", "asap", "Asap", None, False, "gas"),
    _m("mat/water", "air", "Air", None, False, "cecair"),
]



def _l(key: str | None, words: str, name: str, home: str = "darat") -> dict[str, Any]:
    return {"key": key, "words": words, "name": name, "home": home}


# ---------------------------------------------------------------- living things (Rantai Makanan)
# home: where the food chain it belongs to is set (darat, laut), for the scene behind the chain.
LIVING: list[dict[str, Any]] = [
    _l("life/phytoplankton", "fitoplankton", "Fitoplankton", "laut"),
    _l("life/zooplankton", "zooplankton", "Zooplankton", "laut"),
    _l("life/seaweed", "rumpai laut|alga", "Rumpai laut", "laut"),
    _l("life/shrimp", "udang", "Udang", "laut"),
    _l("life/squid", "sotong", "Sotong", "laut"),
    _l("life/crab", "ketam", "Ketam", "laut"),
    _l("life/turtle", "penyu", "Penyu", "laut"),
    _l("life/shark", "jerung|yu", "Jerung", "laut"),
    _l("life/fish", "ikan kecil|ikan besar|ikan", "Ikan", "laut"),
    _l("life/rice", "pokok padi|padi", "Padi"),
    _l("life/grass", "rumput", "Rumput"),
    _l("life/leaf", "daun|sayur|kubis|tumbuhan hijau|tumbuhan", "Tumbuhan"),
    _l("life/tree", "pokok", "Pokok"),
    _l("life/flower", "bunga", "Bunga"),
    _l("life/fruit", "buah", "Buah"),
    _l("life/mushroom", "cendawan|kulat", "Cendawan"),
    _l("life/grasshopper", "belalang", "Belalang"),
    _l("life/caterpillar", "ulat beluncas|beluncas|ulat", "Ulat"),
    _l("life/butterfly", "rama-rama|kupu-kupu", "Rama-rama"),
    _l("life/ant", "semut", "Semut"),
    _l("life/bee", "lebah", "Lebah"),
    _l("life/dragonfly", "pepatung", "Pepatung"),
    _l("life/spider", "labah-labah", "Labah-labah"),
    _l("life/worm", "cacing tanah|cacing", "Cacing tanah"),
    _l("life/frog", "katak", "Katak"),
    _l("life/lizard", "cicak|mengkarung", "Cicak"),
    _l("life/mouse", "tikus", "Tikus"),
    _l("life/snake", "ular", "Ular"),
    _l("life/owl", "burung hantu", "Burung hantu"),
    _l("life/eagle", "helang|lang", "Helang"),
    _l("life/chicken", "ayam", "Ayam"),
    _l("life/bat", "kelawar", "Kelawar"),
    _l("life/rabbit", "arnab", "Arnab"),
    _l("life/goat", "kambing", "Kambing"),
    _l("life/cow", "lembu|kerbau", "Lembu"),
    _l("life/tiger", "harimau", "Harimau"),
    _l("life/lion", "singa", "Singa"),
    _l("life/crocodile", "buaya", "Buaya"),
]


def _s(key: str | None, words: str, name: str, cycle: str) -> dict[str, Any]:
    return {"key": key, "words": words, "name": name, "cycle": cycle}


# ---------------------------------------------------------------- stages of a cycle (Roda Kitaran)
# The same word can be a stage of more than one cycle ("telur" of a frog, a butterfly, a hen): the game
# takes the one cycle that every stage of the question belongs to (`cycle_of`).
STAGES: list[dict[str, Any]] = [
    _s("life/frogspawn", "telur katak|telur", "Telur katak", "katak"),
    _s("life/tadpole", "berudu", "Berudu", "katak"),
    _s("life/froglet", "katak muda|anak katak|katak berekor", "Katak muda", "katak"),
    _s("life/frog", "katak dewasa|katak", "Katak dewasa", "katak"),
    _s(None, "telur rama-rama|telur", "Telur", "rama-rama"),
    _s("life/caterpillar", "ulat beluncas|beluncas|ulat|larva", "Ulat beluncas", "rama-rama"),
    _s("life/pupa", "kepompong|pupa", "Kepompong", "rama-rama"),
    _s("life/butterfly", "rama-rama dewasa|rama-rama|kupu-kupu", "Rama-rama", "rama-rama"),
    _s("life/egg", "telur ayam|telur", "Telur", "ayam"),
    _s(None, "anak ayam", "Anak ayam", "ayam"),
    _s("life/chicken", "ayam dewasa|ayam", "Ayam dewasa", "ayam"),
    _s("life/seed", "biji benih|benih", "Biji benih", "tumbuhan"),
    _s("life/seedling", "anak benih|anak pokok|percambahan|bercambah", "Anak benih", "tumbuhan"),
    _s("life/tree", "pokok dewasa|tumbuhan dewasa|pokok", "Pokok dewasa", "tumbuhan"),
    _s("life/flower", "berbunga|bunga", "Berbunga", "tumbuhan"),
    _s("life/fruit", "berbuah|buah", "Berbuah", "tumbuhan"),
    _s("cycle/evaporation", "penyejatan|sejatan", "Sejatan", "air"),
    _s("cycle/cloud", "kondensasi|pemeluwapan|awan", "Kondensasi", "air"),
    _s("cycle/rain", "kerpasan|hujan", "Kerpasan", "air"),
    _s("cycle/river", "air larian ke laut|air larian|larian|sungai|pengumpulan", "Air larian", "air"),
    _s("cycle/sea", "laut", "Laut", "air"),
    _s("moon/new", "bulan baru|anak bulan", "Bulan baru", "bulan"),
    _s("moon/crescent", "bulan sabit", "Bulan sabit", "bulan"),
    _s("moon/quarter", "bulan separa|bulan separuh|suku pertama", "Bulan separa", "bulan"),
    _s("moon/full", "bulan purnama|purnama", "Bulan purnama", "bulan"),
]



def _e(sym: str, name: str, z: int, group: int, period: int, family: str, more: str = "") -> dict[str, Any]:
    return {"key": None, "sym": sym, "words": "|".join(w for w in (name.lower(), more) if w), "name": name, "z": z, "group": group, "period": period, "family": family}


# ---------------------------------------------------------------- elements (Jadual Berkala)
# The elements a pupil meets up to Tingkatan 5, with their real atomic number and place in the table.
# family: logam alkali, logam alkali bumi, logam peralihan, logam lain, separa logam, bukan logam,
# halogen, gas adi. An element is named by its symbol exactly ("Fe", not "fe") or by its Malay name.
ELEMENTS: list[dict[str, Any]] = [
    _e("H", "Hidrogen", 1, 1, 1, "bukan logam"),
    _e("He", "Helium", 2, 18, 1, "gas adi"),
    _e("Li", "Litium", 3, 1, 2, "logam alkali"),
    _e("Be", "Berilium", 4, 2, 2, "logam alkali bumi"),
    _e("B", "Boron", 5, 13, 2, "separa logam"),
    _e("C", "Karbon", 6, 14, 2, "bukan logam"),
    _e("N", "Nitrogen", 7, 15, 2, "bukan logam"),
    _e("O", "Oksigen", 8, 16, 2, "bukan logam"),
    _e("F", "Fluorin", 9, 17, 2, "halogen"),
    _e("Ne", "Neon", 10, 18, 2, "gas adi"),
    _e("Na", "Natrium", 11, 1, 3, "logam alkali", "sodium"),
    _e("Mg", "Magnesium", 12, 2, 3, "logam alkali bumi"),
    _e("Al", "Aluminium", 13, 13, 3, "logam lain"),
    _e("Si", "Silikon", 14, 14, 3, "separa logam"),
    _e("P", "Fosforus", 15, 15, 3, "bukan logam"),
    _e("S", "Sulfur", 16, 16, 3, "bukan logam", "belerang"),
    _e("Cl", "Klorin", 17, 17, 3, "halogen"),
    _e("Ar", "Argon", 18, 18, 3, "gas adi"),
    _e("K", "Kalium", 19, 1, 4, "logam alkali", "potassium"),
    _e("Ca", "Kalsium", 20, 2, 4, "logam alkali bumi"),
    _e("Fe", "Ferum", 26, 8, 4, "logam peralihan", "besi"),
    _e("Co", "Kobalt", 27, 9, 4, "logam peralihan"),
    _e("Ni", "Nikel", 28, 10, 4, "logam peralihan"),
    _e("Cu", "Kuprum", 29, 11, 4, "logam peralihan", "tembaga"),
    _e("Zn", "Zink", 30, 12, 4, "logam peralihan"),
    _e("Br", "Bromin", 35, 17, 4, "halogen"),
    _e("Ag", "Argentum", 47, 11, 5, "logam peralihan", "perak"),
    _e("Sn", "Stanum", 50, 14, 5, "logam lain", "timah"),
    _e("I", "Iodin", 53, 17, 5, "halogen"),
    _e("Au", "Aurum", 79, 11, 6, "logam peralihan", "emas"),
    _e("Hg", "Merkuri", 80, 12, 6, "logam peralihan", "raksa"),
    _e("Pb", "Plumbum", 82, 14, 6, "logam lain"),
]

LEXICON: dict[str, list[dict[str, Any]]] = {
    "space": SPACE,
    "materials": MATERIALS,
    "living": LIVING,
    "stages": STAGES,
    "elements": ELEMENTS,
}


def fold(text: str) -> str:
    """Lower case, without accents or the marks of older spellings ("Qur'an" and "Quran" are the same word)."""
    plain = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in plain if not unicodedata.combining(c))


@lru_cache(maxsize=None)
def _pattern(words: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![a-z0-9])(?:{words})(?![a-z0-9])")


def find(group: str, text: str) -> dict[str, Any] | None:
    """The entry of a group that some words mean, or None."""
    folded = fold(text)
    for entry in LEXICON[group]:
        if _pattern(entry["words"]).search(folded):
            return entry
    return None


def element(text: str) -> dict[str, Any] | None:
    """The element some words name: its symbol exactly, alone or before its name ("Fe", "Fe (ferum)"), or its name."""
    words = text.strip()
    symbol = re.match(r"[A-Z][a-z]?(?![A-Za-z])", words)
    for entry in ELEMENTS:
        if symbol and entry["sym"] == symbol.group(0):
            return entry
    if symbol:
        return None
    return find("elements", words)


STATES = {"pepejal": "pepejal", "cecair": "cecair", "gas": "gas"}


def state_of_group(name: str) -> str | None:
    """Which state of matter a group's name means (Balang Jirim), or None."""
    folded = fold(name)
    for word, state in STATES.items():
        if _pattern(word).search(folded):
            return state
    return None


def pulls(name: str) -> bool | None:
    """Whether a group's name means "pulled by a magnet" (True), "not pulled" (False), or neither (None)."""
    folded = fold(name)
    if not re.search(r"magnet|ditarik|tertarik|melekat", folded):
        return None
    return not re.search(r"(?<![a-z])(tidak|bukan|tak|tiada)(?![a-z])", folded)


def find_all(group: str, text: str) -> list[dict[str, Any]]:
    """Every entry of a group that some words could mean."""
    folded = fold(text)
    return [entry for entry in LEXICON[group] if _pattern(entry["words"]).search(folded)]


def cycle_of(texts: list[str]) -> str | None:
    """The one cycle every one of these stages belongs to (a frog's life, the water cycle), or None."""
    shared: set[str] | None = None
    for text in texts:
        cycles = {entry["cycle"] for entry in find_all("stages", text)}
        shared = cycles if shared is None else shared & cycles
    return sorted(shared)[0] if shared else None


def dump() -> str:
    """The lexicon as the web reads it (stable, so a test can compare it byte for byte)."""
    return json.dumps(LEXICON, ensure_ascii=False, indent=1) + "\n"


WEB_COPY = Path(__file__).resolve().parents[2] / "web" / "src" / "lib" / "subjects" / "lexicon.gen.json"

if __name__ == "__main__":
    WEB_COPY.write_text(dump(), encoding="utf-8", newline="\n")
    sys.stdout.write(f"wrote {WEB_COPY}\n")
