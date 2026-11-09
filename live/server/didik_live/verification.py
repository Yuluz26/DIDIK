"""Single-use email verification links; only hashes are retained."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .activity import aware
from .models import EmailVerification, User
from .security import new_token, token_hash


def issue(db: Session, user: User) -> str:
    db.execute(delete(EmailVerification).where(EmailVerification.user_id == user.id))
    token = new_token()
    db.add(EmailVerification(user_id=user.id, token_hash=token_hash(token),
                             expires_at=datetime.now(UTC) + timedelta(hours=24)))
    db.commit()
    return token


def complete(db: Session, token: str) -> User | None:
    row = db.scalar(select(EmailVerification).where(EmailVerification.token_hash == token_hash(token)))
    if row is None or aware(row.expires_at) <= datetime.now(UTC):
        return None
    user = db.get(User, row.user_id)
    if user is None:
        return None
    user.email_verified_at = datetime.now(UTC)
    db.execute(delete(EmailVerification).where(EmailVerification.user_id == user.id))
    db.commit()
    return user


def message(name: str, base: str, token: str) -> tuple[str, str]:
    url = f"{base}/ibu-bapa/sahkan-emel#{token}"
    return "Sahkan emel DIDIK", (
        f"Salam {name},\n\nBuka pautan ini untuk mengesahkan emel akaun DIDIK anda. "
        f"Pautan sah selama 24 jam dan hanya boleh digunakan sekali:\n{url}\n\n"
        "Jika anda tidak mendaftar, abaikan emel ini.\n\nDIDIK Main Bersama\n")
