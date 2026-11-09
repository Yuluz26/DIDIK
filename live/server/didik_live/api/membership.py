"""Parent membership, child profiles, and manual QR payment requests."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..activity import iso
from ..deps import get_db, limit, require_user
from ..membership import PRICES, current
from ..models import BillingSettings, ChildProfile, PaymentRequest, User

router = APIRouter(prefix="/api/membership", tags=["membership"])
WHATSAPP = "60139558132"


def payment_out(row: PaymentRequest) -> dict:
    return {"id": row.id, "reference": row.reference, "plan": row.plan, "interval": row.interval,
            "amountSen": row.amount_sen, "status": row.status, "createdAt": iso(row.created_at),
            "reviewedAt": iso(row.reviewed_at), "reviewNote": row.review_note}


@router.get("/plans")
def plans() -> dict:
    return {"plans": [{"key": key, "pricesSen": prices, "childLimit": 3 if key == "family" else 1}
                      for key, prices in PRICES.items()], "currency": "MYR"}


@router.get("/me")
def mine(user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    billing = db.get(BillingSettings, 1)
    children = list(db.scalars(select(ChildProfile).where(ChildProfile.parent_id == user.id).order_by(ChildProfile.id)))
    payments = list(db.scalars(select(PaymentRequest).where(PaymentRequest.parent_id == user.id).order_by(PaymentRequest.id.desc())))
    return {"membership": current(db, user), "pricesSen": PRICES,
            "children": [{"id": c.id, "name": c.name, "schoolYear": c.school_year, "selected": c.selected} for c in children],
            "payments": [payment_out(p) for p in payments],
            "billing": {"qrImage": f"/api/membership/qr" if billing and billing.qr_image else None,
                        "payeeName": billing.payee_name if billing else "",
                        "instructions": billing.instructions if billing else "", "whatsapp": WHATSAPP}}


class ChildIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=60)
    school_year: int | None = Field(default=None, ge=1, le=6)


@router.post("/children", status_code=201)
def add_child(body: ChildIn, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    state = current(db, user)
    if state["childCount"] >= state["childLimit"]:
        raise HTTPException(403, "Had profil anak telah dicapai. Pilih Family untuk sehingga tiga profil.")
    child = ChildProfile(parent_id=user.id, name=body.name, school_year=body.school_year,
                         selected=state["childCount"] == 0)
    db.add(child)
    db.commit()
    return {"id": child.id, "name": child.name, "schoolYear": child.school_year, "selected": child.selected}


@router.patch("/children/{child_id}")
def update_child(child_id: int, body: ChildIn, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    child = db.scalar(select(ChildProfile).where(ChildProfile.id == child_id, ChildProfile.parent_id == user.id))
    if child is None:
        raise HTTPException(404, "Profil anak tidak dijumpai.")
    child.name, child.school_year = body.name, body.school_year
    db.commit()
    return {"id": child.id, "name": child.name, "schoolYear": child.school_year, "selected": child.selected}


@router.post("/children/{child_id}/select")
def select_child(child_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    children = list(db.scalars(select(ChildProfile).where(ChildProfile.parent_id == user.id).order_by(ChildProfile.id)))
    if child_id not in {child.id for child in children}:
        raise HTTPException(403, "Profil ini tidak tersedia untuk pelan semasa.")
    for child in children:
        child.selected = child.id == child_id
    db.commit()
    return {"selectedChildId": child_id}


class CheckoutIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan: Literal["premium", "family"]
    interval: Literal["monthly", "yearly"]


@router.post("/checkout", status_code=201)
def checkout(body: CheckoutIn, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    limit(request, "membership-checkout", 10, 3600, key=str(user.id))
    billing = db.get(BillingSettings, 1)
    if billing is None or not billing.qr_image:
        raise HTTPException(503, "Pembayaran QR belum tersedia. Cuba lagi kemudian.")
    row = PaymentRequest(parent_id=user.id, reference="DIDIK-" + secrets.token_hex(5).upper(),
                         plan=body.plan, interval=body.interval, amount_sen=PRICES[body.plan][body.interval])
    db.add(row)
    db.commit()
    return payment_out(row)


@router.get("/qr")
def qr(request: Request, db: Session = Depends(get_db)):
    from fastapi.responses import FileResponse
    billing = db.get(BillingSettings, 1)
    if billing is None or not billing.qr_image:
        raise HTTPException(404, "QR belum tersedia.")
    path = request.app.state.settings.data_dir / "billing" / billing.qr_image
    if not path.is_file():
        raise HTTPException(404, "QR belum tersedia.")
    return FileResponse(path, media_type="image/png", headers={"Cache-Control": "no-store"})
