"""The owner's control room: invisible without its secret address, a sign-in code by email, and a live dashboard."""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from starlette.websockets import WebSocketDisconnect

from didik_live.app import create_app
from didik_live.config import AdminSettings, MailSettings, Settings, load_settings
from didik_live.mailer import Mailer
from didik_live.models import ActivityEvent, AdminNotification, AdminOtp, AdminSession, Quiz, User

from .conftest import sample_id, wait_until

OWNER = "owner@example.test"
PATH = "k3y-0f-the-control-room-Z9x8w7v6"
P = f"/{PATH}"
ADMIN = AdminSettings(email=OWNER, path=PATH)
MAIL = MailSettings(host="smtp.example.test", port=587, user="", password="", security="starttls", sender="didik@example.test")
HERE = {"origin": "http://testserver"}


class Outbox(Mailer):
    def __init__(self) -> None:
        super().__init__(MAIL)
        self.sent: list[tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> bool:
        self.sent.append((to, subject, body))
        return True

    def code(self) -> str:
        return re.search(r"\b(\d{6})\b", self.sent[-1][2]).group(1)  # type: ignore[union-attr]


@pytest.fixture
def site(settings: Settings) -> TestClient:
    app = create_app(replace(settings, admin=ADMIN))
    app.state.mailer = Outbox()
    with TestClient(app) as client:
        client.headers["x-didik-admin"] = "1"
        yield client


def outbox(site: TestClient) -> Outbox:
    return site.app.state.mailer


def sign_in(site: TestClient) -> None:
    assert site.post(f"{P}/api/otp", json={"email": OWNER}).status_code == 202
    answer = site.post(f"{P}/api/verify", json={"email": OWNER, "code": outbox(site).code()})
    assert answer.status_code == 200, answer.text
    site.app.state.limiter.reset()


def rows(site: TestClient, model, *where):
    with site.app.state.db.sessions() as db:
        return list(db.scalars(select(model).where(*where)))


def events(site: TestClient, kind: str) -> list[ActivityEvent]:
    return rows(site, ActivityEvent, ActivityEvent.kind == kind)


# ---------------------------------------------------------------- the secret address


def test_without_the_settings_there_is_no_control_room(client: TestClient) -> None:
    # nothing is mounted: the secret path answers exactly like any other address
    assert client.post(f"{P}/api/otp", json={"email": OWNER}).status_code == client.post("/api/nothing-here").status_code
    assert client.get(P).text == client.get("/some/other/address").text
    assert client.app.state.settings.admin is None


def test_another_address_shows_nothing_of_the_control_room(site: TestClient) -> None:
    other = site.get("/not-the-secret-path")
    assert "kod" not in other.text.lower() and other.status_code == site.get("/another-one").status_code
    assert site.post("/not-the-secret-path/api/otp", json={"email": OWNER}).status_code in (404, 405)
    assert outbox(site).sent == []


def test_the_secret_address_shows_sign_in_until_signed_in(site: TestClient) -> None:
    page = site.get(P)
    assert page.status_code == 200 and 'id="ask"' in page.text and 'id="nav"' not in page.text
    assert f'data-base="{P}"' in page.text and "__BASE__" not in page.text  # the files are named by absolute address
    assert site.get(f"{P}/_/login.js").status_code == 200  # the sign-in page's own files
    assert site.get(f"{P}/_/app.js").status_code == 404  # the dashboard's files are for a session only
    for private in ("overview", "users", "quizzes", "notifications", "activity", "security", "live", "me"):
        assert site.get(f"{P}/api/{private}").status_code == 401, private

    sign_in(site)
    dashboard = site.get(P).text
    assert 'id="nav"' in dashboard and 'id="ask"' not in dashboard and f'src="{P}/_/app.js"' in dashboard
    assert site.get(f"{P}/_/app.js").status_code == 200
    # only plain names of the three file kinds are ever read from the folder
    for name in ("not-there.js", "app.py", "app.html", "__init__.py", "Admin.css"):
        assert site.get(f"{P}/_/{name}").status_code == 404, name


def test_every_control_room_response_is_private(site: TestClient) -> None:
    for response in (site.get(P), site.get(f"{P}/_/login.js"), site.get(f"{P}/api/me")):
        assert response.headers["cache-control"] == "no-store"
        assert "noindex" in response.headers["x-robots-tag"]
        assert "script-src 'self'" in response.headers["content-security-policy"]
    sign_in(site)
    assert site.get(f"{P}/_/admin.css").headers["cache-control"] == "no-store"
    # the rest of the site is not affected
    assert "x-robots-tag" not in site.get("/api/health").headers


# ---------------------------------------------------------------- the code


def test_the_owner_gets_a_code_and_anyone_else_gets_the_same_answer_and_nothing(site: TestClient) -> None:
    other = site.post(f"{P}/api/otp", json={"email": "someone@else.test"})
    assert outbox(site).sent == []
    mine = site.post(f"{P}/api/otp", json={"email": f" {OWNER.upper()} "})
    assert other.status_code == mine.status_code == 202 and other.json() == mine.json()
    to, subject, body = outbox(site).sent[-1]
    assert to == OWNER and "kod log masuk" in subject.lower() and "10 minit" in body and re.search(r"\b\d{6}\b", body)
    assert rows(site, AdminOtp)[0].code_hash.startswith("scrypt$")  # only a hash is kept


def test_a_code_signs_in_once_and_the_cookie_belongs_to_the_secret_path(site: TestClient) -> None:
    site.post(f"{P}/api/otp", json={"email": OWNER})
    code = outbox(site).code()
    wrong = "000000" if code != "000000" else "111111"
    refused = site.post(f"{P}/api/verify", json={"email": OWNER, "code": wrong})
    assert refused.status_code == 422 and "tidak sah" in refused.json()["message"]
    assert site.get(f"{P}/api/me").status_code == 401

    answer = site.post(f"{P}/api/verify", json={"email": OWNER, "code": code})
    assert answer.status_code == 200
    cookie = answer.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie and f"path={P}".lower() in cookie
    assert site.get(f"{P}/api/me").json()["email"] == OWNER

    # used up: the same code does nothing the second time
    site.app.state.limiter.reset()
    assert site.post(f"{P}/api/verify", json={"email": OWNER, "code": code}).status_code == 422
    # every sign-in is told to the owner
    assert any("log masuk admin" in subject.lower() for _, subject, _ in outbox(site).sent[1:])
    assert events(site, "admin.signin")[0].data["newIp"] is True


def test_the_right_code_with_the_wrong_email_does_not_sign_in(site: TestClient) -> None:
    site.post(f"{P}/api/otp", json={"email": OWNER})
    assert site.post(f"{P}/api/verify", json={"email": "x@else.test", "code": outbox(site).code()}).status_code == 422
    assert site.get(f"{P}/api/me").status_code == 401


def test_five_wrong_tries_end_the_code_even_for_the_right_one(site: TestClient) -> None:
    site.post(f"{P}/api/otp", json={"email": OWNER})
    code = outbox(site).code()
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(5):
        assert site.post(f"{P}/api/verify", json={"email": OWNER, "code": wrong}).status_code == 422
        site.app.state.limiter.reset()
    assert site.post(f"{P}/api/verify", json={"email": OWNER, "code": code}).status_code == 422
    assert site.get(f"{P}/api/me").status_code == 401


def test_an_old_code_does_not_work_and_a_new_one_waits_a_minute(site: TestClient) -> None:
    site.post(f"{P}/api/otp", json={"email": OWNER})
    first = outbox(site).code()
    site.post(f"{P}/api/otp", json={"email": OWNER})  # inside the cooldown: no second email
    assert len(outbox(site).sent) == 1

    with site.app.state.db.sessions() as db:  # time passes: the code is old, and a new one may be asked for
        db.execute(update(AdminOtp).values(created_at=datetime.now(UTC) - timedelta(minutes=11), expires_at=datetime.now(UTC) - timedelta(minutes=1)))
        db.commit()
    assert site.post(f"{P}/api/verify", json={"email": OWNER, "code": first}).status_code == 422
    site.post(f"{P}/api/otp", json={"email": OWNER})
    assert len(outbox(site).sent) == 2
    assert site.post(f"{P}/api/verify", json={"email": OWNER, "code": first}).status_code == 422 or first == outbox(site).code()
    assert len(rows(site, AdminOtp)) == 1  # one code in force at a time


def test_asking_for_codes_and_guessing_them_are_limited(site: TestClient) -> None:
    answers = [site.post(f"{P}/api/otp", json={"email": "a@else.test"}).status_code for _ in range(7)]
    assert answers[:5] == [202] * 5 and answers[5] == 429
    site.app.state.limiter.reset()
    tries = [site.post(f"{P}/api/verify", json={"email": OWNER, "code": "123456"}).status_code for _ in range(12)]
    assert tries[:10] == [422] * 10 and 429 in tries[10:]


def test_the_code_must_be_six_digits(site: TestClient) -> None:
    for bad in ("12345", "1234567", "abcdef", ""):
        assert site.post(f"{P}/api/verify", json={"email": OWNER, "code": bad}).status_code == 422


# ---------------------------------------------------------------- sessions


def test_changes_need_the_header_and_the_sites_own_origin(site: TestClient) -> None:
    sign_in(site)
    body = {"title": "Nota", "body": "", "level": "info", "pinned": False}
    assert site.post(f"{P}/api/notifications", json=body, headers={"x-didik-admin": ""}).status_code == 403
    assert site.post(f"{P}/api/notifications", json=body, headers={"origin": "https://evil.example"}).status_code == 403
    assert site.post(f"{P}/api/notifications", json=body, headers={"sec-fetch-site": "cross-site"}).status_code == 403
    assert site.post(f"{P}/api/notifications", json=body, headers=HERE).status_code == 201


def test_sessions_end_by_logout_by_revoking_and_by_age(site: TestClient) -> None:
    sign_in(site)
    me = site.get(f"{P}/api/me").json()
    security = site.get(f"{P}/api/security").json()
    assert [s["current"] for s in security["sessions"]] == [True]
    assert site.delete(f"{P}/api/sessions/{me['sessionId']}").status_code == 400  # not the one in use

    # a second browser signs in, then the first one revokes it
    other = TestClient(site.app, headers={"x-didik-admin": "1"})
    other.post(f"{P}/api/otp", json={"email": OWNER})
    other.post(f"{P}/api/verify", json={"email": OWNER, "code": outbox(site).code()})
    assert other.get(f"{P}/api/me").status_code == 200
    site.app.state.limiter.reset()
    assert len(site.get(f"{P}/api/security").json()["sessions"]) == 2
    assert site.post(f"{P}/api/sessions/revoke-others").status_code == 204
    assert other.get(f"{P}/api/me").status_code == 401 and site.get(f"{P}/api/me").status_code == 200

    # idle too long: asks for a new code
    with site.app.state.db.sessions() as db:
        db.execute(update(AdminSession).values(last_seen_at=datetime.now(UTC) - timedelta(hours=5)))
        db.commit()
    assert site.get(f"{P}/api/me").status_code == 401

    sign_in(site)
    assert site.post(f"{P}/api/logout").status_code == 204
    assert site.get(f"{P}/api/me").status_code == 401


def test_a_parents_cookie_is_no_key_to_the_control_room(site: TestClient) -> None:
    site.post("/api/auth/login", json={"email": "demo@didik.test", "password": "main-bersama"})
    assert site.get(f"{P}/api/me").status_code == 401


# ---------------------------------------------------------------- parents


def test_parents_appear_in_the_log_and_in_notifications_and_can_be_suspended_and_deleted(site: TestClient) -> None:
    sign_in(site)
    parent = TestClient(site.app)
    assert parent.post("/api/auth/register", json={"name": "Puan Aminah", "email": "aminah@example.test", "password": "rahsia-123"}).status_code == 201
    wait_until(lambda: events(site, "user.signup"))
    assert events(site, "user.signup")[0].data["email"] == "aminah@example.test"
    notes = site.get(f"{P}/api/notifications").json()
    titles = {n["title"]: n for n in notes["items"]}
    # the owner's first sign-in from a new address warns too; the signup is a notification of its own
    assert set(titles) == {"Ibu bapa baharu", "Log masuk admin dari alamat baharu"} and notes["unread"] == 2
    assert titles["Ibu bapa baharu"]["source"] == "system" and titles["Log masuk admin dari alamat baharu"]["level"] == "warning"

    listing = site.get(f"{P}/api/users").json()
    assert [u["email"] for u in listing["items"]] == ["aminah@example.test"]  # no demo, no sample library
    uid = listing["items"][0]["id"]
    assert site.get(f"{P}/api/users?q=AMIN").json()["total"] == 1 and site.get(f"{P}/api/users?q=zzz").json()["total"] == 0
    assert site.get(f"{P}/api/users?q=%25").json()["total"] == 0  # a % is text, not a wildcard

    assert site.patch(f"{P}/api/users/{uid}", json={"name": "Puan Aminah Ali"}).json()["name"] == "Puan Aminah Ali"
    assert site.patch(f"{P}/api/users/{uid}", json={"nope": 1}).status_code == 422

    assert site.patch(f"{P}/api/users/{uid}", json={"disabled": True}).json()["disabled"] is True
    refused = parent.post("/api/auth/login", json={"email": "aminah@example.test", "password": "rahsia-123"})
    assert refused.status_code == 403 and "digantung" in refused.json()["message"]
    assert parent.get("/api/auth/me").json()["user"] is None  # the open session ended too
    assert site.get(f"{P}/api/users?status=suspended").json()["total"] == 1
    assert site.patch(f"{P}/api/users/{uid}", json={"disabled": False}).json()["disabled"] is False
    assert parent.post("/api/auth/login", json={"email": "aminah@example.test", "password": "rahsia-123"}).status_code == 200
    assert site.get(f"{P}/api/users/{uid}").json()["lastLoginAt"]

    assert site.delete(f"{P}/api/users/{uid}").status_code == 204
    assert site.get(f"{P}/api/users/{uid}").status_code == 404
    assert parent.get("/api/auth/me").json()["user"] is None
    wait_until(lambda: events(site, "user.deleted"))


def test_the_demo_and_sample_library_accounts_are_protected(site: TestClient) -> None:
    sign_in(site)
    system = site.get(f"{P}/api/users?status=system").json()["items"]
    assert [u["email"] for u in system] == ["demo@didik.test"] and all(u["system"] for u in system)
    for user in system:
        assert site.patch(f"{P}/api/users/{user['id']}", json={"disabled": True}).status_code == 400
        assert site.delete(f"{P}/api/users/{user['id']}").status_code == 400


def test_deleting_a_parent_closes_their_rooms_and_removes_their_pictures(site: TestClient) -> None:
    sign_in(site)
    host = TestClient(site.app)
    host.post("/api/auth/register", json={"name": "Cikgu Lim", "email": "lim@example.test", "password": "rahsia-123"})
    quiz = host.post("/api/quizzes", json={"title": "Kuiz Lim", "questions": []}).json()
    uid = site.get(f"{P}/api/users?q=lim").json()["items"][0]["id"]
    folder = site.app.state.settings.upload_dir
    (folder / "lim.webp").write_bytes(b"x")
    with site.app.state.db.sessions() as db:
        from didik_live.models import Upload

        db.add(Upload(owner_id=uid, filename="lim.webp", width=1, height=1))
        db.commit()
    assert quiz["id"]
    assert site.delete(f"{P}/api/users/{uid}").status_code == 204
    assert not (folder / "lim.webp").exists()
    assert rows(site, Quiz, Quiz.owner_id == uid) == []


# ---------------------------------------------------------------- quizzes


def test_quizzes_can_be_found_edited_and_deleted(site: TestClient) -> None:
    sign_in(site)
    host = TestClient(site.app)
    host.post("/api/auth/register", json={"name": "Cikgu Rina", "email": "rina@example.test", "password": "rahsia-123"})
    made = host.post("/api/quizzes", json={"title": "Sains Tahun 4", "description": "Bab 1", "questions": []}).json()
    wait_until(lambda: events(site, "quiz.created"))
    assert events(site, "quiz.created")[0].data["owner"] == "Cikgu Rina"

    found = site.get(f"{P}/api/quizzes?q=rina").json()  # also by the parent's name
    assert [q["title"] for q in found["items"]] == ["Sains Tahun 4"] and found["items"][0]["owner"] == "Cikgu Rina"
    assert site.get(f"{P}/api/quizzes?samples=true").json()["total"] > 0

    detail = site.get(f"{P}/api/quizzes/{made['id']}").json()
    assert detail["description"] == "Bab 1" and detail["prompts"] == []
    edited = site.patch(f"{P}/api/quizzes/{made['id']}", json={"title": "Sains Tahun 5"}).json()
    assert edited["title"] == "Sains Tahun 5" and edited["description"] == "Bab 1"
    assert host.get(f"/api/quizzes/{made['id']}").json()["title"] == "Sains Tahun 5"

    host.put(f"/api/quizzes/{made['id']}", json={"title": "Sains Tahun 5", "questions": []})
    host.put(f"/api/quizzes/{made['id']}", json={"title": "Sains Tahun 5 (b)", "questions": []})
    wait_until(lambda: events(site, "quiz.updated"))
    assert len(events(site, "quiz.updated")) == 1  # a quiz saved again within minutes is one line

    assert site.delete(f"{P}/api/quizzes/{made['id']}").status_code == 204
    assert site.get(f"{P}/api/quizzes/{made['id']}").status_code == 404
    wait_until(lambda: events(site, "quiz.deleted"))


# ---------------------------------------------------------------- notifications


def test_notifications_can_be_made_read_pinned_edited_and_removed(site: TestClient) -> None:
    sign_in(site)
    site.post(f"{P}/api/notifications/read-all")
    site.delete(f"{P}/api/notifications")  # the sign-in's own warning is read and cleared first
    assert site.get(f"{P}/api/notifications").json() == {"items": [], "unread": 0}
    made = site.post(f"{P}/api/notifications", json={"title": "Semak sandaran", "body": "Setiap Jumaat", "level": "warning"}).json()
    assert made["source"] == "manual" and made["read"] is False and made["pinned"] is False
    assert site.post(f"{P}/api/notifications", json={"title": "", "level": "info"}).status_code == 422
    assert site.post(f"{P}/api/notifications", json={"title": "x", "level": "loud"}).status_code == 422

    nid = made["id"]
    patched = site.patch(f"{P}/api/notifications/{nid}", json={"read": True, "pinned": True, "body": "Setiap Isnin"}).json()
    assert (patched["read"], patched["pinned"], patched["body"], patched["title"]) == (True, True, "Setiap Isnin", "Semak sandaran")
    assert site.get(f"{P}/api/notifications?show=unread").json()["items"] == []
    assert [n["id"] for n in site.get(f"{P}/api/notifications?show=pinned").json()["items"]] == [nid]
    assert site.patch(f"{P}/api/notifications/{nid}", json={"read": False}).json()["read"] is False
    assert site.get(f"{P}/api/notifications").json()["unread"] == 1

    other = site.post(f"{P}/api/notifications", json={"title": "Lain"}).json()
    assert site.post(f"{P}/api/notifications/read-all").status_code == 204
    assert site.get(f"{P}/api/notifications").json()["unread"] == 0
    assert site.delete(f"{P}/api/notifications").status_code == 204  # clears what is read, keeps what is pinned
    assert [n["id"] for n in site.get(f"{P}/api/notifications").json()["items"]] == [nid]
    assert site.delete(f"{P}/api/notifications/{nid}").status_code == 204
    assert site.delete(f"{P}/api/notifications/{nid}").status_code == 404
    assert site.get(f"{P}/api/notifications").json()["items"] == [] and other["id"] != nid
    assert rows(site, AdminNotification) == []


# ---------------------------------------------------------------- rooms and children


def test_children_joining_are_seen_live_and_counted(site: TestClient) -> None:
    sign_in(site)
    host = TestClient(site.app)
    assert host.post("/api/auth/login", json={"email": "demo@didik.test", "password": "main-bersama"}).status_code == 200
    quiz = sample_id(host, "Haiwan di Malaysia")
    room = host.post("/api/rooms", json={"quiz_id": quiz, "mode": "lumba"}).json()
    wait_until(lambda: events(site, "room.opened"))

    with host.websocket_connect(f"/ws/{room['slug']}") as child:
        child.send_json({"t": "join", "name": "Aisyah", "avatar": "kancil"})
        wait_until(lambda: events(site, "player.joined"))
        joined = events(site, "player.joined")[0]
        assert joined.subject == "lumba" and joined.data["player"] == "Aisyah" and "ip" not in joined.data

        live = site.get(f"{P}/api/live").json()
        assert live["children"] == 1 and live["rooms"][0]["code"] == room["code"] and live["rooms"][0]["host"] == "Ibu Demo"
        detail = site.get(f"{P}/api/rooms/{room['code']}").json()
        assert [p["name"] for p in detail["people"]] == ["Aisyah"] and detail["modeTitle"]

        data = site.get(f"{P}/api/overview?days=7").json()
        assert data["students"]["period"] == 1 and data["rooms"]["period"] == 1
        assert data["modes"][0]["key"] == "lumba" and sum(map(sum, data["heatmap"]["grid"])) == 1
        assert len(data["students"]["series"]) == 7

        assert site.post(f"{P}/api/rooms/{room['code']}/close").status_code == 204
        assert site.get(f"{P}/api/rooms/{room['code']}").status_code == 404
    wait_until(lambda: events(site, "room.closed"))
    assert events(site, "room.closed")[0].data["players"] == 1


def test_bots_are_not_counted_as_children(site: TestClient) -> None:
    sign_in(site)
    host = TestClient(site.app)
    host.post("/api/auth/login", json={"email": "demo@didik.test", "password": "main-bersama"})
    room = host.post("/api/rooms", json={"quiz_id": sample_id(host, "Haiwan di Malaysia"), "mode": "lumba"}).json()
    found = site.app.state.rooms.find(room["code"])
    found.join(None, {"name": "Bot"}, bot=True)
    assert site.get(f"{P}/api/live").json()["children"] == 0
    assert events(site, "player.joined") == []


def test_the_overview_starts_empty_and_follows_the_period(site: TestClient) -> None:
    sign_in(site)
    for days in (7, 14, 30, 90):
        data = site.get(f"{P}/api/overview?days={days}").json()
        assert data["days"] == days and len(data["parents"]["series"]) == days
        assert data["students"]["period"] == 0 and data["heatmap"]["max"] == 0
    assert site.get(f"{P}/api/overview?days=11").json()["days"] == 14  # only the offered periods


def test_the_activity_log_filters_and_pages(site: TestClient) -> None:
    sign_in(site)
    bus = site.app.state.bus
    for number in range(55):
        bus.emit("quiz.created", f"kuiz {number}", title=str(number))
    bus.emit("room.opened", "bilik terbuka", subject="lumba")
    wait_until(lambda: len(events(site, "quiz.created")) == 55 and events(site, "room.opened"))

    first = site.get(f"{P}/api/activity?per=40").json()
    assert len(first["items"]) == 40 and first["more"] is True
    assert all(not e["kind"].startswith("admin.") for e in first["items"])  # own sign-ins live on the security page
    second = site.get(f"{P}/api/activity?per=40&before={first['items'][-1]['id']}").json()
    assert second["more"] is False and len(first["items"]) + len(second["items"]) == 56
    assert {e["kind"] for e in site.get(f"{P}/api/activity?group=room").json()["items"]} == {"room.opened"}
    assert [e["summary"] for e in site.get(f"{P}/api/activity?q=KUIZ 54").json()["items"]] == ["kuiz 54"]
    assert {e["kind"] for e in site.get(f"{P}/api/activity?group=admin").json()["items"]} >= {"admin.signin"}


# ---------------------------------------------------------------- the live connection


def _next(ws, kind: str, tries: int = 12) -> dict:
    for _ in range(tries):
        message = ws.receive_json()
        if message["t"] == kind:
            return message
    raise AssertionError(f"no {kind}")


def test_the_live_connection_needs_the_session_and_the_sites_own_origin(site: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as signed_out, site.websocket_connect(f"{P}/ws", headers=HERE):
        pass
    assert signed_out.value.code == 4401
    sign_in(site)
    with pytest.raises(WebSocketDisconnect) as foreign, site.websocket_connect(f"{P}/ws", headers={"origin": "https://evil.example"}):
        pass
    assert foreign.value.code == 4403
    with pytest.raises(WebSocketDisconnect) as bare, site.websocket_connect(f"{P}/ws"):
        pass
    assert bare.value.code == 4403  # a browser always names its origin


def test_the_live_connection_pushes_events_notifications_and_the_rooms(site: TestClient) -> None:
    sign_in(site)
    with site.websocket_connect(f"{P}/ws", headers=HERE) as ws:
        assert _next(ws, "hello")["now"].endswith("Z")
        assert _next(ws, "live")["rooms"] == []

        TestClient(site.app).post("/api/auth/register", json={"name": "Puan Siti", "email": "siti@example.test", "password": "rahsia-123"})
        event = _next(ws, "event")["event"]
        assert event["kind"] == "user.signup" and event["data"]["name"] == "Puan Siti"
        assert _next(ws, "notification")["notification"]["title"] == "Ibu bapa baharu"

        # the owner's own change reaches every open dashboard
        made = site.post(f"{P}/api/notifications", json={"title": "Nota"}).json()
        assert _next(ws, "notification")["notification"]["id"] == made["id"]
        site.delete(f"{P}/api/notifications/{made['id']}")
        assert _next(ws, "notification-removed")["id"] == made["id"]

        ws.send_text('{"t":"ping"}')
        assert _next(ws, "pong")


def test_the_live_connection_closes_when_the_session_ends(site: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from didik_live.admin import socket as admin_socket

    monkeypatch.setattr(admin_socket, "SNAPSHOT_EVERY", 0.05)
    monkeypatch.setattr(admin_socket, "RECHECK_EVERY", 0.0)
    sign_in(site)
    with site.websocket_connect(f"{P}/ws", headers=HERE) as ws:
        _next(ws, "live")
        with site.app.state.db.sessions() as db:
            db.execute(update(AdminSession).values(expires_at=datetime.now(UTC) - timedelta(seconds=1)))
            db.commit()
        assert _next(ws, "bye")


# ---------------------------------------------------------------- settings and mail


def test_settings_read_the_owner_and_the_secret_path_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("DIDIK_ADMIN_EMAIL", "DIDIK_ADMIN_PATH", "DIDIK_ADMIN_TZ"):
        monkeypatch.delenv(name, raising=False)
    assert load_settings().admin is None

    monkeypatch.setenv("DIDIK_ADMIN_EMAIL", " Owner@Example.test ")
    with pytest.raises(ValueError, match="bersama"):
        load_settings()
    monkeypatch.setenv("DIDIK_ADMIN_PATH", "too-short")
    with pytest.raises(ValueError, match="24"):
        load_settings()
    monkeypatch.setenv("DIDIK_ADMIN_PATH", "/" + PATH + "/")
    admin = load_settings().admin
    assert admin is not None and admin.email == OWNER and admin.path == PATH and admin.prefix == P
    monkeypatch.setenv("DIDIK_ADMIN_EMAIL", "not-an-email")
    with pytest.raises(ValueError, match="emel"):
        load_settings()


def test_a_public_server_with_a_control_room_needs_mail(settings: Settings, tmp_path) -> None:
    (tmp_path / "no-web").mkdir()
    (tmp_path / "no-web" / "200.html").write_text("<html></html>")
    base = replace(settings, production=True, public_url="https://didik.example.test", secure_cookies=True, seed_demo=False, admin=ADMIN)
    assert any("SMTP" in problem for problem in base.problems())
    assert not any("SMTP" in problem for problem in replace(base, mail=MAIL).problems())
    assert not any("SMTP" in problem for problem in replace(base, admin=None).problems())


def test_an_upgraded_database_gets_the_new_columns(tmp_path) -> None:
    from sqlalchemy import create_engine, text

    from didik_live.db import Database

    url = f"sqlite:///{tmp_path / 'old.db'}"
    old = create_engine(url)
    with old.begin() as connection:  # a parents table as the first version made it
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(80), email VARCHAR(254), password_hash VARCHAR(255), created_at DATETIME)"))
        connection.execute(text("INSERT INTO users (name, email, password_hash) VALUES ('Lama', 'lama@example.test', 'x')"))
    database = Database(url)
    database.create_all()
    with database.sessions() as db:
        user = db.scalar(select(User))
        assert user.name == "Lama" and user.disabled_at is None and user.last_login_at is None
    database.create_all()  # and a second start changes nothing


def test_mailer_says_whether_it_sent(monkeypatch: pytest.MonkeyPatch) -> None:
    assert Mailer(None).send("a@b.test", "s", "b") is False
    sent = []

    class Smtp:
        def __init__(self, *args, **kwargs) -> None: ...
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def starttls(self, **kwargs) -> None: ...
        def login(self, *args) -> None: ...
        def send_message(self, message) -> None: sent.append(message)

    monkeypatch.setattr("didik_live.mailer.smtplib.SMTP", Smtp)
    assert Mailer(MAIL).send("a@b.test", "s", "b") is True and len(sent) == 1


# ---------------------------------------------------------------- bulk actions


def parents(site: TestClient, count: int) -> list[tuple[TestClient, int]]:
    made = []
    for number in range(count):
        parent = TestClient(site.app)
        email = f"ibu{number}@example.test"
        assert parent.post("/api/auth/register", json={"name": f"Ibu {number}", "email": email, "password": "rahsia-123"}).status_code == 201
        made.append((parent, site.get(f"{P}/api/users?q={email}").json()["items"][0]["id"]))
    return made


def test_parents_can_be_suspended_restored_and_deleted_in_bulk(site: TestClient) -> None:
    sign_in(site)
    made = parents(site, 4)
    ids = [uid for _, uid in made]
    system = site.get(f"{P}/api/users?status=system").json()["items"][0]["id"]

    # one of them is hosting a room, and has a picture on disk
    host, host_id = made[0]
    sample = sample_id(host, "Haiwan di Malaysia")
    quiz = host.post(f"/api/quizzes/{sample}/copy").json()
    assert host.post("/api/rooms", json={"quiz_id": quiz["id"], "mode": "lumba"}).status_code == 201
    picture = site.app.state.settings.upload_dir / "bulk.webp"
    picture.write_bytes(b"x")
    with site.app.state.db.sessions() as db:
        from didik_live.models import Upload

        db.add(Upload(owner_id=made[1][1], filename="bulk.webp", width=1, height=1))
        db.commit()

    # three real accounts, one repeated, the protected demo account, and an id that does not exist
    answer = site.post(f"{P}/api/users/bulk", json={"ids": [*ids[:3], ids[0], system, 99999], "action": "suspend"}).json()
    assert answer == {"action": "suspend", "requested": 5, "done": 3, "skipped": 2}
    assert [made[n][0].get("/api/auth/me").json()["user"] for n in range(3)] == [None, None, None]  # signed out at once
    assert made[3][0].get("/api/auth/me").json()["user"] is not None  # the fourth was not asked
    assert site.app.state.rooms.rooms_of(host_id) == []  # the room closed with its host
    assert made[1][0].post("/api/auth/login", json={"email": "ibu1@example.test", "password": "rahsia-123"}).status_code == 403
    wait_until(lambda: events(site, "user.suspended"))
    summary = events(site, "user.suspended")[0]
    assert summary.data["count"] == 3 and summary.data["bulk"] is True and "3 ibu bapa" in summary.summary  # one line, not three

    # restoring asks only for what is suspended
    assert site.post(f"{P}/api/users/bulk", json={"ids": ids, "action": "restore"}).json() == {"action": "restore", "requested": 4, "done": 3, "skipped": 1}
    assert made[2][0].post("/api/auth/login", json={"email": "ibu2@example.test", "password": "rahsia-123"}).status_code == 200

    # deleting takes the quizzes and the pictures with it
    assert site.post(f"{P}/api/users/bulk", json={"ids": [ids[0], ids[1], system], "action": "delete"}).json() == {"action": "delete", "requested": 3, "done": 2, "skipped": 1}
    assert not picture.exists() and rows(site, Quiz, Quiz.owner_id.in_(ids[:2])) == []
    assert [u["id"] for u in site.get(f"{P}/api/users").json()["items"]] == [ids[3], ids[2]]
    assert site.get(f"{P}/api/users?status=system").json()["total"] == 1  # still there
    wait_until(lambda: events(site, "user.deleted"))


def test_a_bulk_action_is_checked_before_it_runs(site: TestClient) -> None:
    for path, body in (
        ("users", {"ids": [], "action": "delete"}),
        ("users", {"ids": list(range(501)), "action": "delete"}),
        ("users", {"ids": [1], "action": "explode"}),
        ("users", {"ids": ["x"], "action": "delete"}),
        ("users", {"ids": [1], "action": "delete", "extra": 1}),
        ("quizzes", {"ids": [1], "action": "suspend"}),
        ("notifications", {"ids": [1], "action": "burn"}),
        ("rooms", {"codes": [], "action": "close"}),
        ("rooms", {"codes": ["x" * 40], "action": "close"}),
    ):
        assert site.post(f"{P}/api/{path}/bulk", json=body).status_code in (401, 422), (path, body)
    sign_in(site)
    for path, body in (
        ("users", {"ids": [], "action": "delete"}),
        ("users", {"ids": list(range(501)), "action": "delete"}),
        ("users", {"ids": [1], "action": "explode"}),
        ("users", {"ids": ["x"], "action": "delete"}),
        ("users", {"ids": [1], "action": "delete", "extra": 1}),
        ("quizzes", {"ids": [1], "action": "suspend"}),
        ("notifications", {"ids": [1], "action": "burn"}),
        ("rooms", {"codes": [], "action": "close"}),
        ("rooms", {"codes": ["x" * 40], "action": "close"}),
    ):
        assert site.post(f"{P}/api/{path}/bulk", json=body).status_code == 422, (path, body)
    assert site.post(f"{P}/api/users/bulk", json={"ids": [1], "action": "delete"}, headers={"x-didik-admin": ""}).status_code == 403


def test_select_all_that_match_returns_the_ids_up_to_a_cap(site: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from didik_live.admin import api

    sign_in(site)
    made = parents(site, 5)
    site.patch(f"{P}/api/users/{made[0][1]}", json={"disabled": True})
    everyone = site.get(f"{P}/api/users/ids").json()
    assert sorted(everyone["ids"]) == sorted(uid for _, uid in made[1:]) and everyone["total"] == 4 and everyone["capped"] is False
    assert site.get(f"{P}/api/users/ids?status=suspended").json()["ids"] == [made[0][1]]
    assert site.get(f"{P}/api/users/ids?q=ibu3").json()["ids"] == [made[3][1]]
    monkeypatch.setattr(api, "MAX_BULK", 2)
    capped = site.get(f"{P}/api/users/ids").json()
    assert len(capped["ids"]) == 2 and capped["total"] == 4 and capped["capped"] is True


def test_quizzes_can_be_deleted_in_bulk(site: TestClient) -> None:
    sign_in(site)
    ((host, _),) = parents(site, 1)
    made = [host.post("/api/quizzes", json={"title": f"Kuiz {n}", "questions": []}).json()["id"] for n in range(4)]
    found = site.get(f"{P}/api/quizzes/ids?q=kuiz").json()
    assert sorted(found["ids"]) == sorted(made) and found["total"] == 4 and found["capped"] is False
    assert site.post(f"{P}/api/quizzes/bulk", json={"ids": [*made[:3], 99999], "action": "delete"}).json() == {"action": "delete", "requested": 4, "done": 3, "skipped": 1}
    assert [q["id"] for q in site.get(f"{P}/api/quizzes").json()["items"]] == [made[3]]
    wait_until(lambda: events(site, "quiz.deleted"))
    assert events(site, "quiz.deleted")[0].data["count"] == 3
    assert site.get(f"{P}/api/quizzes/ids?samples=true").json()["total"] > 0


def test_notifications_can_be_changed_in_bulk(site: TestClient) -> None:
    sign_in(site)
    site.post(f"{P}/api/notifications/read-all")
    site.delete(f"{P}/api/notifications")
    ids = [site.post(f"{P}/api/notifications", json={"title": f"Nota {n}"}).json()["id"] for n in range(4)]

    def state() -> dict[int, tuple[bool, bool]]:
        return {n["id"]: (n["read"], n["pinned"]) for n in site.get(f"{P}/api/notifications").json()["items"]}

    assert site.post(f"{P}/api/notifications/bulk", json={"ids": ids[:3], "action": "read"}).json()["done"] == 3
    assert state() == {ids[0]: (True, False), ids[1]: (True, False), ids[2]: (True, False), ids[3]: (False, False)}
    assert site.post(f"{P}/api/notifications/bulk", json={"ids": ids[:2], "action": "unread"}).json()["done"] == 2
    assert site.post(f"{P}/api/notifications/bulk", json={"ids": [ids[1], ids[3]], "action": "pin"}).json()["done"] == 2
    assert state()[ids[1]] == (False, True) and state()[ids[3]] == (False, True) and state()[ids[0]] == (False, False)
    assert site.post(f"{P}/api/notifications/bulk", json={"ids": [ids[3]], "action": "unpin"}).json()["done"] == 1
    assert site.get(f"{P}/api/notifications").json()["unread"] == 3

    answer = site.post(f"{P}/api/notifications/bulk", json={"ids": [*ids[:3], 99999], "action": "delete"}).json()
    assert answer == {"action": "delete", "requested": 4, "done": 3, "skipped": 1}
    assert list(state()) == [ids[3]]


def test_rooms_can_be_closed_in_bulk(site: TestClient) -> None:
    sign_in(site)
    host = TestClient(site.app)
    host.post("/api/auth/login", json={"email": "demo@didik.test", "password": "main-bersama"})
    quiz = sample_id(host, "Haiwan di Malaysia")
    codes = [host.post("/api/rooms", json={"quiz_id": quiz, "mode": mode}).json()["code"] for mode in ("lumba", "hutan", "kebun")]
    assert len(site.get(f"{P}/api/live").json()["rooms"]) == 3
    answer = site.post(f"{P}/api/rooms/bulk", json={"codes": [codes[0], codes[2], codes[0], "000000"], "action": "close"}).json()
    assert answer == {"action": "close", "requested": 3, "done": 2, "skipped": 1}
    assert [r["code"] for r in site.get(f"{P}/api/live").json()["rooms"]] == [codes[1]]
    wait_until(lambda: events(site, "admin.room_closed"))
