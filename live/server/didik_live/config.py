"""Settings read once from the environment. Every value has a default that works on localhost.

With DIDIK_ENV=production the defaults turn safe for a public server (no demo account, no bots, cookies
only over https) and `problems()` lists what a public server still needs before it may start.
"""

from __future__ import annotations

import os
import re
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


# The secret address of the owner's control room: long enough that guessing it is hopeless.
ADMIN_PATH = re.compile(r"^[A-Za-z0-9_-]{24,64}$")


@dataclass(frozen=True)
class AdminSettings:
    """The owner's private control room. It exists only when both the owner's email and a secret path are
    set; otherwise the server has no admin pages at all, and every address under it is an ordinary 404."""

    # The only address that may ask for a sign-in code.
    email: str
    # The secret address, without slashes (generate one with `didik-live --admin-path`).
    path: str
    # The clock the dashboard's days and hours follow.
    timezone: str = "Asia/Kuala_Lumpur"
    session_hours: int = 12
    otp_minutes: int = 10

    @property
    def prefix(self) -> str:
        return f"/{self.path}"


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
    # The demo account's password is public, and it owns the sample quizzes everyone plays: it can only
    # sign in from the computer the server runs on (tests switch this off; their client is not local).
    demo_local_only: bool = True
    session_days: int = 30
    max_upload_bytes: int = 5 * 1024 * 1024
    # The address children use to reach the site (room links and QR codes). When empty, links use the
    # address the host's browser used, which is "localhost" on the host's own computer. Required for
    # emailed password reset links, which must never be built from a request's Host header.
    public_url: str | None = None
    # Without SMTP, password reset links are written to the server log instead of being emailed.
    mail: MailSettings | None = None
    # The owner's control room (see AdminSettings); None leaves it switched off.
    admin: AdminSettings | None = None
    # A public server (DIDIK_ENV=production): safe defaults, and a check of the settings before it starts.
    production: bool = False

    def problems(self) -> list[str]:
        """What stops this server from running in production, in words for whoever deploys it."""
        if not self.production:
            return []
        out = []
        if not self.public_url:
            out.append("DIDIK_PUBLIC_URL mesti ditetapkan (contoh https://didik.contoh.my): pautan bilik, kod QR dan emel dibina daripadanya.")
        elif not self.public_url.startswith("https://"):
            out.append("DIDIK_PUBLIC_URL mesti bermula dengan https:// pada pelayan sebenar.")
        if not self.secure_cookies:
            out.append("DIDIK_SECURE_COOKIES tidak boleh dimatikan pada pelayan sebenar: kuki sesi mesti dihantar melalui https sahaja.")
        if self.seed_demo:
            out.append("DIDIK_SEED_DEMO mesti 0 pada pelayan sebenar: kata laluan akaun demo diketahui umum.")
        if self.admin is not None and self.mail is None:
            out.append("Bilik kawalan admin perlukan SMTP (DIDIK_SMTP_*): kod log masuk dihantar melalui emel, bukan dalam log.")
        if not (self.web_dir / "200.html").is_file() and not (self.web_dir / "index.html").is_file():
            out.append(f"Antara muka belum dibina di {self.web_dir} (jalankan npm run build dalam live/web).")
        return out

    def warnings(self) -> list[str]:
        """What works, but is worth knowing on a public server."""
        if not self.production:
            return []
        out = []
        if self.mail is None:
            out.append("SMTP belum ditetapkan: pautan set semula kata laluan ditulis dalam log pelayan, bukan diemel.")
        if self.allow_bots:
            out.append("Bot latihan dibenarkan (DIDIK_ALLOW_BOTS=1).")
        return out

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"


def load_settings() -> Settings:
    production = (os.environ.get("DIDIK_ENV") or "").strip().lower() in {"production", "prod"}
    data_dir = Path(os.environ.get("DIDIK_DATA_DIR") or LIVE_DIR / "server" / "data").resolve()
    database_url = os.environ.get("DIDIK_DATABASE_URL") or f"sqlite:///{data_dir / 'didik-live.db'}"
    web_dir = Path(os.environ.get("DIDIK_WEB_DIR") or LIVE_DIR / "web" / "build").resolve()

    return Settings(
        data_dir=data_dir,
        database_url=database_url,
        web_dir=web_dir,
        secure_cookies=_flag("DIDIK_SECURE_COOKIES", production),
        allow_bots=_flag("DIDIK_ALLOW_BOTS", not production),
        seed_demo=_flag("DIDIK_SEED_DEMO", not production),
        public_url=(os.environ.get("DIDIK_PUBLIC_URL") or "").strip().rstrip("/") or None,
        mail=_mail(),
        admin=_admin(),
        production=production,
    )


def _admin() -> AdminSettings | None:
    email = (os.environ.get("DIDIK_ADMIN_EMAIL") or "").strip().lower()
    path = (os.environ.get("DIDIK_ADMIN_PATH") or "").strip().strip("/")
    if not email and not path:
        return None
    if not email or not path:
        raise ValueError("DIDIK_ADMIN_EMAIL dan DIDIK_ADMIN_PATH mesti ditetapkan bersama.")
    if not re.fullmatch(r"[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}", email):
        raise ValueError("DIDIK_ADMIN_EMAIL bukan alamat emel yang sah.")
    if not ADMIN_PATH.fullmatch(path):
        raise ValueError("DIDIK_ADMIN_PATH mesti 24 hingga 64 aksara (a-z, A-Z, 0-9, _ dan -). Jana satu: didik-live --admin-path")
    return AdminSettings(email=email, path=path, timezone=(os.environ.get("DIDIK_ADMIN_TZ") or "Asia/Kuala_Lumpur").strip())


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
