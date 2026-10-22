"""Request-scoped helpers shared by the API routers: the database session, the signed-in parent,
request limits and Malay error responses."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import AuthSession, User
from .security import new_token, token_hash

SESSION_COOKIE = "didik_sesi"


def get_db(request: Request) -> Iterator[Session]:
    yield from request.app.state.db.session()


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def site_url(request: Request) -> str:
    """The site's address for links: DIDIK_PUBLIC_URL, else the address this browser used."""
    return request.app.state.settings.public_url or str(request.base_url).rstrip("/")


def limit(request: Request, bucket: str, count: int, per_seconds: float, key: str | None = None) -> None:
    limiter = request.app.state.limiter
    if not limiter.hit(f"{bucket}:{key or client_ip(request)}", count, per_seconds):
        raise HTTPException(429, "Terlalu banyak cubaan. Tunggu sebentar dan cuba lagi.")


def start_session(request: Request, response: Response, db: Session, user: User) -> None:
    settings = request.app.state.settings
    token = new_token()
    db.add(
        AuthSession(
            user_id=user.id,
            token_hash=token_hash(token),
            expires_at=datetime.now(UTC) + timedelta(days=settings.session_days),
        )
    )
    db.commit()
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.session_days * 86400,
        httponly=True,
        samesite="lax",
        secure=settings.secure_cookies,
        path="/",
    )


def end_session(request: Request, response: Response, db: Session) -> None:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        db.execute(delete(AuthSession).where(AuthSession.token_hash == token_hash(token)))
        db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")


def user_from_token(db: Session, token: str | None) -> User | None:
    if not token:
        return None
    row = db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash(token)))
    if row is None:
        return None
    expires = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)
    if expires < datetime.now(UTC):
        db.delete(row)
        db.commit()
        return None
    return row.user


def current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    return user_from_token(db, request.cookies.get(SESSION_COOKIE))


def require_user(user: User | None = Depends(current_user)) -> User:
    if user is None:
        raise HTTPException(401, "Sila log masuk dahulu.")
    return user


_MESSAGES = {
    "missing": "Wajib diisi.",
    "string_too_short": "Wajib diisi.",
    "string_too_long": "Terlalu panjang (maksimum {max_length} aksara).",
    "too_short": "Perlu sekurang-kurangnya {min_length}.",
    "too_long": "Maksimum {max_length} sahaja.",
    "greater_than_equal": "Mesti sekurang-kurangnya {ge}.",
    "less_than_equal": "Mesti tidak lebih daripada {le}.",
    "string_pattern_mismatch": "Format tidak sah.",
    "union_tag_invalid": "Jenis soalan tidak dikenali.",
    "union_tag_not_found": "Pilih jenis soalan.",
    "extra_forbidden": "Medan ini tidak dikenali.",
    "float_type": "Tulis satu nombor.",
    "float_parsing": "Tulis satu nombor.",
    "int_type": "Tulis nombor bulat.",
    "int_parsing": "Tulis nombor bulat.",
    "bool_type": "Pilih ya atau tidak.",
}


def malay_errors(errors: list[dict]) -> list[dict]:
    """Pydantic's errors in plain Malay, keyed by the path the editor uses to place them."""
    out = []
    for error in errors:
        kind = error.get("type", "")
        context = error.get("ctx") or {}
        if kind == "value_error":
            message = str(context.get("error") or error.get("msg", "")).removeprefix("Value error, ")
        elif kind == "string_too_short" and int(context.get("min_length", 1)) > 1:
            message = f"Terlalu pendek: sekurang-kurangnya {context['min_length']} aksara."
        else:
            template = _MESSAGES.get(kind, "Nilai tidak sah.")
            try:
                message = template.format(**{k: v for k, v in context.items() if isinstance(v, (int, float, str))})
            except (KeyError, IndexError):
                message = template
        out.append({"loc": _clean_loc(error.get("loc", ())), "message": message})
    return out


_TAGS = {"single", "multiple", "truefalse", "text", "number", "order", "match", "blank"}


def _clean_loc(loc: tuple | list) -> list:
    """Drops "body" and the union tag Pydantic puts after a question's index
    (questions, 2, "single", choices ...), which is noise for the editor."""
    parts = [p for p in loc if p != "body"]
    clean: list = []
    for index, part in enumerate(parts):
        after_question = index >= 2 and parts[index - 2] == "questions" and isinstance(parts[index - 1], int)
        if after_question and part in _TAGS:
            continue
        clean.append(part)
    return clean
