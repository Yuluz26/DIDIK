"""The 3D stickers: the server's list, the web's list and the pictures themselves stay the same set."""

from __future__ import annotations

import re
from pathlib import Path

from didik_live.stickers import PLACES, STICKERS

WEB = Path(__file__).resolve().parents[2] / "web"


def web_keys() -> set[str]:
    source = (WEB / "src" / "lib" / "stickers.ts").read_text(encoding="utf-8")
    # every "key=Name" pair inside the S(...) lists
    return set(re.findall(r"(?:'|,\s*)([a-z][a-z-]*)=", source))


def test_web_and_server_know_the_same_stickers() -> None:
    assert web_keys() == STICKERS


def test_every_sticker_has_its_picture_and_the_licence_is_beside_them() -> None:
    folder = WEB / "static" / "pelekat"
    assert {p.stem for p in folder.glob("*.webp")} == STICKERS
    assert "MIT License" in (folder / "LICENSE.txt").read_text(encoding="utf-8")


def test_places_are_stickers_and_match_the_web() -> None:
    assert PLACES <= STICKERS
    source = (WEB / "src" / "lib" / "stickers.ts").read_text(encoding="utf-8")
    block = source.split("export const PLACES", 1)[1].split("];", 1)[0]
    assert set(re.findall(r"key: '([a-z-]+)'", block)) == PLACES
