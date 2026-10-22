"""Settings read once from the environment. Every value has a default that works on localhost."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
LIVE_DIR = PACKAGE_DIR.parents[1]


def _flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class MailSettings:
    """SMTP for the few emails the app sends (password reset links)."""

    host: str
    port: int
    user: str
    password: str
    # "starttls" (usually port 587), "ssl" (usually 465) or "none" (a relay on the same machine).
    security: str
    sender: str


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    database_url: str
    web_dir: Path
    # Cookies marked Secure are dropped over plain http, so this stays off until the site runs on https.
    secure_cookies: bool
    # Bots fill a room for testing alone; harmless in production but can be switched off.
    allow_bots: bool
    # Creates the demo parent and the sample quizzes on start when the database is empty.
    seed_demo: bool
    session_days: int = 30
    max_upload_bytes: int = 5 * 1024 * 1024
    # The address children use to reach the site (room links and QR codes). When empty, links use the
    # address the host's browser used, which is "localhost" on the host's own computer. Required for
    # emailed password reset links, which must never be built from a request's Host header.
    public_url: str | None = None
    # Without SMTP, password reset links are written to the server log instead of being emailed.
    mail: MailSettings | None = None

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"


def load_settings() -> Settings:
    data_dir = Path(os.environ.get("DIDIK_DATA_DIR") or LIVE_DIR / "server" / "data").resolve()
    database_url = os.environ.get("DIDIK_DATABASE_URL") or f"sqlite:///{data_dir / 'didik-live.db'}"
    web_dir = Path(os.environ.get("DIDIK_WEB_DIR") or LIVE_DIR / "web" / "build").resolve()

    return Settings(
        data_dir=data_dir,
        database_url=database_url,
        web_dir=web_dir,
        secure_cookies=_flag("DIDIK_SECURE_COOKIES", False),
        allow_bots=_flag("DIDIK_ALLOW_BOTS", True),
        seed_demo=_flag("DIDIK_SEED_DEMO", True),
        public_url=(os.environ.get("DIDIK_PUBLIC_URL") or "").strip().rstrip("/") or None,
        mail=_mail(),
    )


def _mail() -> MailSettings | None:
    host = (os.environ.get("DIDIK_SMTP_HOST") or "").strip()
    if not host:
        return None
    security = (os.environ.get("DIDIK_SMTP_SECURITY") or "starttls").strip().lower()
    if security not in {"starttls", "ssl", "none"}:
        raise ValueError("DIDIK_SMTP_SECURITY mesti starttls, ssl atau none")
    user = (os.environ.get("DIDIK_SMTP_USER") or "").strip()
    sender = (os.environ.get("DIDIK_MAIL_FROM") or "").strip() or (user if "@" in user else f"no-reply@{host}")
    return MailSettings(
        host=host,
        port=int(os.environ.get("DIDIK_SMTP_PORT") or (465 if security == "ssl" else 587)),
        user=user,
        password=os.environ.get("DIDIK_SMTP_PASSWORD") or "",
        security=security,
        sender=sender,
    )
