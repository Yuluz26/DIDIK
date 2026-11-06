"""The subject games: thirty-six ways to answer a question, twelve for each of Sains, Sejarah and
Pendidikan Islam (Tahun 1 to Tingkatan 5). A game is a look and a way of playing laid over a question
type: Makmal Ramuan is a "pick the right ones" question answered by pouring bottles into a beaker, Gali
Artifak is a "pick one" question whose choices are dug out of the ground. So a question is still
checked by its type; the game only changes how a child answers it.

The web keeps the same keys, with the pictures and the play, in web/src/lib/subjects/games.ts; a test
keeps the two lists the same.
"""

from __future__ import annotations

from typing import TypedDict


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


def check_game(game: str | None, qtype: str) -> str | None:
    if game in (None, ""):
        return None
    spec = GAMES.get(game)
    if spec is None:
        raise ValueError("Permainan tidak dikenali.")
    if qtype not in spec["types"]:
        raise ValueError(f"{spec['title']} tidak sesuai untuk jenis soalan ini.")
    return game
