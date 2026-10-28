from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from didik_live.app import create_app
from didik_live.config import Settings
from didik_live.game.modes.base import BaseMode
from didik_live.seed import DEMO_EMAIL, DEMO_PASSWORD


@pytest.fixture(autouse=True)
def quick_intros(monkeypatch: pytest.MonkeyPatch) -> None:
    """The 4-second "Bersedia!" countdown is for children, not for tests."""
    monkeypatch.setattr(BaseMode, "intro_seconds", 0.2)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path,
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        web_dir=tmp_path / "no-web",
        secure_cookies=False,
        allow_bots=True,
        seed_demo=True,
        demo_local_only=False,
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def parent(client: TestClient) -> TestClient:
    response = client.post("/api/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    assert response.status_code == 200, response.text
    return client


def wait_until(check: Callable[[], bool], timeout: float = 5.0) -> None:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if check():
            return
        time.sleep(0.02)
    raise AssertionError("condition not reached in time")


def sample_id(client: TestClient, title: str) -> int:
    quizzes = client.get("/api/quizzes").json()
    for quiz in quizzes["mine"] + quizzes["samples"]:
        if quiz["title"] == title:
            return quiz["id"]
    raise AssertionError(f"no quiz {title}")
