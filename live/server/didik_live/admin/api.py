"""The control room's JSON API, all under the secret path. Sign-in is open (and limited); everything else
needs the owner's session."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from ..activity import aware, event_out, iso, notification_out
from ..config import AdminSettings
from ..deps import client_ip, get_db, limit
from ..models import ActivityEvent, AdminNotification, AdminSession, AuthSession, Quiz, Upload, User
from . import auth, stats
from .auth import require_admin, settings_of

log = logging.getLogger("didik.admin")

public = APIRouter()
private = APIRouter(dependencies=[Depends(require_admin)])


class EmailIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: str = Field(min_length=3, max_length=254)


class CodeIn(EmailIn):
    code: str = Field(pattern=r"^\d{6}$")


# ---------------------------------------------------------------- signing in


def _when(app: Any) -> str:
    return datetime.now(app.state.admin_tz).strftime("%d/%m/%Y %H:%M")


def _send_code(app: Any, admin: AdminSettings, code: str, ip: str) -> None:
    body = (
        f"Kod log masuk bilik kawalan DIDIK: {code}\n\n"
        f"Kod ini sah {admin.otp_minutes} minit dan hanya boleh digunakan sekali.\n"
        f"Diminta pada {_when(app)} dari alamat {ip}.\n\n"
        "Jika bukan anda yang meminta kod ini, abaikan emel ini: tanpa kod ini, tiada sesiapa dapat log masuk.\n"
    )
    if app.state.mailer.send(admin.email, "Kod log masuk admin DIDIK", body) is False:
        app.state.bus.emit("admin.mail_failed", "Emel kod log masuk tidak dapat dihantar. Semak tetapan SMTP.", coalesce=("mail", 60))


def _send_alert(app: Any, admin: AdminSettings, ip: str, agent: str, new_ip: bool) -> None:
    body = (
        f"Seseorang baru log masuk ke bilik kawalan DIDIK pada {_when(app)}.\n\n"
        f"Alamat: {ip}{' (alamat baharu)' if new_ip else ''}\n"
        f"Peranti: {agent or 'tidak diketahui'}\n\n"
        "Jika itu bukan anda, tukar DIDIK_ADMIN_PATH pada pelayan dan kata laluan emel anda, "
        "kemudian mulakan semula perkhidmatan (ini menamatkan semua sesi).\n"
    )
    app.state.mailer.send(admin.email, "Log masuk admin DIDIK" + (" dari alamat baharu" if new_ip else ""), body)


@public.post("/api/otp", status_code=202)
def request_code(body: EmailIn, request: Request, background: BackgroundTasks, db: Session = Depends(get_db)) -> dict:
    """Emails a code to the owner. Any other address gets the very same answer and no email."""
    admin = settings_of(request)
    limit(request, "admin-otp", 5, 600)
    limit(request, "admin-otp-all", 12, 3600, key="all")
    code, hashed = auth.make_code()
    ip = client_ip(request)
    bus = request.app.state.bus
    if auth.is_owner(admin, body.email):
        if auth.store_code(db, admin, hashed):
            background.add_task(_send_code, request.app, admin, code, ip)
            bus.emit("admin.otp_sent", "Kod log masuk dihantar", coalesce=("otp", 30), ip=ip)
    else:
        bus.emit("admin.refused", "Kod diminta untuk emel yang tidak dibenarkan", coalesce=(ip, 300), ip=ip)
    return {"message": auth.SENT.format(minutes=admin.otp_minutes)}


@public.post("/api/verify")
def verify_code(body: CodeIn, request: Request, response: Response, background: BackgroundTasks, db: Session = Depends(get_db)) -> dict:
    admin = settings_of(request)
    limit(request, "admin-verify", 10, 600)
    limit(request, "admin-verify-all", 30, 3600, key="all")
    ip = client_ip(request)
    bus = request.app.state.bus
    right_code = auth.check_code(db, body.code)
    if not (right_code and auth.is_owner(admin, body.email)):
        bus.emit("admin.signin_failed", "Kod log masuk yang salah", coalesce=(ip, 60), ip=ip)
        raise HTTPException(422, auth.REFUSED)
    session, new_ip = auth.open_session(request, response, db)
    bus.emit("admin.signin", "Log masuk admin", ip=ip, agent=session.agent, newIp=new_ip)
    background.add_task(_send_alert, request.app, admin, ip, session.agent, new_ip)
    return {"ok": True}


@private.post("/api/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> Response:
    request.app.state.bus.emit("admin.signout", "Log keluar admin", ip=client_ip(request))
    auth.end_session(request, response, db)
    response.status_code = 204
    return response


@private.get("/api/me")
def me(request: Request, session: AdminSession = Depends(require_admin)) -> dict:
    admin = settings_of(request)
    return {
        "email": admin.email,
        "timezone": admin.timezone,
        "sessionId": session.id,
        "expiresAt": iso(session.expires_at),
        "now": iso(datetime.now(UTC)),
        "mail": request.app.state.mailer.ready,
    }


# ---------------------------------------------------------------- overview and live rooms


@private.get("/api/overview")
def overview(request: Request, days: int = 14, db: Session = Depends(get_db)) -> dict:
    return stats.overview(db, request.app.state.admin_tz, days)


async def live_names(request: Request) -> dict[int, str]:
    """Names of the parents hosting rooms right now (looked up off the event loop, remembered)."""
    cache: dict[int, str] = request.app.state.host_names
    wanted = {room.host_id for room in request.app.state.rooms.by_code.values()}
    if wanted - cache.keys():
        def fill() -> None:
            with request.app.state.db.sessions() as db:
                stats.host_names(db, wanted, cache)

        await run_in_threadpool(fill)
    return cache


@private.get("/api/live")
async def live(request: Request) -> dict:
    return stats.live(request.app.state.rooms, await live_names(request))


# ---------------------------------------------------------------- bulk actions
#
# Every list can act on many rows at once. A bulk call is one transaction, skips what it must not touch
# (the demo and sample accounts, rows that are already gone or already in the asked state) and says how many
# it did and how many it skipped. The log gets one summary line, not one per row.

MAX_BULK = 500


def _ids(values: list[int]) -> list[int]:
    return list(dict.fromkeys(values))


def _outcome(action: str, requested: int, done: int) -> dict[str, Any]:
    return {"action": action, "requested": requested, "done": done, "skipped": requested - done}


class RoomBulk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codes: list[Annotated[str, StringConstraints(max_length=12)]] = Field(min_length=1, max_length=100)
    action: Literal["close"]


@private.post("/api/rooms/bulk")
async def rooms_bulk(body: RoomBulk, request: Request) -> dict:
    rooms = request.app.state.rooms
    codes = list(dict.fromkeys(body.codes))
    closed = 0
    for code in codes:
        found = rooms.by_code.get(code)
        if found is not None:
            rooms.close(found, "Bilik ini ditutup oleh pentadbir laman.")
            closed += 1
    if closed:
        request.app.state.bus.emit("admin.room_closed", f"{closed} bilik ditutup oleh admin", count=closed, codes=codes[:10])
    return _outcome(body.action, len(codes), closed)


@private.get("/api/rooms/{code}")
async def room(code: str, request: Request) -> dict:
    detail = stats.room_detail(request.app.state.rooms, code, await live_names(request))
    if detail is None:
        raise HTTPException(404, "Bilik ini sudah tamat.")
    return detail


@private.post("/api/rooms/{code}/close", status_code=204)
async def close_room(code: str, request: Request) -> Response:
    rooms = request.app.state.rooms
    found = rooms.by_code.get(code)
    if found is None:
        raise HTTPException(404, "Bilik ini sudah tamat.")
    rooms.close(found, "Bilik ini ditutup oleh pentadbir laman.")
    request.app.state.bus.emit("admin.room_closed", f"Bilik {code} ditutup oleh admin", code=code)
    return Response(status_code=204)


# ---------------------------------------------------------------- parents


class UserPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=80)
    disabled: bool | None = None


def _search(column: Any, text: str) -> Any:
    return func.lower(column).contains(text.strip().lower(), autoescape=True)


def _page(page: int, per: int) -> tuple[int, int]:
    return max(1, page), min(max(5, per), 100)


def _user_where(q: str, status: str) -> list[Any]:
    """status: active, suspended or system (the demo and sample-library accounts)."""
    where: list[Any] = []
    if status == "system":
        where.append(User.email.in_(stats.SYSTEM_EMAILS))
    else:
        where.append(stats.real_users())
        if status == "active":
            where.append(User.disabled_at.is_(None))
        elif status == "suspended":
            where.append(User.disabled_at.is_not(None))
    if q.strip():
        where.append(or_(_search(User.name, q), _search(User.email, q)))
    return where


@private.get("/api/users")
def users(q: str = "", status: str = "active", page: int = 1, per: int = 25, db: Session = Depends(get_db)) -> dict:
    page, per = _page(page, per)
    owned = select(Quiz.owner_id, func.count().label("n")).where(Quiz.is_sample.is_(False)).group_by(Quiz.owner_id).subquery()
    where = _user_where(q, status)
    total = db.scalar(select(func.count()).select_from(User).where(*where)) or 0
    rows = db.execute(
        select(User, func.coalesce(owned.c.n, 0))
        .outerjoin(owned, owned.c.owner_id == User.id)
        .where(*where)
        .order_by(User.id.desc())
        .offset((page - 1) * per)
        .limit(per)
    ).all()
    return {"items": [stats.user_row(u, n) for u, n in rows], "total": total, "page": page, "per": per}


@private.get("/api/users/ids")
def user_ids(q: str = "", status: str = "active", db: Session = Depends(get_db)) -> dict:
    """Every account the filter matches (the first MAX_BULK), for "select all that match"."""
    where = _user_where(q, status)
    total = db.scalar(select(func.count()).select_from(User).where(*where)) or 0
    ids = list(db.scalars(select(User.id).where(*where).order_by(User.id.desc()).limit(MAX_BULK)))
    return {"ids": ids, "total": total, "capped": total > len(ids)}


class UserBulk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ids: list[int] = Field(min_length=1, max_length=MAX_BULK)
    action: Literal["suspend", "restore", "delete"]


@private.post("/api/users/bulk")
async def users_bulk(body: UserBulk, request: Request, db: Session = Depends(get_db)) -> dict:
    ids = _ids(body.ids)

    def work() -> tuple[list[int], list[str], list[str]]:
        rows = list(db.scalars(select(User).where(User.id.in_(ids), User.email.not_in(stats.SYSTEM_EMAILS))))
        files: list[str] = []
        if body.action == "suspend":
            rows = [u for u in rows if u.disabled_at is None]
            now = datetime.now(UTC)
            for user in rows:
                user.disabled_at = now
            if rows:
                db.execute(delete(AuthSession).where(AuthSession.user_id.in_([u.id for u in rows])))
        elif body.action == "restore":
            rows = [u for u in rows if u.disabled_at is not None]
            for user in rows:
                user.disabled_at = None
        else:
            if rows:
                files = list(db.scalars(select(Upload.filename).where(Upload.owner_id.in_([u.id for u in rows]))))
            for user in rows:
                db.delete(user)  # their quizzes, saved rooms and sessions go with them
        names = [u.name for u in rows][:5]
        changed = [u.id for u in rows]
        db.commit()
        return changed, names, files

    changed, names, files = await run_in_threadpool(work)
    if body.action in ("suspend", "delete"):
        for user_id in changed:
            _close_rooms_of(request, user_id, "Akaun hos ini digantung." if body.action == "suspend" else "Akaun hos ini telah dipadam.")
    folder = request.app.state.settings.upload_dir
    for filename in files:
        (folder / filename).unlink(missing_ok=True)
    if changed:
        kind, said = {"suspend": ("user.suspended", "digantung"), "restore": ("user.restored", "dipulihkan"), "delete": ("user.deleted", "dipadam")}[body.action]
        request.app.state.bus.emit(kind, f"{len(changed)} ibu bapa {said} oleh admin", count=len(changed), names=names, bulk=True)
    return _outcome(body.action, len(ids), len(changed))


def _user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "Ibu bapa ini tidak dijumpai.")
    return user


@private.get("/api/users/{user_id}")
def user_detail(user_id: int, db: Session = Depends(get_db)) -> dict:
    user = _user(db, user_id)
    quizzes = db.scalars(select(Quiz).where(Quiz.owner_id == user.id, Quiz.is_sample.is_(False)).order_by(Quiz.id.desc())).all()
    return stats.user_row(user, len(quizzes)) | {
        "quizList": [{"id": q.id, "title": q.title, "questions": len(q.questions), "updatedAt": iso(q.updated_at)} for q in quizzes],
        "pictures": db.scalar(select(func.count()).select_from(Upload).where(Upload.owner_id == user.id)) or 0,
    }


def _close_rooms_of(request: Request, user_id: int, message: str) -> None:
    rooms = request.app.state.rooms
    for open_room in rooms.rooms_of(user_id):
        rooms.close(open_room, message)


@private.patch("/api/users/{user_id}")
async def update_user(user_id: int, body: UserPatch, request: Request, db: Session = Depends(get_db)) -> dict:
    def work() -> tuple[dict, bool | None]:
        user = _user(db, user_id)
        if user.email in stats.SYSTEM_EMAILS:
            raise HTTPException(400, "Akaun sistem ini tidak boleh diubah.")
        changed: bool | None = None
        if body.name is not None:
            user.name = body.name
        if body.disabled is not None and (user.disabled_at is not None) != body.disabled:
            changed = body.disabled
            user.disabled_at = datetime.now(UTC) if body.disabled else None
            if body.disabled:
                db.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
        db.commit()
        return stats.user_row(user, 0), changed

    row, changed = await run_in_threadpool(work)
    bus = request.app.state.bus
    if changed is True:
        _close_rooms_of(request, user_id, "Akaun hos ini digantung.")
        bus.emit("user.suspended", f"{row['name']} digantung", userId=user_id, name=row["name"])
    elif changed is False:
        bus.emit("user.restored", f"{row['name']} dipulihkan", userId=user_id, name=row["name"])
    return row


@private.delete("/api/users/{user_id}", status_code=204)
async def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)) -> Response:
    def work() -> tuple[str, list[str]]:
        user = _user(db, user_id)
        if user.email in stats.SYSTEM_EMAILS:
            raise HTTPException(400, "Akaun sistem ini tidak boleh dipadam.")
        name = user.name
        files = list(db.scalars(select(Upload.filename).where(Upload.owner_id == user.id)))
        db.delete(user)  # their quizzes, pictures' rows, sessions and saved rooms go with them
        db.commit()
        return name, files

    name, files = await run_in_threadpool(work)
    _close_rooms_of(request, user_id, "Akaun hos ini telah dipadam.")
    folder = request.app.state.settings.upload_dir
    for filename in files:
        (folder / filename).unlink(missing_ok=True)
    request.app.state.bus.emit("user.deleted", f"{name} dipadam oleh admin", userId=user_id, name=name)
    return Response(status_code=204)


# ---------------------------------------------------------------- quizzes


class QuizPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


def _quiz_row(quiz: Quiz) -> dict[str, Any]:
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "owner": quiz.owner.name,
        "ownerId": quiz.owner_id,
        "questions": len(quiz.questions),
        "sample": quiz.is_sample,
        "createdAt": iso(quiz.created_at),
        "updatedAt": iso(quiz.updated_at),
    }


def _quiz_where(q: str, samples: bool) -> list[Any]:
    where: list[Any] = [Quiz.is_sample.is_(samples)]
    if q.strip():
        where.append(or_(_search(Quiz.title, q), Quiz.owner_id.in_(select(User.id).where(_search(User.name, q)))))
    return where


@private.get("/api/quizzes")
def quizzes(q: str = "", samples: bool = False, page: int = 1, per: int = 25, db: Session = Depends(get_db)) -> dict:
    page, per = _page(page, per)
    where = _quiz_where(q, samples)
    total = db.scalar(select(func.count()).select_from(Quiz).where(*where)) or 0
    rows = db.scalars(select(Quiz).where(*where).order_by(Quiz.id.desc()).offset((page - 1) * per).limit(per)).all()
    return {"items": [_quiz_row(row) for row in rows], "total": total, "page": page, "per": per}


@private.get("/api/quizzes/ids")
def quiz_ids(q: str = "", samples: bool = False, db: Session = Depends(get_db)) -> dict:
    where = _quiz_where(q, samples)
    total = db.scalar(select(func.count()).select_from(Quiz).where(*where)) or 0
    ids = list(db.scalars(select(Quiz.id).where(*where).order_by(Quiz.id.desc()).limit(MAX_BULK)))
    return {"ids": ids, "total": total, "capped": total > len(ids)}


class QuizBulk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ids: list[int] = Field(min_length=1, max_length=MAX_BULK)
    action: Literal["delete"]


@private.post("/api/quizzes/bulk")
def quizzes_bulk(body: QuizBulk, request: Request, db: Session = Depends(get_db)) -> dict:
    ids = _ids(body.ids)
    rows = list(db.scalars(select(Quiz).where(Quiz.id.in_(ids))))
    titles = [row.title for row in rows][:5]
    for row in rows:
        db.delete(row)
    db.commit()
    if rows:
        request.app.state.bus.emit("quiz.deleted", f"{len(rows)} kuiz dipadam oleh admin", count=len(rows), titles=titles, byAdmin=True, bulk=True)
    return _outcome(body.action, len(ids), len(rows))


def _the_quiz(db: Session, quiz_id: int) -> Quiz:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None:
        raise HTTPException(404, "Kuiz ini tidak dijumpai.")
    return quiz


@private.get("/api/quizzes/{quiz_id}")
def quiz_detail(quiz_id: int, db: Session = Depends(get_db)) -> dict:
    quiz = _the_quiz(db, quiz_id)
    kinds: dict[str, int] = {}
    for question in quiz.questions:
        kinds[question.get("type", "?")] = kinds.get(question.get("type", "?"), 0) + 1
    return _quiz_row(quiz) | {"types": kinds, "prompts": [str(q.get("prompt", ""))[:160] for q in quiz.questions[:40]]}


@private.patch("/api/quizzes/{quiz_id}")
def update_quiz(quiz_id: int, body: QuizPatch, request: Request, db: Session = Depends(get_db)) -> dict:
    quiz = _the_quiz(db, quiz_id)
    if body.title is not None:
        quiz.title = body.title
    if body.description is not None:
        quiz.description = body.description
    db.commit()
    request.app.state.bus.emit("admin.quiz_edited", f"Kuiz “{quiz.title}” disunting oleh admin", quizId=quiz.id)
    return _quiz_row(quiz)


@private.delete("/api/quizzes/{quiz_id}", status_code=204)
def delete_quiz(quiz_id: int, request: Request, db: Session = Depends(get_db)) -> Response:
    quiz = _the_quiz(db, quiz_id)
    title, owner = quiz.title, quiz.owner.name
    db.delete(quiz)
    db.commit()
    request.app.state.bus.emit("quiz.deleted", f"Kuiz “{title}” ({owner}) dipadam oleh admin", quizId=quiz_id, title=title, owner=owner, byAdmin=True)
    return Response(status_code=204)


# ---------------------------------------------------------------- notifications


class NoteIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=1, max_length=120)
    body: str = Field(default="", max_length=600)
    level: Literal["info", "success", "warning", "danger"] = "info"
    pinned: bool = False


class NotePatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=120)
    body: str | None = Field(default=None, max_length=600)
    level: Literal["info", "success", "warning", "danger"] | None = None
    pinned: bool | None = None
    read: bool | None = None


@private.get("/api/notifications")
def notifications(show: str = "all", db: Session = Depends(get_db)) -> dict:
    """show: all, unread, pinned or manual (the owner's own notes)."""
    where: list[Any] = []
    if show == "unread":
        where.append(AdminNotification.read_at.is_(None))
    elif show == "pinned":
        where.append(AdminNotification.pinned.is_(True))
    elif show == "manual":
        where.append(AdminNotification.source == "manual")
    rows = db.scalars(select(AdminNotification).where(*where).order_by(AdminNotification.pinned.desc(), AdminNotification.id.desc()).limit(200)).all()
    unread = db.scalar(select(func.count()).select_from(AdminNotification).where(AdminNotification.read_at.is_(None))) or 0
    return {"items": [notification_out(row) for row in rows], "unread": unread}


@private.post("/api/notifications", status_code=201)
def create_notification(body: NoteIn, request: Request, db: Session = Depends(get_db)) -> dict:
    row = AdminNotification(title=body.title, body=body.body, level=body.level, pinned=body.pinned, source="manual")
    db.add(row)
    db.commit()
    out = notification_out(row)
    request.app.state.bus.publish({"t": "notification", "notification": out})
    return out


@private.post("/api/notifications/read-all", status_code=204)
def read_all(request: Request, db: Session = Depends(get_db)) -> Response:
    now = datetime.now(UTC)
    for row in db.scalars(select(AdminNotification).where(AdminNotification.read_at.is_(None))):
        row.read_at = now
    db.commit()
    request.app.state.bus.publish({"t": "notifications-changed"})
    return Response(status_code=204)


@private.delete("/api/notifications", status_code=204)
def clear_read(request: Request, db: Session = Depends(get_db)) -> Response:
    """Removes every notification that has been read and is not pinned."""
    db.execute(delete(AdminNotification).where(AdminNotification.read_at.is_not(None), AdminNotification.pinned.is_(False)))
    db.commit()
    request.app.state.bus.publish({"t": "notifications-changed"})
    return Response(status_code=204)


class NoteBulk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ids: list[int] = Field(min_length=1, max_length=MAX_BULK)
    action: Literal["read", "unread", "pin", "unpin", "delete"]


@private.post("/api/notifications/bulk")
def notifications_bulk(body: NoteBulk, request: Request, db: Session = Depends(get_db)) -> dict:
    ids = _ids(body.ids)
    rows = list(db.scalars(select(AdminNotification).where(AdminNotification.id.in_(ids))))
    now = datetime.now(UTC)
    for row in rows:
        if body.action == "read":
            row.read_at = row.read_at or now
        elif body.action == "unread":
            row.read_at = None
        elif body.action == "pin":
            row.pinned = True
        elif body.action == "unpin":
            row.pinned = False
        else:
            db.delete(row)
    db.commit()
    request.app.state.bus.publish({"t": "notifications-changed"})
    return _outcome(body.action, len(ids), len(rows))


def _note(db: Session, note_id: int) -> AdminNotification:
    row = db.get(AdminNotification, note_id)
    if row is None:
        raise HTTPException(404, "Notifikasi ini tidak dijumpai.")
    return row


@private.patch("/api/notifications/{note_id}")
def update_notification(note_id: int, body: NotePatch, request: Request, db: Session = Depends(get_db)) -> dict:
    row = _note(db, note_id)
    for field in ("title", "body", "level", "pinned"):
        value = getattr(body, field)
        if value is not None:
            setattr(row, field, value)
    if body.read is not None:
        row.read_at = datetime.now(UTC) if body.read else None
    db.commit()
    out = notification_out(row)
    request.app.state.bus.publish({"t": "notification", "notification": out})
    return out


@private.delete("/api/notifications/{note_id}", status_code=204)
def delete_notification(note_id: int, request: Request, db: Session = Depends(get_db)) -> Response:
    db.delete(_note(db, note_id))
    db.commit()
    request.app.state.bus.publish({"t": "notification-removed", "id": note_id})
    return Response(status_code=204)


# ---------------------------------------------------------------- activity and security

GROUPS = {"user", "quiz", "room", "player", "game", "admin"}


@private.get("/api/activity")
def activity(group: str = "", q: str = "", before: int | None = None, per: int = 40, db: Session = Depends(get_db)) -> dict:
    """The log, newest first. `before` is the id of the last row already shown. Without a group, the
    owner's own sign-ins are left out (they have a page of their own)."""
    per = min(max(10, per), 100)
    where: list[Any] = []
    if group in GROUPS:
        where.append(ActivityEvent.kind.startswith(group + "."))
    else:
        where.append(~ActivityEvent.kind.startswith("admin."))
    if before:
        where.append(ActivityEvent.id < before)
    if q.strip():
        where.append(_search(ActivityEvent.summary, q))
    rows = db.scalars(select(ActivityEvent).where(*where).order_by(ActivityEvent.id.desc()).limit(per + 1)).all()
    return {"items": [event_out(row) for row in rows[:per]], "more": len(rows) > per}


@private.get("/api/security")
def security(session: AdminSession = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    now = datetime.now(UTC)
    live_sessions = [s for s in db.scalars(select(AdminSession).order_by(AdminSession.id.desc())) if aware(s.expires_at) > now]
    log_rows = db.scalars(select(ActivityEvent).where(ActivityEvent.kind.startswith("admin.")).order_by(ActivityEvent.id.desc()).limit(40)).all()
    return {
        "sessions": [
            {
                "id": s.id,
                "current": s.id == session.id,
                "createdAt": iso(s.created_at),
                "lastSeenAt": iso(s.last_seen_at),
                "expiresAt": iso(s.expires_at),
                "ip": s.ip,
                "agent": s.agent,
            }
            for s in live_sessions
        ],
        "log": [event_out(row) for row in log_rows],
    }


@private.post("/api/sessions/revoke-others", status_code=204)
def revoke_others(request: Request, session: AdminSession = Depends(require_admin), db: Session = Depends(get_db)) -> Response:
    db.execute(delete(AdminSession).where(AdminSession.id != session.id))
    db.commit()
    request.app.state.bus.emit("admin.sessions_revoked", "Semua sesi lain ditamatkan", ip=client_ip(request))
    return Response(status_code=204)


@private.delete("/api/sessions/{session_id}", status_code=204)
def revoke(session_id: int, request: Request, session: AdminSession = Depends(require_admin), db: Session = Depends(get_db)) -> Response:
    if session_id == session.id:
        raise HTTPException(400, "Ini sesi anda sekarang. Gunakan Log keluar.")
    db.execute(delete(AdminSession).where(AdminSession.id == session_id))
    db.commit()
    request.app.state.bus.emit("admin.session_revoked", "Satu sesi ditamatkan", ip=client_ip(request))
    return Response(status_code=204)
