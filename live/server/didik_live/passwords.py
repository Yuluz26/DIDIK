"""Password reset links for parents.

The token travels in the link's fragment (after #), which browsers never send to a server, so it
stays out of access logs. Only its hash is stored; a link works once and for an hour, and asking for
a new link cancels the old one.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from .models import AuthSession, PasswordReset, User
from .security import hash_password, new_token, token_hash

RESET_MINUTES = 60
RESET_PATH = "/ibu-bapa/kata-laluan"


def issue(db: Session, user: User) -> str:
    """A fresh token for this parent; any earlier link stops working."""
    now = datetime.now(UTC)
    db.execute(delete(PasswordReset).where(or_(PasswordReset.user_id == user.id, PasswordReset.expires_at < now)))
    token = new_token()
    db.add(PasswordReset(user_id=user.id, token_hash=token_hash(token), expires_at=now + timedelta(minutes=RESET_MINUTES)))
    db.commit()
    return token


def link(base: str, token: str) -> str:
    return f"{base}{RESET_PATH}#{token}"


def pending(db: Session, token: str) -> PasswordReset | None:
    """The reset this token belongs to, while it can still be used."""
    row = db.scalar(select(PasswordReset).where(PasswordReset.token_hash == token_hash(token)))
    if row is None:
        return None
    expires = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)
    return row if expires > datetime.now(UTC) else None


def complete(db: Session, reset: PasswordReset, password: str) -> User:
    """Sets the new password, uses up every reset link of this parent and signs out every device."""
    user = reset.user
    user.password_hash = hash_password(password)
    db.execute(delete(PasswordReset).where(PasswordReset.user_id == user.id))
    db.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
    db.commit()
    return user


def email(name: str, url: str) -> tuple[str, str]:
    """Subject and plain-text body of the reset email."""
    subject = "Tetapkan kata laluan baharu untuk DIDIK Main Bersama"
    body = (
        f"Salam {name},\n\n"
        "Ada permintaan untuk menetapkan kata laluan baharu bagi akaun DIDIK Main Bersama dengan emel ini.\n\n"
        "Buka pautan ini untuk memilih kata laluan baharu. Pautan ini sah selama satu jam dan boleh digunakan sekali sahaja:\n"
        f"{url}\n\n"
        "Jika anda tidak memintanya, abaikan emel ini. Kata laluan anda tidak berubah.\n\n"
        "DIDIK Main Bersama\n"
    )
    return subject, body
