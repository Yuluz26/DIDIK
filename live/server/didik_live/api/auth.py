"""Parent accounts: register, sign in, sign out, and a new password by email. Children never get
accounts."""

from __future__ import annotations

import logging
import re

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import passwords
from ..deps import current_user, demo_allowed, end_session, get_db, limit, site_url, start_session
from ..models import User
from ..security import DUMMY_PASSWORD_HASH, hash_password, verify_password
from ..seed import DEMO_EMAIL, LIBRARY_EMAIL

router = APIRouter(prefix="/api/auth", tags=["auth"])
log = logging.getLogger("didik.auth")

EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$")
RESET_SENT = (
    "Jika emel ini berdaftar, pautan untuk menetapkan kata laluan baharu sudah dihantar ke sana. "
    "Pautan itu sah selama satu jam."
)
RESET_GONE = "Pautan ini sudah tamat tempoh atau sudah digunakan. Minta pautan baharu."


def valid_email(value: str) -> str:
    if not EMAIL.match(value):
        raise ValueError("Masukkan alamat emel yang sah.")
    return value.lower()


def valid_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Kata laluan perlu sekurang-kurangnya 8 aksara.")
    return value


class Register(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=200)

    _email = field_validator("email")(valid_email)
    _password = field_validator("password")(valid_password)


class Login(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=200)


class Forgot(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=3, max_length=254)

    _email = field_validator("email")(valid_email)


class ResetLink(BaseModel):
    token: str = Field(min_length=20, max_length=100)


class NewPassword(ResetLink):
    password: str = Field(min_length=8, max_length=200)

    _password = field_validator("password")(valid_password)


def user_out(user: User | None) -> dict | None:
    if user is None:
        return None
    return {"id": user.id, "name": user.name, "email": user.email}


@router.get("/me")
def me(request: Request, user: User | None = Depends(current_user)) -> dict:
    # `demo` tells the sign-in page to show the local demo account (only when it was seeded); `mail`
    # whether reset links are emailed or only written to the server log.
    return {"user": user_out(user), "demo": demo_allowed(request), "mail": request.app.state.mailer.ready}


@router.post("/register", status_code=201)
def register(body: Register, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    limit(request, "register", 20, 600)
    if db.scalar(select(User).where(func.lower(User.email) == body.email)):
        raise HTTPException(422, {"message": "Semak semula maklumat.", "errors": [
            {"loc": ["email"], "message": "Emel ini sudah didaftarkan. Cuba log masuk."}
        ]})
    user = User(name=body.name, email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    start_session(request, response, db, user)
    return {"user": user_out(user)}


@router.post("/login")
def login(body: Login, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    email = body.email.lower()
    limit(request, "login", 30, 60)
    limit(request, "login-email", 8, 600, key=email)
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    if not verify_password(body.password, user.password_hash if user else DUMMY_PASSWORD_HASH) or user is None:
        raise HTTPException(422, {"message": "Emel atau kata laluan tidak betul.", "errors": []})
    if user.email == DEMO_EMAIL and not demo_allowed(request):
        # the same answer as a wrong password: the demo account does not exist for the internet
        raise HTTPException(422, {"message": "Emel atau kata laluan tidak betul.", "errors": []})
    start_session(request, response, db, user)
    return {"user": user_out(user)}


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> Response:
    end_session(request, response, db)
    response.status_code = 204
    return response


@router.post("/forgot", status_code=202)
def forgot(body: Forgot, request: Request, background: BackgroundTasks, db: Session = Depends(get_db)) -> dict:
    """Sends a reset link. The answer is the same whether or not the email has an account."""
    limit(request, "forgot", 20, 600)
    limit(request, "forgot-email", 3, 3600, key=body.email)
    user = db.scalar(select(User).where(func.lower(User.email) == body.email))
    # nobody can take over the account that owns the samples, or the demo account on a public server
    if user is None or user.email == LIBRARY_EMAIL or (user.email == DEMO_EMAIL and not demo_allowed(request)):
        return {"message": RESET_SENT}
    mailer = request.app.state.mailer
    if mailer.ready and not request.app.state.settings.public_url:
        # A link sent by email must not be built from the request's Host header, which anyone can
        # set: the email would carry a valid token to the sender's own site.
        log.error("Pautan set semula tidak dihantar: tetapkan DIDIK_PUBLIC_URL untuk menghantar emel.")
        return {"message": RESET_SENT}
    url = passwords.link(site_url(request), passwords.issue(db, user))
    subject, text = passwords.email(user.name, url)
    background.add_task(mailer.send, user.email, subject, text)
    return {"message": RESET_SENT}


@router.post("/reset/check")
def reset_check(body: ResetLink, request: Request, db: Session = Depends(get_db)) -> dict:
    """Whether a reset link still works, and for which account."""
    limit(request, "reset", 20, 600)
    reset = passwords.pending(db, body.token)
    if reset is None:
        raise HTTPException(410, RESET_GONE)
    return {"email": reset.user.email}


@router.post("/reset")
def reset_password(body: NewPassword, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    limit(request, "reset", 20, 600)
    reset = passwords.pending(db, body.token)
    if reset is None:
        raise HTTPException(410, RESET_GONE)
    user = passwords.complete(db, reset, body.password)
    start_session(request, response, db, user)
    return {"user": user_out(user)}
