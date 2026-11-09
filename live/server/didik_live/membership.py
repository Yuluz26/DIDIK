"""Membership rules. Prices are fixed in sen; paid terms and admin grants stay separate."""

from __future__ import annotations

from calendar import monthrange
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .activity import aware, iso
from .models import ChildProfile, EntitlementOverride, MembershipGrant, PaidSubscription, User

PRICES = {
    "free": {"monthly": 0, "yearly": 0},
    "premium": {"monthly": 1490, "yearly": 14900},
    "family": {"monthly": 2490, "yearly": 24900},
}
RANK = {"free": 0, "premium": 1, "family": 2}
FEATURES = {"story", "games", "premium_quizzes", "premium_levels", "host", "history", "solo", "party"}


def add_months(value: datetime, count: int) -> datetime:
    month = value.month - 1 + count
    year, month = value.year + month // 12, month % 12 + 1
    return value.replace(year=year, month=month, day=min(value.day, monthrange(year, month)[1]))


def current(db: Session, user: User, now: datetime | None = None) -> dict:
    now = now or datetime.now(UTC)
    paid = [row for row in db.scalars(select(PaidSubscription).where(PaidSubscription.parent_id == user.id, PaidSubscription.status == "active"))
            if aware(row.starts_at) <= now < aware(row.expires_at)]
    # The newest started admin decision supersedes older grants, even after it expires.
    # That prevents an old complimentary term from silently reappearing after a downgrade.
    decisions = [row for row in db.scalars(select(MembershipGrant).where(MembershipGrant.parent_id == user.id))
                 if aware(row.starts_at) <= now]
    best_paid = max(paid, key=lambda row: (RANK[row.plan], aware(row.expires_at)), default=None)
    latest_grant = max(decisions, key=lambda row: (aware(row.starts_at), row.id), default=None)
    best_grant = latest_grant if latest_grant and latest_grant.status == "active" and (
        latest_grant.expires_at is None or now < aware(latest_grant.expires_at)) else None
    plan = max((best_paid.plan if best_paid else "free", best_grant.plan if best_grant else "free"), key=RANK.get)
    overrides = {row.feature: row for row in db.scalars(select(EntitlementOverride).where(EntitlementOverride.parent_id == user.id).order_by(EntitlementOverride.id))
                 if aware(row.starts_at) <= now and (row.expires_at is None or now < aware(row.expires_at))}
    features = {key: plan != "free" for key in FEATURES}
    features.update({key: row.enabled for key, row in overrides.items() if key in FEATURES})
    if user.disabled_at is not None:
        features = {key: False for key in FEATURES}
    active_children = list(db.scalars(select(ChildProfile).where(ChildProfile.parent_id == user.id).order_by(ChildProfile.id)))
    limit = overrides["max_children"].value_int if "max_children" in overrides else (3 if plan == "family" else 1)
    return {
        "plan": plan,
        "source": "paid" if best_paid and RANK[best_paid.plan] >= RANK[best_grant.plan if best_grant else "free"] else "complimentary" if best_grant else "free",
        "interval": best_paid.interval if best_paid and plan == best_paid.plan else None,
        "expiresAt": iso(best_paid.expires_at if best_paid and plan == best_paid.plan else best_grant.expires_at if best_grant else None),
        "features": features,
        "childLimit": limit,
        "childCount": len(active_children),
        "selectedChildId": next((child.id for child in active_children if child.selected), None),
        "suspended": user.disabled_at is not None,
        "paidSubscriptionId": best_paid.id if best_paid else None,
    }


def can(db: Session, user: User, feature: str) -> bool:
    return current(db, user)["features"].get(feature, False)


def expire_records(db: Session, now: datetime | None = None) -> None:
    """Keep lifecycle labels in sync; entitlement checks are time-aware even between runs."""
    now = now or datetime.now(UTC)
    db.execute(update(PaidSubscription).where(PaidSubscription.status == "active", PaidSubscription.expires_at <= now)
               .values(status="expired"))
    db.execute(update(MembershipGrant).where(MembershipGrant.status == "active", MembershipGrant.expires_at.is_not(None),
               MembershipGrant.expires_at <= now).values(status="expired"))
    db.commit()
