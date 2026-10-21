"""Opening a room from a quiz, looking a room up by its link, and the room's QR code.

Everything that touches live rooms runs on the event loop (async endpoints), never in a worker
thread, because rooms are only ever changed from the loop.
"""

from __future__ import annotations

from io import BytesIO

import segno
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from ..deps import get_db, limit, require_user
from ..game.modes import MODES
from ..game.settings import RoomSettings
from ..models import Quiz, User
from ..questions import parse_questions

router = APIRouter(prefix="/api", tags=["rooms"])


class OpenRoom(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quiz_id: int
    mode: str = Field(min_length=1, max_length=20)
    settings: RoomSettings = Field(default_factory=RoomSettings)


def join_link(request: Request, slug: str) -> str:
    return f"{str(request.base_url).rstrip('/')}/m/{slug}"


def _quiz_for(db: Session, quiz_id: int, user: User) -> Quiz:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None or (quiz.owner_id != user.id and not quiz.is_sample):
        raise HTTPException(404, "Kuiz tidak dijumpai.")
    return quiz


def _room_or_404(request: Request, key: str):
    room = request.app.state.rooms.find(key)
    if room is None:
        raise HTTPException(404, "Bilik tidak dijumpai. Semak kod atau minta pautan baharu.")
    return room


@router.get("/modes")
def modes(quiz_id: int | None = None, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    questions = parse_questions(_quiz_for(db, quiz_id, user).questions) if quiz_id else None
    return {"modes": [cls.describe(questions) for cls in MODES.values()]}


@router.post("/rooms", status_code=201)
async def open_room(
    body: OpenRoom, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)
) -> dict:
    limit(request, "open-room", 20, 600, key=str(user.id))
    if body.mode not in MODES:
        raise HTTPException(422, "Permainan tidak dikenali.")
    quiz = await run_in_threadpool(_quiz_for, db, body.quiz_id, user)
    questions = parse_questions(quiz.questions)
    reason = MODES[body.mode].unplayable_reason(questions)
    if reason:
        raise HTTPException(422, reason)
    room = request.app.state.rooms.create(
        host_id=user.id,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        questions=questions,
        mode_key=body.mode,
        settings=body.settings,
    )
    return {"code": room.code, "slug": room.slug, "link": join_link(request, room.slug)}


@router.get("/rooms/mine")
async def my_rooms(request: Request, user: User = Depends(require_user)) -> dict:
    rooms = sorted(request.app.state.rooms.rooms_of(user.id), key=lambda r: -r.created)
    return {
        "rooms": [
            {**room.info(), "link": join_link(request, room.slug), "players": len(room.players)} for room in rooms
        ]
    }


@router.get("/rooms/{key}")
async def room_info(key: str, request: Request) -> dict:
    limit(request, "room-lookup", 60, 60)
    room = _room_or_404(request, key)
    return {**room.info(), "link": join_link(request, room.slug)}


@router.get("/rooms/{key}/qr.svg")
async def room_qr(key: str, request: Request) -> Response:
    room = _room_or_404(request, key)
    out = BytesIO()
    segno.make(join_link(request, room.slug), error="m").save(
        out, kind="svg", scale=8, border=2, dark="#1E2A2E", light="#FFFFFF", xmldecl=False, svgns=True
    )
    return Response(out.getvalue(), media_type="image/svg+xml", headers={"Cache-Control": "no-store"})


@router.get("/rooms/{key}/picture/{token}")
async def room_picture(key: str, token: str, request: Request) -> Response:
    """The hidden picture in Teka Gambar, by a per-round token, so the picture's name never travels."""
    data = _room_or_404(request, key).picture(token)
    if data is None:
        raise HTTPException(404, "Gambar tidak dijumpai.")
    return Response(data, media_type="image/svg+xml", headers={"Cache-Control": "no-store"})
