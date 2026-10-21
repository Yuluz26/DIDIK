from __future__ import annotations

from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from didik_live.seed import DEMO_EMAIL

from .conftest import sample_id

NEW_QUIZ = {
    "title": "Kuiz Adik",
    "description": "",
    "questions": [
        {"type": "truefalse", "prompt": "Langit biru.", "answer": True},
        {"type": "text", "prompt": "Warna daun?", "answers": ["hijau"]},
    ],
}


def register(client: TestClient, email: str = "ibu@contoh.my") -> None:
    response = client.post("/api/auth/register", json={"name": "Ibu Aminah", "email": email, "password": "rahsia-123"})
    assert response.status_code == 201, response.text


def test_register_sign_in_and_out(client: TestClient) -> None:
    assert client.get("/api/auth/me").json() == {"user": None, "demo": True}
    register(client)
    assert client.get("/api/auth/me").json()["user"]["email"] == "ibu@contoh.my"

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").json()["user"] is None

    wrong = client.post("/api/auth/login", json={"email": "IBU@contoh.my", "password": "salah-sekali"})
    assert wrong.status_code == 422
    assert wrong.json()["message"] == "Emel atau kata laluan tidak betul."

    right = client.post("/api/auth/login", json={"email": "IBU@contoh.my", "password": "rahsia-123"})
    assert right.status_code == 200
    cookie = right.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie


def test_registration_explains_problems_in_malay(client: TestClient) -> None:
    response = client.post("/api/auth/register", json={"name": "", "email": "bukan-emel", "password": "123"})
    assert response.status_code == 422
    errors = {tuple(e["loc"]): e["message"] for e in response.json()["errors"]}
    assert errors[("name",)] == "Wajib diisi."
    assert errors[("email",)] == "Masukkan alamat emel yang sah."
    assert "8 aksara" in errors[("password",)]

    taken = client.post("/api/auth/register", json={"name": "X", "email": DEMO_EMAIL, "password": "rahsia-123"})
    assert taken.json()["errors"][0]["message"].startswith("Emel ini sudah didaftarkan")


def test_sign_in_attempts_are_limited(client: TestClient) -> None:
    codes = [
        client.post("/api/auth/login", json={"email": "x@y.my", "password": "salah-salah"}).status_code
        for _ in range(9)
    ]
    assert codes[-1] == 429


def test_cross_site_writes_are_refused(parent: TestClient) -> None:
    response = parent.post("/api/quizzes", json=NEW_QUIZ, headers={"Origin": "https://evil.example"})
    assert response.status_code == 403
    response = parent.post("/api/quizzes", json=NEW_QUIZ, headers={"Sec-Fetch-Site": "cross-site"})
    assert response.status_code == 403


def test_responses_carry_security_headers(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "script-src 'self'" in response.headers["content-security-policy"]


def test_quiz_lifecycle(client: TestClient) -> None:
    register(client)
    created = client.post("/api/quizzes", json=NEW_QUIZ)
    assert created.status_code == 201
    quiz = created.json()
    assert quiz["questionCount"] == 2 and quiz["canEdit"]
    assert all(q["id"] for q in quiz["questions"])

    quiz["questions"].append({"type": "number", "prompt": "2 + 2", "answer": 4})
    updated = client.put(f"/api/quizzes/{quiz['id']}", json={k: quiz[k] for k in ("title", "description", "questions")})
    assert updated.status_code == 200
    assert updated.json()["types"] == {"truefalse": 1, "text": 1, "number": 1}

    listing = client.get("/api/quizzes").json()
    assert [q["title"] for q in listing["mine"]] == ["Kuiz Adik"]
    assert len(listing["samples"]) == 5

    assert client.delete(f"/api/quizzes/{quiz['id']}").status_code == 204
    assert client.get(f"/api/quizzes/{quiz['id']}").status_code == 404


def test_editor_errors_point_at_the_exact_field(client: TestClient) -> None:
    register(client)
    bad = {
        "title": "Kuiz",
        "questions": [
            {"type": "truefalse", "prompt": "Ok", "answer": True},
            {"type": "single", "prompt": "3 + 4?", "choices": [{"text": "7"}, {"text": ""}]},
        ],
    }
    response = client.post("/api/quizzes", json=bad)
    assert response.status_code == 422
    locs = {tuple(e["loc"]): e["message"] for e in response.json()["errors"]}
    assert locs[("questions", 1, "choices", 1, "text")] == "Wajib diisi."


def test_samples_can_be_copied_but_not_edited_by_other_parents(client: TestClient) -> None:
    register(client)
    sample = sample_id(client, "Matematik Ceria")
    shown = client.get(f"/api/quizzes/{sample}").json()
    assert shown["canEdit"] is False
    assert client.put(f"/api/quizzes/{sample}", json=NEW_QUIZ).status_code == 404
    assert client.delete(f"/api/quizzes/{sample}").status_code == 404

    copy = client.post(f"/api/quizzes/{sample}/copy").json()
    assert copy["canEdit"] is True and copy["title"] == "Matematik Ceria"
    assert copy["questionCount"] == shown["questionCount"]


def test_other_parents_quizzes_stay_private(client: TestClient) -> None:
    register(client, "a@contoh.my")
    quiz_id = client.post("/api/quizzes", json=NEW_QUIZ).json()["id"]
    client.post("/api/auth/logout")
    register(client, "b@contoh.my")
    assert client.get(f"/api/quizzes/{quiz_id}").status_code == 404
    assert client.post(f"/api/quizzes/{quiz_id}/copy").status_code == 404


def test_uploads_are_reencoded_and_reject_non_images(parent: TestClient) -> None:
    image = Image.new("RGB", (3000, 1500), (200, 120, 40))
    raw = BytesIO()
    image.save(raw, "PNG")
    response = parent.post("/api/uploads", content=raw.getvalue(), headers={"Content-Type": "image/png"})
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["url"].startswith("/uploads/") and body["url"].endswith(".webp")
    assert (body["width"], body["height"]) == (1280, 640)
    served = parent.get(body["url"])
    assert served.status_code == 200 and served.content[:4] == b"RIFF"

    fake = parent.post("/api/uploads", content=b"<svg onload=alert(1)>", headers={"Content-Type": "image/svg+xml"})
    assert fake.status_code == 422


def test_uploads_need_a_parent(client: TestClient) -> None:
    assert client.post("/api/uploads", content=b"x").status_code == 401
