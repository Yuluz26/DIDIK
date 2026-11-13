"""The diagrams and photographs a question can show, or have labelled (the "Label rajah" type): a body with
its organs, cells, the water cycle, maps of Malaysia and Arabia, the solar system, a volcano, and photos
of A Famosa, the Kaabah, Lembah Bujang and Gua Niah. Each key is a picture in web/static/rajah/<key>.webp,
from Wikimedia Commons under a free licence (public domain, CC0, CC BY or CC BY-SA; who made each one is
in web/static/rajah/CREDITS.txt and shown under the picture).

The web keeps the same keys, with names and sizes, in web/src/lib/diagrams.ts; a test keeps the two lists
the same. Only these keys are accepted, so a question can never point at some other file.
"""

from __future__ import annotations

DIAGRAMS: frozenset[str] = frozenset(
    """
    rajah-organ rajah-cerna rajah-sel-haiwan rajah-sel-pokok rajah-sel-bawang rajah-kitaran-air rajah-rangka
    rajah-malaysia rajah-semenanjung rajah-arab rajah-jalur rajah-suria rajah-gunung-berapi
    rajah-afamosa rajah-kaabah rajah-lembah-bujang rajah-gua-niah
    rajah-number-line rajah-letters rajah-gajah-asia
    """.split()
)


def check_diagram(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    if value not in DIAGRAMS:
        raise ValueError("Rajah tidak dikenali.")
    return value
