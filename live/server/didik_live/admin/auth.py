"""Signing in to the control room: a secret address, then a six-digit code sent to the owner's email.

Nothing here trusts the address alone. The code is hashed, lives ten minutes, allows five tries and works once;
asking for one is limited, and only the configured email ever gets one (the answer is the same for any other,
so the form cannot be used to find out which address is the owner's). The session cookie belongs to the secret
path alone, so the browser never sends it anywhere else on the site.
"""

from __future__ import annotations

import hmac
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from ..activity import aware
from ..deps import client_ip, get_db
from ..config import AdminSettings
from ..models import AdminOtp, AdminSession
from ..security import DUMMY_PASSWORD_HASH, hash_password, new_token, token_hash, verify_password

COOKIE = "didik_admin"
MAX_TRIES = 5
# The cooldown between two codes, so a stuck button cannot flood the owner's inbox.
RESEND_SECONDS = 60
# A browser left alone this long asks for a new code, even before the session's own end.
IDLE = timedelta(hours=4)
UNSAFE = {"POST", "PUT", "PATCH", "DELETE"}
SENT = "Jika emel ini dibenarkan, kod 6 digit sudah dihantar ke sana. Kod sah {minutes} minit."
REFUSED = "Kod tidak sah atau sudah tamat tempoh."


def settings_of(request: Request) -> AdminSettings:
    admin = request.app.state.settings.admin
    assert admin is not None  # the routes exist only when the control room is switched on
    return admin


def make_code() -> tuple[str, str]:
    """A fresh code and its hash. The hash is always made, so a wrong email takes as long as the right one."""
    code = f"{secrets.randbelow(10**6):06d}"
    return code, hash_password(code)


def is_owner(admin: AdminSettings, email: str) -> bool:
    return hmac.compare_digest(email.strip().lower().encode(), admin.email.encode())


def store_code(db: Session, admin: AdminSettings, hashed: str) -> bool:
    """Replaces the code in force with a new one. False (and nothing changes) within the cooldown."""
    now = datetime.now(UTC)
    last = db.scalar(select(AdminOtp).order_by(AdminOtp.id.desc()).limit(1))
    if last is not None and aware(last.created_at) > now - timedelta(seconds=RESEND_SECONDS):
        return False
    db.execute(delete(AdminOtp))
    db.add(AdminOtp(code_hash=hashed, expires_at=now + timedelta(minutes=admin.otp_minutes)))
    db.commit()
    return True


def check_code(db: Session, code: str) -> bool:
    """Whether this is the code in force. Every try is counted before it is judged, atomically, so
    parallel guesses cannot share one attempt; the fifth wrong try ends the code."""
    now = datetime.now(UTC)
    otp = db.scalar(select(AdminOtp).order_by(AdminOtp.id.desc()).limit(1))
    if otp is None or aware(otp.expires_at) <= now:
        verify_password(code, DUMMY_PASSWORD_HASH)  # the same time as a real check
        return False
    counted = db.execute(
        update(AdminOtp).where(AdminOtp.id == otp.id, AdminOtp.attempts < MAX_TRIES).values(attempts=AdminOtp.attempts + 1)
    )
    db.commit()
    if counted.rowcount == 0:
        verify_password(code, DUMMY_PASSWORD_HASH)
        return False
    if not verify_password(code, otp.code_hash):
        return False
    db.delete(otp)  # single use
    db.commit()
    return True


def open_session(request: Request, response: Response, db: Session) -> tuple[AdminSession, bool]:
    """Starts a session and sets its cookie. The second value is whether this address is new to the owner."""
    admin = settings_of(request)
    settings = request.app.state.settings
    ip = client_ip(request)
    known = db.scalar(select(AdminSession.id).where(AdminSession.ip == ip).limit(1)) is not None
    token = new_token()
    row = AdminSession(
        token_hash=token_hash(token),
        expires_at=datetime.now(UTC) + timedelta(hours=admin.session_hours),
        ip=ip,
        agent=(request.headers.get("user-agent") or "")[:200],
    )
    db.add(row)
    db.commit()
    response.set_cookie(
        COOKIE,
        token,
        max_age=admin.session_hours * 3600,
        httponly=True,
        samesite="strict",
        secure=settings.secure_cookies,
        path=admin.prefix,
    )
    return row, not known


def find_session(db: Session, token: str | None) -> AdminSession | None:
    """The live session for this cookie value, or None. Expired and idle sessions are removed."""
    if not token:
        return None
    row = db.scalar(select(AdminSession).where(AdminSession.token_hash == token_hash(token)))
    if row is None:
        return None
    now = datetime.now(UTC)
    if aware(row.expires_at) <= now or aware(row.last_seen_at) < now - IDLE:
        db.delete(row)
        db.commit()
        return None
    if aware(row.last_seen_at) < now - timedelta(minutes=1):
        row.last_seen_at = now
        db.commit()
    return row


def end_session(request: Request, response: Response, db: Session) -> None:
    row = find_session(db, request.cookies.get(COOKIE))
    if row is not None:
        db.delete(row)
        db.commit()
    response.delete_cookie(COOKIE, path=settings_of(request).prefix)


def require_admin(request: Request, db: Session = Depends(get_db)) -> AdminSession:
    row = find_session(db, request.cookies.get(COOKIE))
    if row is None:
        raise HTTPException(401, "Sila log masuk.")
    # A page of another site cannot add this header to a request without the browser asking this server
    # first, and this server never agrees (see also the same-origin check in app.Guard).
    if request.method in UNSAFE and request.headers.get("x-didik-admin") != "1":
        raise HTTPException(403, "Permintaan ditolak.")
    return row
