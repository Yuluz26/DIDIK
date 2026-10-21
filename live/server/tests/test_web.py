"""Serving the built web app: the page's inline scripts are allowed by hash, and a new build is
picked up without restarting the server."""

from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from didik_live.app import create_app
from didik_live.config import Settings


def page(script: str) -> str:
    return f"<!doctype html><html><body><script>{script}</script></body></html>"


def allowed(script: str) -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(script.encode()).digest()).decode() + "'"


def test_a_new_build_is_served_with_a_policy_that_matches_it_on_the_first_request(settings: Settings, tmp_path: Path) -> None:
    web = tmp_path / "web"
    web.mkdir()
    shell = web / "200.html"
    shell.write_text(page("start(1)"), encoding="utf-8")
    with TestClient(create_app(replace(settings, web_dir=web))) as client:
        first = client.get("/ibu-bapa")
        assert "start(1)" in first.text
        assert allowed("start(1)") in first.headers["content-security-policy"]

        shell.write_text(page("start(2)"), encoding="utf-8")
        later = os.stat(shell).st_mtime + 5
        os.utime(shell, (later, later))

        rebuilt = client.get("/ibu-bapa")
        assert "start(2)" in rebuilt.text
        policy = rebuilt.headers["content-security-policy"]
        assert allowed("start(2)") in policy and allowed("start(1)") not in policy
