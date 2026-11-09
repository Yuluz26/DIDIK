"""Owner-only membership operations and manual QR payment review."""

from __future__ import annotations

import base64
import io
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session
from PIL import Image

from ..activity import aware, iso
from ..deps import get_db
from ..membership import PRICES, add_months, current
from ..models import (BillingSettings, ChildProfile, EntitlementOverride, MembershipAudit,
                      MembershipGrant, PaidSubscription, PaymentRequest, User)
from ..seed import DEMO_EMAIL, LIBRARY_EMAIL
from .auth import require_admin, settings_of

router = APIRouter(prefix="/api/membership", dependencies=[Depends(require_admin)])
SYSTEM = {DEMO_EMAIL, LIBRARY_EMAIL}


def parent_or_404(db: Session, parent_id: int) -> User:
    user = db.get(User, parent_id)
    if user is None or user.email in SYSTEM:
        raise HTTPException(404, "Ibu bapa tidak dijumpai.")
    return user


def audit(db: Session, request: Request, user: User, action: str, before: dict, after: dict, note: str = "") -> None:
    db.add(MembershipAudit(parent_id=user.id, actor=settings_of(request).email, action=action,
                           before=before, after=after, note=note))


@router.get("/overview")
def overview(db: Session = Depends(get_db)) -> dict:
    users = list(db.scalars(select(User).where(User.email.not_in(SYSTEM))))
    states = [current(db, user) for user in users]
    now = datetime.now(UTC)
    paid = list(db.scalars(select(PaidSubscription).where(PaidSubscription.status == "active")))
    grants = list(db.scalars(select(MembershipGrant).where(MembershipGrant.status == "active")))
    return {"totalParents": len(users), "free": sum(s["plan"] == "free" for s in states),
            "premium": sum(s["plan"] == "premium" for s in states),
            "family": sum(s["plan"] == "family" for s in states),
            "activePaid": sum(aware(p.starts_at) <= now < aware(p.expires_at) for p in paid),
            "activeGrants": sum(aware(g.starts_at) <= now and (g.expires_at is None or now < aware(g.expires_at)) for g in grants),
            "pendingPayments": db.scalar(select(func.count()).select_from(PaymentRequest).where(PaymentRequest.status == "pending")) or 0,
            "mrrSen": sum(p.price_sen // (12 if p.interval == "yearly" else 1) for p in paid if aware(p.starts_at) <= now < aware(p.expires_at))}


@router.get("/parents")
def parents(q: str = "", plan: str = "", page: int = 1, db: Session = Depends(get_db)) -> dict:
    where = [User.email.not_in(SYSTEM)]
    if q.strip():
        needle = q.strip().lower()
        where.append(or_(func.lower(User.name).contains(needle, autoescape=True), func.lower(User.email).contains(needle, autoescape=True)))
    rows = list(db.scalars(select(User).where(*where).order_by(User.id.desc())))
    items = [{"id": u.id, "name": u.name, "email": u.email, "createdAt": iso(u.created_at),
              "lastActivityAt": iso(u.last_login_at), "membership": current(db, u)} for u in rows]
    if plan in PRICES:
        items = [item for item in items if item["membership"]["plan"] == plan]
    page = max(1, page)
    return {"items": items[(page - 1) * 25:page * 25], "total": len(items), "page": page, "per": 25}


@router.get("/parents/{parent_id}")
def parent_detail(parent_id: int, db: Session = Depends(get_db)) -> dict:
    user = parent_or_404(db, parent_id)
    children = list(db.scalars(select(ChildProfile).where(ChildProfile.parent_id == parent_id).order_by(ChildProfile.id)))
    paid = list(db.scalars(select(PaidSubscription).where(PaidSubscription.parent_id == parent_id).order_by(PaidSubscription.id.desc())))
    grants = list(db.scalars(select(MembershipGrant).where(MembershipGrant.parent_id == parent_id).order_by(MembershipGrant.id.desc())))
    overrides = list(db.scalars(select(EntitlementOverride).where(EntitlementOverride.parent_id == parent_id).order_by(EntitlementOverride.id.desc())))
    payments = list(db.scalars(select(PaymentRequest).where(PaymentRequest.parent_id == parent_id).order_by(PaymentRequest.id.desc())))
    logs = list(db.scalars(select(MembershipAudit).where(MembershipAudit.parent_id == parent_id).order_by(MembershipAudit.id.desc()).limit(100)))
    return {"id": user.id, "name": user.name, "email": user.email, "createdAt": iso(user.created_at),
            "lastActivityAt": iso(user.last_login_at), "membership": current(db, user),
            "children": [{"id": c.id, "name": c.name, "schoolYear": c.school_year, "selected": c.selected} for c in children],
            "paid": [{"id": p.id, "plan": p.plan, "interval": p.interval, "priceSen": p.price_sen, "status": p.status,
                      "startsAt": iso(p.starts_at), "expiresAt": iso(p.expires_at)} for p in paid],
            "grants": [{"id": g.id, "plan": g.plan, "status": g.status, "startsAt": iso(g.starts_at),
                        "expiresAt": iso(g.expires_at), "note": g.note} for g in grants],
            "overrides": [{"id": o.id, "feature": o.feature, "enabled": o.enabled, "valueInt": o.value_int, "startsAt": iso(o.starts_at),
                           "expiresAt": iso(o.expires_at), "note": o.note} for o in overrides],
            "payments": [{"id": p.id, "reference": p.reference, "plan": p.plan, "interval": p.interval,
                          "amountSen": p.amount_sen, "status": p.status, "createdAt": iso(p.created_at),
                          "reviewedAt": iso(p.reviewed_at), "reviewNote": p.review_note} for p in payments],
            "history": [{"at": iso(a.at), "actor": a.actor, "action": a.action, "before": a.before,
                         "after": a.after, "note": a.note} for a in logs]}


class GrantIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    plan: Literal["free", "premium", "family"]
    starts_at: datetime
    expires_at: datetime | None = None
    note: str = Field(min_length=3, max_length=500)
    selected_child_id: int | None = None

    @model_validator(mode="after")
    def valid_dates(self):
        if self.expires_at is not None and self.expires_at <= self.starts_at:
            raise ValueError("Tarikh tamat mesti selepas tarikh mula.")
        return self


@router.post("/parents/{parent_id}/grants", status_code=201)
def grant(parent_id: int, body: GrantIn, request: Request, db: Session = Depends(get_db)) -> dict:
    user = parent_or_404(db, parent_id)
    before = current(db, user)
    children = list(db.scalars(select(ChildProfile).where(ChildProfile.parent_id == parent_id).order_by(ChildProfile.id)))
    if body.plan != "family" and len(children) > 1 and body.selected_child_id not in {c.id for c in children}:
        raise HTTPException(422, "Pilih satu profil anak aktif untuk pelan ini.")
    if body.selected_child_id:
        for child in children:
            child.selected = child.id == body.selected_child_id
    row = MembershipGrant(parent_id=parent_id, plan=body.plan, starts_at=body.starts_at,
                          expires_at=body.expires_at, note=body.note)
    db.add(row)
    db.flush()
    after = current(db, user)
    audit(db, request, user, "grant.created", before, after, body.note)
    db.commit()
    return {"id": row.id, "membership": after}


@router.post("/parents/{parent_id}/grants/{grant_id}/cancel")
def cancel_grant(parent_id: int, grant_id: int, request: Request, db: Session = Depends(get_db)) -> dict:
    user = parent_or_404(db, parent_id)
    row = db.scalar(select(MembershipGrant).where(MembershipGrant.id == grant_id, MembershipGrant.parent_id == parent_id))
    if row is None:
        raise HTTPException(404, "Grant tidak dijumpai.")
    before = current(db, user)
    row.status = "canceled"
    db.flush()
    after = current(db, user)
    audit(db, request, user, "grant.canceled", before, after)
    db.commit()
    return {"membership": after}


class OverrideIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    feature: Literal["story", "games", "premium_quizzes", "premium_levels", "host", "history", "solo", "party", "max_children"]
    enabled: bool
    value_int: int | None = Field(default=None, ge=1, le=3)
    starts_at: datetime
    expires_at: datetime | None = None
    note: str = Field(min_length=3, max_length=500)


@router.post("/parents/{parent_id}/overrides", status_code=201)
def add_override(parent_id: int, body: OverrideIn, request: Request, db: Session = Depends(get_db)) -> dict:
    user = parent_or_404(db, parent_id)
    if body.expires_at and body.expires_at <= body.starts_at:
        raise HTTPException(422, "Tarikh tamat mesti selepas tarikh mula.")
    if body.feature == "max_children" and body.value_int is None:
        raise HTTPException(422, "Pilih had profil anak, satu hingga tiga.")
    if body.feature == "max_children" and not body.enabled:
        raise HTTPException(422, "Had profil khas mesti diaktifkan.")
    before = current(db, user)
    purchased = list(db.scalars(select(PaidSubscription).where(PaidSubscription.parent_id == parent_id,
                     PaidSubscription.status == "active", PaidSubscription.expires_at > body.starts_at)))
    if body.feature == "max_children" and any(p.plan == "family" for p in purchased) and body.value_int < 3:
        raise HTTPException(409, "Had profil daripada langganan berbayar tidak boleh dikurangkan.")
    if not body.enabled and body.feature != "max_children" and purchased:
        raise HTTPException(409, "Akses yang telah dibayar tidak boleh disekat melalui akses khas. Gunakan penggantungan akaun jika perlu.")
    row = EntitlementOverride(parent_id=parent_id, feature=body.feature, enabled=body.enabled,
                              value_int=body.value_int, starts_at=body.starts_at, expires_at=body.expires_at, note=body.note)
    db.add(row)
    db.flush()
    after = current(db, user)
    audit(db, request, user, "entitlement.created", before, after, body.note)
    db.commit()
    return {"id": row.id, "membership": after}


@router.post("/parents/{parent_id}/overrides/{override_id}/cancel")
def cancel_override(parent_id: int, override_id: int, request: Request, db: Session = Depends(get_db)) -> dict:
    user = parent_or_404(db, parent_id)
    row = db.scalar(select(EntitlementOverride).where(EntitlementOverride.id == override_id, EntitlementOverride.parent_id == parent_id))
    if row is None:
        raise HTTPException(404, "Akses khas tidak dijumpai.")
    before = current(db, user)
    row.expires_at = datetime.now(UTC)
    db.flush()
    after = current(db, user)
    audit(db, request, user, "entitlement.canceled", before, after)
    db.commit()
    return {"membership": after}


@router.get("/payments")
def payments(status: str = "pending", page: int = 1, db: Session = Depends(get_db)) -> dict:
    query = select(PaymentRequest, User.name, User.email).join(User, User.id == PaymentRequest.parent_id)
    if status in {"pending", "paid", "rejected"}:
        query = query.where(PaymentRequest.status == status)
    page = max(1, page)
    rows = db.execute(query.order_by(PaymentRequest.id.desc()).offset((page - 1) * 25).limit(25)).all()
    return {"items": [{"id": p.id, "parentId": p.parent_id, "parentName": name, "email": email,
                       "reference": p.reference, "plan": p.plan, "interval": p.interval,
                       "amountSen": p.amount_sen, "status": p.status, "createdAt": iso(p.created_at)}
                      for p, name, email in rows], "page": page}


class ReviewIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    action: Literal["approve", "reject"]
    note: str = Field(min_length=3, max_length=500)


@router.post("/payments/{payment_id}/review")
def review(payment_id: int, body: ReviewIn, request: Request, db: Session = Depends(get_db)) -> dict:
    payment = db.get(PaymentRequest, payment_id)
    if payment is None:
        raise HTTPException(404, "Permintaan bayaran tidak dijumpai.")
    if payment.status != "pending":
        raise HTTPException(409, "Permintaan ini sudah disemak.")
    reserved = db.execute(update(PaymentRequest).where(PaymentRequest.id == payment_id,
                           PaymentRequest.status == "pending").values(status="processing"))
    if reserved.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Permintaan ini sedang atau sudah disemak.")
    user = parent_or_404(db, payment.parent_id)
    before = current(db, user)
    if body.action == "approve":
        # Every request stores the price agreed at checkout; later catalog edits cannot rewrite it.
        if payment.amount_sen != PRICES[payment.plan][payment.interval]:
            raise HTTPException(409, "Harga permintaan tidak sepadan dengan harga rasmi.")
        now = datetime.now(UTC)
        latest = db.scalar(select(PaidSubscription).where(PaidSubscription.parent_id == user.id,
                           PaidSubscription.plan == payment.plan, PaidSubscription.status == "active")
                           .order_by(PaidSubscription.expires_at.desc()).limit(1))
        start = max(now, aware(latest.expires_at)) if latest else now
        end = add_months(start, 12 if payment.interval == "yearly" else 1)
        subscription = PaidSubscription(parent_id=user.id, plan=payment.plan, interval=payment.interval,
                                        price_sen=payment.amount_sen, starts_at=start, expires_at=end)
        db.add(subscription)
        db.flush()
        payment.subscription_id = subscription.id
        payment.status = "paid"
    else:
        payment.status = "rejected"
    payment.reviewed_at = datetime.now(UTC)
    payment.review_note = body.note
    after = current(db, user)
    audit(db, request, user, "payment." + payment.status, before, after, f"{payment.reference}: {body.note}")
    db.commit()
    return {"status": payment.status, "membership": after}


@router.get("/billing")
def billing(db: Session = Depends(get_db)) -> dict:
    row = db.get(BillingSettings, 1)
    return {"qrImage": "/api/membership/qr" if row and row.qr_image else None,
            "payeeName": row.payee_name if row else "", "instructions": row.instructions if row else ""}


class BillingIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    payee_name: str = Field(max_length=120)
    instructions: str = Field(max_length=500)
    qr_png_base64: str | None = None


@router.put("/billing")
def save_billing(body: BillingIn, request: Request, db: Session = Depends(get_db)) -> dict:
    row = db.get(BillingSettings, 1)
    if row is None:
        row = BillingSettings(id=1)
        db.add(row)
    old = {"payeeName": row.payee_name, "instructions": row.instructions, "hasQr": bool(row.qr_image)}
    if body.qr_png_base64 is not None:
        try:
            raw = base64.b64decode(body.qr_png_base64, validate=True)
            if len(raw) > 2_000_000:
                raise ValueError("too large")
            image = Image.open(io.BytesIO(raw))
            image.verify()
            if image.format != "PNG" or image.width > 2400 or image.height > 2400:
                raise ValueError("not png")
        except (ValueError, OSError, base64.binascii.Error):
            raise HTTPException(422, "Muat naik gambar QR PNG yang sah, maksimum 2 MB.") from None
        folder = request.app.state.settings.data_dir / "billing"
        folder.mkdir(parents=True, exist_ok=True)
        filename = secrets.token_hex(16) + ".png"
        (folder / filename).write_bytes(raw)
        previous = row.qr_image
        row.qr_image = filename
    else:
        previous = None
    row.payee_name, row.instructions = body.payee_name, body.instructions
    db.add(MembershipAudit(parent_id=None, actor=settings_of(request).email, action="billing.updated",
                           before=old, after={"payeeName": row.payee_name, "instructions": row.instructions,
                                              "hasQr": bool(row.qr_image)}, note="Tetapan QR"))
    db.commit()
    if previous:
        (request.app.state.settings.data_dir / "billing" / previous).unlink(missing_ok=True)
    return billing(db)
