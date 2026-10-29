"""A public server: safe defaults, the check before it starts, its headers, health and backups."""

from __future__ import annotations

import dataclasses
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from didik_live import backup
from didik_live.app import create_app
from didik_live.config import MailSettings, Settings, load_settings
from didik_live.mailer import Mailer

ENV = ("DIDIK_ENV", "DIDIK_PUBLIC_URL", "DIDIK_SEED_DEMO", "DIDIK_ALLOW_BOTS", "DIDIK_SECURE_COOKIES", "DIDIK_DATA_DIR", "DIDIK_WEB_DIR", "DIDIK_DATABASE_URL", "DIDIK_SMTP_HOST")


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> pytest.MonkeyPatch:
    for name in ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DIDIK_DATA_DIR", str(tmp_path / "data"))
    web = tmp_path / "web"
    web.mkdir()
    (web / "200.html").write_text("<!doctype html><title>DIDIK</title>", encoding="utf-8")
    monkeypatch.setenv("DIDIK_WEB_DIR", str(web))
    return monkeypatch


def test_localhost_defaults_stay_friendly(env: pytest.MonkeyPatch) -> None:
    settings = load_settings()
    assert not settings.production
    assert settings.seed_demo and settings.allow_bots and not settings.secure_cookies
    assert settings.problems() == []


def test_production_defaults_are_safe(env: pytest.MonkeyPatch) -> None:
    env.setenv("DIDIK_ENV", "production")
    env.setenv("DIDIK_PUBLIC_URL", "https://didik.contoh.my/")
    settings = load_settings()
    assert settings.production
    assert not settings.seed_demo and not settings.allow_bots and settings.secure_cookies
    assert settings.public_url == "https://didik.contoh.my"
    assert settings.problems() == []
    assert any("SMTP" in w for w in settings.warnings())


@pytest.mark.parametrize(
    ("setting", "value", "says"),
    [
        ("DIDIK_PUBLIC_URL", "", "DIDIK_PUBLIC_URL mesti ditetapkan"),
        ("DIDIK_PUBLIC_URL", "http://didik.contoh.my", "https://"),
        ("DIDIK_SEED_DEMO", "1", "DIDIK_SEED_DEMO"),
        ("DIDIK_SECURE_COOKIES", "0", "DIDIK_SECURE_COOKIES"),
    ],
)
def test_production_refuses_unsafe_settings(env: pytest.MonkeyPatch, setting: str, value: str, says: str) -> None:
    env.setenv("DIDIK_ENV", "production")
    env.setenv("DIDIK_PUBLIC_URL", "https://didik.contoh.my")
    env.setenv(setting, value)
    assert any(says in problem for problem in load_settings().problems())


def test_production_needs_the_built_web(env: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env.setenv("DIDIK_ENV", "production")
    env.setenv("DIDIK_PUBLIC_URL", "https://didik.contoh.my")
    env.setenv("DIDIK_WEB_DIR", str(tmp_path / "missing"))
    assert any("npm run build" in problem for problem in load_settings().problems())


def test_https_only_header_on_a_public_server(settings: Settings) -> None:
    with TestClient(create_app(settings)) as local:
        assert "strict-transport-security" not in local.get("/api/health").headers
    public = dataclasses.replace(settings, production=True, seed_demo=False, public_url="https://didik.contoh.my")
    with TestClient(create_app(public)) as client:
        response = client.get("/api/health")
        assert response.headers["strict-transport-security"].startswith("max-age=31536000")


def test_health_answers_for_the_database(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["database"] is True
    assert response.headers["cache-control"] == "no-store"


def test_backup_copies_the_database_and_pictures(env: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = tmp_path / "data"
    (data / "uploads").mkdir(parents=True)
    (data / "uploads" / "a.webp").write_bytes(b"RIFF....WEBP")
    with sqlite3.connect(data / "didik-live.db") as db:
        db.execute("CREATE TABLE t (x)")
        db.execute("INSERT INTO t VALUES (42)")
    folder = tmp_path / "backups"
    made = backup.backup(folder, keep=2)
    copy = next(p for p in made if p.suffix == ".db")
    with sqlite3.connect(copy) as db:
        assert db.execute("SELECT x FROM t").fetchone() == (42,)
    assert any(p.name.endswith(".tar.gz") for p in made)
    # only the newest `keep` are kept
    for i in range(3):
        (folder / f"didik-live-2000010{i}-000000.db").write_bytes(b"")
    backup.backup(folder, keep=2)
    assert len(list(folder.glob("didik-live-*.db"))) == 2


def test_mail_id_uses_the_bare_domain(monkeypatch: pytest.MonkeyPatch) -> None:
    sent = {}

    class FakeSMTP:
        def __init__(self, *_args, **_kwargs) -> None: ...
        def __enter__(self):
            return self
        def __exit__(self, *_exc) -> None: ...
        def starttls(self, **_kwargs) -> None: ...
        def send_message(self, message) -> None:
            sent["id"] = message["Message-ID"]

    monkeypatch.setattr("smtplib.SMTP", FakeSMTP)
    mail = MailSettings(host="smtp.contoh.my", port=587, user="", password="", security="starttls", sender="DIDIK <no-reply@contoh.my>")
    Mailer(mail).send("ibu@contoh.my", "Ujian", "Hai")
    assert sent["id"].endswith("@contoh.my>")


def test_public_server_still_has_the_sample_quizzes(settings: Settings) -> None:
    from didik_live.models import PasswordReset
    from didik_live.seed import LIBRARY_EMAIL, SAMPLES

    public = dataclasses.replace(settings, seed_demo=False)
    app = create_app(public)
    with TestClient(app) as client:
        # a new parent sees every sample quiz
        signed = client.post("/api/auth/register", json={"name": "Cikgu Aminah", "email": "aminah@contoh.my", "password": "rahsia-yang-panjang"})
        assert signed.status_code == 201, signed.text
        samples = client.get("/api/quizzes").json()["samples"]
        assert len(samples) == len(SAMPLES)
        client.post("/api/auth/logout")
        # nobody signs in as their owner, and no reset link is made for it
        assert client.post("/api/auth/login", json={"email": LIBRARY_EMAIL, "password": "!"}).status_code == 422
        assert client.post("/api/auth/forgot", json={"email": LIBRARY_EMAIL}).status_code == 202
        with app.state.db.sessions() as db:
            assert db.query(PasswordReset).count() == 0
    # a restart adds nothing twice
    with TestClient(create_app(public)) as client:
        client.post("/api/auth/login", json={"email": "aminah@contoh.my", "password": "rahsia-yang-panjang"})
        assert len(client.get("/api/quizzes").json()["samples"]) == len(SAMPLES)
