from __future__ import annotations

from datetime import UTC, datetime, timedelta
import base64
import io

from PIL import Image

from sqlalchemy import select

from didik_live.membership import PRICES, current
from didik_live.models import BillingSettings, MembershipAudit, MembershipGrant, PaidSubscription, PaymentRequest, User

from .test_admin import P, OWNER, outbox, sign_in, site  # noqa: F401


def register(site, email="member@example.test"):
    response = site.post("/api/auth/register", json={"name": "Ibu Test", "email": email, "password": "password123"})
    assert response.status_code == 201, response.text
    return response.json()["user"]["id"]


def test_prices_and_free_child_limit(site):
    assert PRICES == {"free": {"monthly": 0, "yearly": 0}, "premium": {"monthly": 1490, "yearly": 14900}, "family": {"monthly": 2490, "yearly": 24900}}
    register(site)
    assert site.get("/api/membership/me").json()["membership"]["plan"] == "free"
    assert site.post("/api/membership/children", json={"name": "Ani", "school_year": 4}).status_code == 201
    assert site.post("/api/membership/children", json={"name": "Ali"}).status_code == 403


def test_admin_grant_expiry_and_paid_overlap(site):
    user_id = register(site)
    now = datetime.now(UTC)
    with site.app.state.db.sessions() as db:
        db.add(PaidSubscription(parent_id=user_id, plan="premium", interval="monthly", price_sen=1490,
                                starts_at=now - timedelta(days=1), expires_at=now + timedelta(days=20)))
        db.commit()
    assert site.get("/api/membership/me").json()["membership"]["plan"] == "premium"
    sign_in(site)
    response = site.post(f"{P}/api/membership/parents/{user_id}/grants", json={
        "plan": "family", "starts_at": now.isoformat(), "expires_at": (now + timedelta(days=5)).isoformat(),
        "note": "Hadiah keluarga sementara"})
    assert response.status_code == 201, response.text
    assert response.json()["membership"]["plan"] == "family"
    with site.app.state.db.sessions() as db:
        user = db.get(User, user_id)
        assert current(db, user, now + timedelta(days=6))["plan"] == "premium"
        assert db.scalar(select(MembershipAudit).where(MembershipAudit.parent_id == user_id)) is not None


def test_manual_qr_review_is_single_use(site):
    user_id = register(site)
    with site.app.state.db.sessions() as db:
        db.add(BillingSettings(id=1, qr_image="test.png", payee_name="DIDIK"))
        db.commit()
    request = site.post("/api/membership/checkout", json={"plan": "family", "interval": "yearly"})
    assert request.status_code == 201, request.text
    payment = request.json()
    assert payment["amountSen"] == 24900
    assert site.get("/api/membership/me").json()["membership"]["plan"] == "free"
    sign_in(site)
    endpoint = f"{P}/api/membership/payments/{payment['id']}/review"
    approved = site.post(endpoint, json={"action": "approve", "note": "Bukti WhatsApp disemak"})
    assert approved.status_code == 200, approved.text
    assert approved.json()["membership"]["plan"] == "family"
    assert site.post(endpoint, json={"action": "approve", "note": "Cuba sekali lagi"}).status_code == 409
    with site.app.state.db.sessions() as db:
        assert len(list(db.scalars(select(PaidSubscription).where(PaidSubscription.parent_id == user_id)))) == 1


def test_parent_cannot_use_owner_routes(site):
    register(site)
    assert site.get(f"{P}/api/membership/parents").status_code == 401
    assert site.post("/api/rooms", json={"quiz_id": 1, "mode": "legenda"}).status_code == 403


def test_qr_admin_upload_and_family_profiles_survive_downgrade(site):
    user_id = register(site, "family@example.test")
    image = Image.new("RGB", (64, 64), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    sign_in(site)
    saved = site.put(f"{P}/api/membership/billing", json={"payee_name": "DIDIK", "instructions": "Bayar jumlah tepat",
        "qr_png_base64": base64.b64encode(buffer.getvalue()).decode()})
    assert saved.status_code == 200, saved.text
    assert site.get("/api/membership/qr").headers["content-type"].startswith("image/png")
    now = datetime.now(UTC)
    family = site.post(f"{P}/api/membership/parents/{user_id}/grants", json={"plan": "family", "starts_at": now.isoformat(),
        "expires_at": (now + timedelta(days=10)).isoformat(), "note": "Akses keluarga ujian"})
    assert family.status_code == 201, family.text
    for name in ("Ani", "Ali", "Abu"):
        assert site.post("/api/membership/children", json={"name": name}).status_code == 201
    assert site.post("/api/membership/children", json={"name": "Amin"}).status_code == 403
    ids = [row["id"] for row in site.get("/api/membership/me").json()["children"]]
    downgrade = site.post(f"{P}/api/membership/parents/{user_id}/grants", json={"plan": "premium", "starts_at": now.isoformat(),
        "expires_at": (now + timedelta(days=20)).isoformat(), "selected_child_id": ids[2], "note": "Pilih satu profil"})
    assert downgrade.status_code == 201, downgrade.text
    # The still-valid Family grant takes precedence; cancel it to reveal the Premium grant.
    grant_id = family.json()["id"]
    assert site.post(f"{P}/api/membership/parents/{user_id}/grants/{grant_id}/cancel").status_code == 200
    state = site.get("/api/membership/me").json()
    assert state["membership"]["plan"] == "premium"
    assert state["membership"]["selectedChildId"] == ids[2]
    assert len(state["children"]) == 3


def test_custom_story_access_does_not_unlock_other_games(site):
    user_id = register(site, "custom@example.test")
    sign_in(site)
    now = datetime.now(UTC)
    expires = now + timedelta(days=2)
    for feature, value in (("story", None), ("max_children", 2)):
        response = site.post(f"{P}/api/membership/parents/{user_id}/overrides", json={
            "feature": feature, "enabled": True, "value_int": value, "starts_at": now.isoformat(),
            "expires_at": expires.isoformat(), "note": "Akses khas ujian"})
        assert response.status_code == 201, response.text
    state = site.get("/api/membership/me").json()["membership"]
    assert state["plan"] == "free" and state["features"]["story"] is True
    assert state["features"]["games"] is False and state["childLimit"] == 2
    assert site.post("/api/membership/children", json={"name": "Satu"}).status_code == 201
    assert site.post("/api/membership/children", json={"name": "Dua"}).status_code == 201
