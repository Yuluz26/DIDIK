"""The application: API, sockets, uploads and the web app on one origin."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api import auth, quizzes, rooms, uploads
from .config import Settings, load_settings
from .db import Database
from .deps import malay_errors
from .game.manager import RoomManager
from .game.socket import room_socket
from .game.store import RoomStore
from .security import RateLimiter
from .seed import seed
from .web import mount_web

log = logging.getLogger("didik")

UNSAFE = {"POST", "PUT", "PATCH", "DELETE"}
SECURITY_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (b"x-frame-options", b"DENY"),
    (b"permissions-policy", b"camera=(), microphone=(), geolocation=(), payment=()"),
    (b"cross-origin-opener-policy", b"same-origin"),
]


class Guard:
    """Plain ASGI middleware: security headers on every response, and a same-origin check on
    every request that changes data, so another site cannot act with a parent's cookie."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        if scope["method"] in UNSAFE and scope["path"].startswith("/api/") and not _same_site(headers):
            response = JSONResponse({"message": "Permintaan ditolak."}, status_code=403)
            await response(scope, receive, send)
            return

        app = scope.get("app")

        async def send_with_headers(message: dict) -> None:
            if message["type"] == "http.response.start":
                extra = list(SECURITY_HEADERS)
                # Read when the response starts, not when the request arrives: serving the page may
                # have just picked up a new build, whose inline scripts the policy must match.
                csp = getattr(app.state, "csp", None) if app else None
                if csp:
                    extra.append((b"content-security-policy", csp.encode()))
                message["headers"] = list(message.get("headers", [])) + extra
            await send(message)

        await self.app(scope, receive, send_with_headers)


def _same_site(headers: dict[str, str]) -> bool:
    fetch_site = headers.get("sec-fetch-site")
    if fetch_site and fetch_site not in ("same-origin", "none"):
        return False
    origin = headers.get("origin")
    return not origin or urlparse(origin).netloc == headers.get("host")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    database = Database(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        database.create_all()
        if settings.seed_demo:
            with database.sessions() as db:
                seed(db)
        # Rooms that were open when the server last stopped come back before the first connection.
        await app.state.rooms.restore()
        app.state.rooms.start()
        yield
        await app.state.rooms.shutdown()

    app = FastAPI(title="DIDIK Main Bersama", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    app.state.db = database
    app.state.limiter = RateLimiter()
    app.state.rooms = RoomManager(allow_bots=settings.allow_bots, store=RoomStore(database))
    app.add_middleware(Guard)

    @app.exception_handler(RequestValidationError)
    async def _invalid(_request: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse({"message": "Semak semula maklumat.", "errors": malay_errors(error.errors())}, status_code=422)

    @app.exception_handler(HTTPException)
    async def _http(_request: Request, error: HTTPException) -> JSONResponse:
        body = error.detail if isinstance(error.detail, dict) else {"message": error.detail}
        return JSONResponse(body, status_code=error.status_code, headers=getattr(error, "headers", None))

    @app.get("/api/health", include_in_schema=False)
    def health() -> dict:
        return {"ok": True, "rooms": len(app.state.rooms.by_code)}

    for router in (auth.router, quizzes.router, uploads.router, rooms.router):
        app.include_router(router)

    @app.websocket("/ws/{key}")
    async def socket(ws: WebSocket, key: str) -> None:
        await room_socket(ws, key)

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir, check_dir=False), name="uploads")
    mount_web(app, settings.web_dir)
    return app
