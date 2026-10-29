"""A parent's quizzes: list, write, copy, delete. Sample quizzes can be read and copied by any parent."""

from __future__ import annotations

from collections import Counter
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..deps import get_db, limit, require_user
from ..models import Quiz, User
from ..questions import MAX_QUESTIONS, Question, unique_ids

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


class QuizIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    questions: list[Question] = Field(default_factory=list, max_length=MAX_QUESTIONS)

    @model_validator(mode="after")
    def _ids(self) -> QuizIn:
        unique_ids(self.questions)
        return self


def summary(quiz: Quiz) -> dict[str, Any]:
    types = Counter(q.get("type") for q in quiz.questions)
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "questionCount": len(quiz.questions),
        "types": dict(types),
        "isSample": quiz.is_sample,
        "updatedAt": quiz.updated_at.isoformat() if quiz.updated_at else None,
    }


def full(quiz: Quiz, user: User) -> dict[str, Any]:
    return {**summary(quiz), "questions": quiz.questions, "canEdit": quiz.owner_id == user.id}


def _readable(db: Session, quiz_id: int, user: User) -> Quiz:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None or (quiz.owner_id != user.id and not quiz.is_sample):
        raise HTTPException(404, "Kuiz tidak dijumpai.")
    return quiz


def _own(db: Session, quiz_id: int, user: User) -> Quiz:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None or quiz.owner_id != user.id:
        raise HTTPException(404, "Kuiz tidak dijumpai.")
    return quiz


@router.get("")
def index(user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(
        select(Quiz).where(or_(Quiz.owner_id == user.id, Quiz.is_sample.is_(True))).order_by(Quiz.updated_at.desc())
    ).all()
    mine = [summary(q) for q in rows if q.owner_id == user.id]
    samples = [summary(q) for q in rows if q.is_sample and q.owner_id != user.id]
    return {"mine": mine, "samples": samples}


@router.post("", status_code=201)
def store(body: QuizIn, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    limit(request, "quiz-write", 60, 60, key=str(user.id))
    quiz = Quiz(
        owner_id=user.id,
        title=body.title,
        description=body.description,
        questions=[q.model_dump() for q in body.questions],
    )
    db.add(quiz)
    db.commit()
    request.app.state.bus.emit("quiz.created", f"{user.name} cipta kuiz “{quiz.title}”", quizId=quiz.id, title=quiz.title, owner=user.name, questions=len(quiz.questions))
    return full(quiz, user)


@router.get("/{quiz_id}")
def show(quiz_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    return full(_readable(db, quiz_id, user), user)


@router.put("/{quiz_id}")
def update(
    quiz_id: int, body: QuizIn, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)
) -> dict:
    limit(request, "quiz-write", 60, 60, key=str(user.id))
    quiz = _own(db, quiz_id, user)
    quiz.title = body.title
    quiz.description = body.description
    quiz.questions = [q.model_dump() for q in body.questions]
    db.commit()
    request.app.state.bus.emit(
        "quiz.updated", f"{user.name} kemas kini kuiz “{quiz.title}”", coalesce=(quiz.id, 300), quizId=quiz.id, title=quiz.title, owner=user.name, questions=len(quiz.questions)
    )
    return full(quiz, user)


@router.post("/{quiz_id}/copy", status_code=201)
def copy(quiz_id: int, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    source = _readable(db, quiz_id, user)
    title = source.title if source.owner_id != user.id else f"{source.title} (salinan)"
    quiz = Quiz(owner_id=user.id, title=title[:120], description=source.description, questions=list(source.questions))
    db.add(quiz)
    db.commit()
    request.app.state.bus.emit("quiz.created", f"{user.name} salin kuiz “{quiz.title}”", quizId=quiz.id, title=quiz.title, owner=user.name, questions=len(quiz.questions), copy=True)
    return full(quiz, user)


@router.delete("/{quiz_id}", status_code=204)
def destroy(quiz_id: int, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> Response:
    quiz = _own(db, quiz_id, user)
    title = quiz.title
    db.delete(quiz)
    db.commit()
    request.app.state.bus.emit("quiz.deleted", f"{user.name} padam kuiz “{title}”", quizId=quiz_id, title=title, owner=user.name)
    return Response(status_code=204)
