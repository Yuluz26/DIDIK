"""Parent accounts: register, sign in, sign out. Children never get accounts."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..deps import current_user, end_session, get_db, limit, start_session
from ..models import User
from ..security import DUMMY_PASSWORD_HASH, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$")


class Register(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        if not EMAIL.match(value):
            raise ValueError("Masukkan alamat emel yang sah.")
        return value.lower()

    @field_validator("password")
    @classmethod
    def _password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Kata laluan perlu sekurang-kurangnya 8 aksara.")
        return value


class Login(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=200)


def user_out(user: User | None) -> dict | None:
    if user is None:
        return None
    return {"id": user.id, "name": user.name, "email": user.email}


@router.get("/me")
def me(user: User | None = Depends(current_user)) -> dict:
    return {"user": user_out(user)}


@router.post("/register", status_code=201)
def register(body: Register, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    limit(request, "register", 5, 600)
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
    limit(request, "login", 10, 60)
    limit(request, "login-email", 8, 600, key=email)
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    if not verify_password(body.password, user.password_hash if user else DUMMY_PASSWORD_HASH) or user is None:
        raise HTTPException(422, {"message": "Emel atau kata laluan tidak betul.", "errors": []})
    start_session(request, response, db, user)
    return {"user": user_out(user)}


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> Response:
    end_session(request, response, db)
    response.status_code = 204
    return response
