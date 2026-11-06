"""The subject games: thirty-six ways to answer a question, twelve for each of Sains, Sejarah and
Pendidikan Islam (Tahun 1 to Tingkatan 5). A game is a look and a way of playing laid over a question
type: Makmal Ramuan is a "pick the right ones" question answered by pouring bottles into a beaker, Gali
Artifak is a "pick one" question whose choices are dug out of the ground. So a question is still
checked by its type; the game only changes how a child answers it.

The web keeps the same keys, with the pictures and the play, in web/src/lib/subjects/games.ts; a test
keeps the two lists the same.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, TypedDict


class Game(TypedDict):
    subject: str
    title: str
    types: tuple[str, ...]


SUBJECTS = {"sains": "Sains", "sejarah": "Sejarah", "islam": "Pendidikan Islam"}


def _g(subject: str, title: str, *types: str) -> Game:
    return {"subject": subject, "title": title, "types": types}


GAMES: dict[str, Game] = {
    # Sains
    "ramuan": _g("sains", "Makmal Ramuan", "single", "multiple"),
    "teropong": _g("sains", "Teropong Angkasa", "single"),
    "orbit": _g("sains", "Orbit Planet", "order"),
    "tubuh": _g("sains", "Tubuh Manusia", "diagram"),
    "rantai": _g("sains", "Rantai Makanan", "order"),
    "litar": _g("sains", "Litar Elektrik", "single"),
    "magnet": _g("sains", "Magnet Ajaib", "sort"),
    "jirim": _g("sains", "Balang Jirim", "sort"),
    "kitaran": _g("sains", "Roda Kitaran", "order"),
    "mikroskop": _g("sains", "Mikroskop", "diagram"),
    "unsur": _g("sains", "Jadual Berkala", "match"),
    "alat": _g("sains", "Alat Pengukur", "number"),
    # Sejarah
    "gali": _g("sejarah", "Gali Artifak", "single"),
    "empayar": _g("sejarah", "Bina Empayar", "order"),
    "garismasa": _g("sejarah", "Garis Masa", "order"),
    "peta": _g("sejarah", "Peta Nusantara", "diagram"),
    "muzium": _g("sejarah", "Kurator Muzium", "sort"),
    "skrol": _g("sejarah", "Skrol Purba", "blank"),
    "pelabuhan": _g("sejarah", "Pelabuhan Melaka", "match"),
    "siapa": _g("sejarah", "Siapakah Aku?", "single"),
    "istana": _g("sejarah", "Hierarki Istana", "order"),
    "arkib": _g("sejarah", "Arkib Negara", "truefalse"),
    "mesinmasa": _g("sejarah", "Mesin Masa", "number"),
    "mesintaip": _g("sejarah", "Mesin Taip Merdeka", "text"),
    # Pendidikan Islam
    "tajwid": _g("islam", "Warna Tajwid", "sort"),
    "hijaiyah": _g("islam", "Huruf Hijaiyah", "single"),
    "wuduk": _g("islam", "Langkah Wuduk", "order"),
    "solat": _g("islam", "Gerakan Solat", "order"),
    "kiblat": _g("islam", "Kompas Kiblat", "single"),
    "waktu": _g("islam", "Langit Waktu Solat", "match"),
    "rukun": _g("islam", "Tiang Rukun", "multiple"),
    "timbangan": _g("islam", "Neraca Amal", "sort"),
    "hijrah": _g("islam", "Peta Hijrah", "order"),
    "malaikat": _g("islam", "Lentera Tugas", "match"),
    "zakat": _g("islam", "Tabung Zakat", "money"),
    "kafilah": _g("islam", "Kafilah Sirah", "single", "truefalse"),
}


# A subject's Kuiz Interaktif (Makmal Sains, Ekspedisi Sejarah, Cahaya Ilmu) plays any quiz with that
# subject's games: each question is dealt a game of its type, the least used so far, so a quiz gets as
# many different games as it can. Most games suit anything of their type. A few need their own kind of
# content and are dealt only when the question has it (`_suits`): Arabic letters for Huruf Hijaiyah and
# Warna Tajwid, solat movements for Gerakan Solat, prayer names for Langit Waktu Solat, a reading the
# instrument can show for Alat Pengukur and Mesin Masa, the right kind of picture for the diagram games.
# Rantai Makanan always says "dimakan oleh", so it is never dealt; a question written for it keeps it.
DEALT: dict[str, dict[str, tuple[str, ...]]] = {
    "sains": {
        "single": ("ramuan", "teropong", "litar"),
        "multiple": ("ramuan",),
        "order": ("kitaran", "orbit"),
        "sort": ("jirim", "magnet"),
        "match": ("unsur",),
        "number": ("alat",),
        "diagram": ("tubuh", "mikroskop"),
    },
    "sejarah": {
        "single": ("gali", "siapa"),
        "order": ("garismasa", "empayar", "istana"),
        "diagram": ("peta",),
        "sort": ("muzium",),
        "blank": ("skrol",),
        "match": ("pelabuhan",),
        "truefalse": ("arkib",),
        "number": ("mesinmasa",),
        "text": ("mesintaip",),
    },
    "islam": {
        "single": ("kiblat", "kafilah", "hijaiyah"),
        "multiple": ("rukun",),
        "order": ("hijrah", "wuduk", "solat"),
        "sort": ("timbangan", "tajwid"),
        "match": ("malaikat", "waktu"),
        "money": ("zakat",),
        "truefalse": ("kafilah",),
    },
}

_ARABIC = re.compile(r"[؀-ۿ]")
_POSE = re.compile(r"takbir|rukuk|ruku'|iktidal|i'tidal|sujud|salam|duduk|tahiyat|tasyahhud|qiam|berdiri", re.I)
_PRAYER = re.compile(r"subuh|syuruk|dhuha|duha|zohor|zuhur|asar|maghrib|isyak|isya|tahajud|witir", re.I)
_BODY = {"rajah-organ", "rajah-cerna", "rajah-rangka"}
_PLACES = {"rajah-malaysia", "rajah-semenanjung", "rajah-arab", "rajah-afamosa", "rajah-lembah-bujang", "rajah-gua-niah", "rajah-jalur"}


def _instrument(unit: str) -> tuple[float, float, float]:
    """The scale Alat Pengukur shows for a unit (min, max, step), as web/src/lib/subjects/sains/Alat.svelte."""
    u = unit.strip().lower()
    if u.endswith("c") or "celsius" in u:
        return (-10, 110, 1)
    return {
        "ml": (0, 1000, 10),
        "l": (0, 10, 0.5),
        "liter": (0, 10, 0.5),
        "litre": (0, 10, 0.5),
        "cm": (0, 30, 0.5),
        "mm": (0, 300, 1),
        "m": (0, 100, 1),
        "kg": (0, 100, 0.5),
        "g": (0, 1000, 10),
    }.get(u, (0, 1000, 1))


def _suits(game: str, question: Any) -> bool:
    if game == "hijaiyah":
        return all(_ARABIC.search(c.text) for c in question.choices)
    if game == "tajwid":
        return all(_ARABIC.search(i.text) for i in question.items)
    if game == "solat":
        return all(_POSE.search(i.text) for i in question.items)
    if game == "waktu":
        return all(_PRAYER.search(p.left) for p in question.pairs)
    if game == "alat":
        low, high, step = _instrument(question.unit)
        answer = float(question.answer)
        return low <= answer <= high and abs(answer / step - round(answer / step)) < 1e-9
    if game == "mesinmasa":
        answer = float(question.answer)
        return answer == int(answer) and 0 <= answer <= 9999
    if game == "tubuh":
        return question.diagram in _BODY
    if game == "mikroskop":
        return question.diagram.startswith("rajah-sel")
    if game == "peta":
        return question.diagram in _PLACES
    return True


def deal_games(subject: str, questions: list[Any]) -> list[str | None]:
    """The game each question is played as in this subject's Kuiz Interaktif, in trail order. A question
    written for one of this subject's games keeps it; a question nothing suits is played the plain way."""
    used: Counter[str] = Counter()
    dealt: list[str | None] = []
    for question in questions:
        if question.game and GAMES[question.game]["subject"] == subject:
            pick: str | None = question.game
        else:
            options = [g for g in DEALT[subject].get(question.type, ()) if _suits(g, question)]
            pick = min(options, key=lambda g: (used[g], options.index(g))) if options else None
        if pick:
            used[pick] += 1
        dealt.append(pick)
    return dealt


def check_game(game: str | None, qtype: str) -> str | None:
    if game in (None, ""):
        return None
    spec = GAMES.get(game)
    if spec is None:
        raise ValueError("Permainan tidak dikenali.")
    if qtype not in spec["types"]:
        raise ValueError(f"{spec['title']} tidak sesuai untuk jenis soalan ini.")
    return game
