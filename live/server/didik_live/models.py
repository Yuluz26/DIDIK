"""Stored data: parents, their sign-in sessions and password reset links, their quizzes and their
uploaded pictures, and the rooms that are open right now. The owner's control room adds an activity
log, notifications, and its own one-time codes and sign-in sessions (kept apart from the parents').

Children have no accounts. A child in a room exists only for the life of that room: a running room is
saved (nicknames and scores included) so that restarting the server does not end it, and its row is
deleted as soon as the room closes.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, LargeBinary, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    # Set by the site's owner: a suspended parent cannot sign in and has no open rooms.
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    quizzes: Mapped[list[Quiz]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # Only a hash of the cookie value is stored, so a leaked database cannot sign anyone in.
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    user: Mapped[User] = relationship()


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(500), default="")
    # Questions are stored as one validated document (see questions.py): the editor saves a quiz
    # whole, and the eight question types share no columns worth normalising.
    questions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    is_sample: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    owner: Mapped[User] = relationship(back_populates="quizzes")


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(80), unique=True)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LiveRoom(Base):
    """One open room, saved every few seconds while it changes and when the server stops."""

    __tablename__ = "live_rooms"

    code: Mapped[str] = mapped_column(String(12), primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    # The room's JSON (Room.save), zlib-compressed: rooms are saved often and compress about tenfold.
    state: Mapped[bytes] = mapped_column(LargeBinary)


class PasswordReset(Base):
    """A one-time link to choose a new password. Only a hash of its token is stored."""

    __tablename__ = "password_resets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    user: Mapped[User] = relationship()


class ActivityEvent(Base):
    """One thing that happened on the site, for the owner's control room: a parent signed up, a quiz was
    written, a room opened, a child joined. Children are recorded by their nickname only (no address, no
    device), and the log is trimmed after 90 days."""

    __tablename__ = "activity_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    kind: Mapped[str] = mapped_column(String(40), index=True)
    # What the event is about in one word (a game's key), so the dashboard can group without opening `data`.
    subject: Mapped[str | None] = mapped_column(String(40), default=None, index=True)
    summary: Mapped[str] = mapped_column(String(200))
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    # The day and hour on the dashboard's clock, fixed when the event is written, so charts group in SQL.
    day: Mapped[str] = mapped_column(String(10), index=True)
    hour: Mapped[int] = mapped_column(SmallInteger)


class AdminNotification(Base):
    __tablename__ = "admin_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(String(600), default="")
    # info, success, warning or danger
    level: Mapped[str] = mapped_column(String(10), default="info")
    # "system" (made by the site) or "manual" (written by the owner)
    source: Mapped[str] = mapped_column(String(10), default="system")
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)


class AdminOtp(Base):
    """The one sign-in code that is valid right now. Only a hash is stored; it is single-use and short-lived."""

    __tablename__ = "admin_otps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ip: Mapped[str] = mapped_column(String(64), default="")
    agent: Mapped[str] = mapped_column(String(200), default="")
