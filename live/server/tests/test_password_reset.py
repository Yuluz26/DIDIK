"""A parent who forgot their password gets a one-time link by email and chooses a new one."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update

from didik_live import passwords
from didik_live.app import create_app
from didik_live.config import MailSettings, Settings
from didik_live.deps import SESSION_COOKIE
from didik_live.mailer import Mailer
from didik_live.models import PasswordReset
from didik_live.seed import DEMO_EMAIL, DEMO_PASSWORD

MAIL = MailSettings(host="smtp.example.test", port=587, user="", password="", security="starttls", sender="didik@example.test")


class Outbox(Mailer):
    """Keeps emails instead of sending them."""

    def __init__(self, ready: bool = True) -> None:
        super().__init__(MAIL if ready else None)
        self.sent: list[tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append((to, subject, body))

    def token(self) -> str:
        to, _, body = self.sent[-1]
        line = next(line for line in body.splitlines() if passwords.RESET_PATH in line)
        return line.split("#", 1)[1]


@pytest.fixture
def site(settings: Settings) -> TestClient:
    app = create_app(replace(settings, public_url="https://didik.example.test"))
    app.state.mailer = Outbox()
    with TestClient(app) as client:
        yield client


def test_a_reset_link_is_emailed_and_sets_a_new_password_once(site: TestClient) -> None:
    outbox: Outbox = site.app.state.mailer
    answer = site.post("/api/auth/forgot", json={"email": " Demo@Didik.test "})
    assert answer.status_code == 202 and "sah selama satu jam" in answer.json()["message"]
    to, subject, body = outbox.sent[-1]
    assert to == DEMO_EMAIL and "kata laluan baharu" in subject
    assert "https://didik.example.test/ibu-bapa/kata-laluan#" in body
    token = outbox.token()

    assert site.post("/api/auth/reset/check", json={"token": token}).json() == {"email": DEMO_EMAIL}
    short = site.post("/api/auth/reset", json={"token": token, "password": "pendek"})
    assert short.status_code == 422
    done = site.post("/api/auth/reset", json={"token": token, "password": "kata-laluan-baharu"})
    assert done.status_code == 200 and done.json()["user"]["email"] == DEMO_EMAIL
    assert site.get("/api/auth/me").json()["user"]["email"] == DEMO_EMAIL  # signed in straight away

    again = site.post("/api/auth/reset", json={"token": token, "password": "satu-lagi-kata-laluan"})
    assert again.status_code == 410 and "Minta pautan baharu" in again.json()["message"]
    site.post("/api/auth/logout")
    assert site.post("/api/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}).status_code == 422
    assert site.post("/api/auth/login", json={"email": DEMO_EMAIL, "password": "kata-laluan-baharu"}).status_code == 200


def test_unknown_emails_get_the_same_answer_and_no_email(site: TestClient) -> None:
    outbox: Outbox = site.app.state.mailer
    known = site.post("/api/auth/forgot", json={"email": DEMO_EMAIL})
    unknown = site.post("/api/auth/forgot", json={"email": "tiada@sesiapa.test"})
    assert unknown.status_code == known.status_code == 202
    assert unknown.json() == known.json()
    assert [to for to, _, _ in outbox.sent] == [DEMO_EMAIL]
    assert site.post("/api/auth/forgot", json={"email": "bukan emel"}).status_code == 422


def test_a_new_link_cancels_the_old_one_and_links_expire(site: TestClient) -> None:
    outbox: Outbox = site.app.state.mailer
    site.post("/api/auth/forgot", json={"email": DEMO_EMAIL})
    first = outbox.token()
    site.post("/api/auth/forgot", json={"email": DEMO_EMAIL})
    second = outbox.token()
    assert site.post("/api/auth/reset/check", json={"token": first}).status_code == 410
    assert site.post("/api/auth/reset/check", json={"token": second}).status_code == 200

    with site.app.state.db.sessions() as db:
        db.execute(update(PasswordReset).values(expires_at=datetime.now(UTC) - timedelta(minutes=1)))
        db.commit()
    assert site.post("/api/auth/reset/check", json={"token": second}).status_code == 410
    assert site.post("/api/auth/reset", json={"token": "x" * 43, "password": "kata-laluan-baharu"}).status_code == 410


def test_a_new_password_signs_out_every_other_device(site: TestClient) -> None:
    assert site.post("/api/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}).status_code == 200
    laptop = site.cookies.get(SESSION_COOKIE)
    site.cookies.clear()  # now on another device
    site.post("/api/auth/forgot", json={"email": DEMO_EMAIL})
    site.post("/api/auth/reset", json={"token": site.app.state.mailer.token(), "password": "kata-laluan-baharu"})
    assert site.get("/api/auth/me").json()["user"]["email"] == DEMO_EMAIL
    site.cookies.clear()
    site.cookies.set(SESSION_COOKIE, laptop)
    assert site.get("/api/auth/me").json()["user"] is None


def test_requests_for_links_are_limited_per_email(site: TestClient) -> None:
    for _ in range(3):
        assert site.post("/api/auth/forgot", json={"email": DEMO_EMAIL}).status_code == 202
    assert site.post("/api/auth/forgot", json={"email": DEMO_EMAIL}).status_code == 429


def test_emailed_links_are_never_built_from_the_host_header(settings: Settings, caplog: pytest.LogCaptureFixture) -> None:
    app = create_app(settings)  # SMTP set up, but no DIDIK_PUBLIC_URL
    app.state.mailer = Outbox()
    with TestClient(app, base_url="http://evil.example") as client, caplog.at_level(logging.ERROR):
        assert client.post("/api/auth/forgot", json={"email": DEMO_EMAIL}).status_code == 202
    assert app.state.mailer.sent == []
    assert "DIDIK_PUBLIC_URL" in caplog.text


def test_without_smtp_the_link_goes_to_the_server_log(settings: Settings, caplog: pytest.LogCaptureFixture) -> None:
    with TestClient(create_app(settings)) as client, caplog.at_level(logging.WARNING, logger="didik.mail"):
        assert client.get("/api/auth/me").json()["mail"] is False
        client.post("/api/auth/forgot", json={"email": DEMO_EMAIL})
    assert "http://testserver/ibu-bapa/kata-laluan#" in caplog.text


def test_the_command_line_prints_a_working_link(settings: Settings) -> None:
    with TestClient(create_app(settings)):
        pass  # creates the database with the demo parent
    env = {"DIDIK_DATA_DIR": str(settings.data_dir), "DIDIK_DATABASE_URL": settings.database_url, "PATH": ""}
    # Windows cannot start Python without these
    env |= {k: os.environ[k] for k in ("SYSTEMROOT", "SYSTEMDRIVE", "TEMP", "TMP") if k in os.environ}
    out = subprocess.run(
        [sys.executable, "-m", "didik_live", "--reset-link", DEMO_EMAIL, "--port", "8123"],
        capture_output=True, text=True, env=env, check=True,
    ).stdout
    link = out.strip().splitlines()[-1]
    assert link.startswith("http://localhost:8123/ibu-bapa/kata-laluan#")
    with TestClient(create_app(settings)) as client:
        assert client.post("/api/auth/reset/check", json={"token": link.split("#", 1)[1]}).json() == {"email": DEMO_EMAIL}
