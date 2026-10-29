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
from sqlalchemy import text

from .activity import AdminBus, NullBus
from .admin import mount_admin
from .api import auth, quizzes, rooms, uploads
from .config import Settings, load_settings
from .db import Database
from .deps import malay_errors
from .game.manager import RoomManager
from .game.socket import room_socket
from .game.store import RoomStore
from .mailer import Mailer
from .security import RateLimiter
from .seed import seed, seed_library
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
# The control room's pages: never kept, never indexed, and no script or style except its own files.
ADMIN_HEADERS = [
    (b"cache-control", b"no-store"),
    (b"x-robots-tag", b"noindex, nofollow, noarchive"),
    (
        b"content-security-policy",
        b"default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; "
        b"base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    ),
]
# On a public server the site is https only: browsers remember to never try plain http for a year.
HSTS = (b"strict-transport-security", b"max-age=31536000; includeSubDomains")


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
        app = scope.get("app")
        path = scope["path"]
        prefix = getattr(app.state, "admin_prefix", None) if app else None
        admin = bool(prefix) and (path == prefix or path.startswith(prefix + "/"))
        if scope["method"] in UNSAFE and (path.startswith("/api/") or admin) and not _same_site(headers):
            response = JSONResponse({"message": "Permintaan ditolak."}, status_code=403)
            await response(scope, receive, send)
            return

        async def send_with_headers(message: dict) -> None:
            if message["type"] == "http.response.start":
                extra = list(SECURITY_HEADERS)
                # Read when the response starts, not when the request arrives: serving the page may
                # have just picked up a new build, whose inline scripts the policy must match.
                csp = getattr(app.state, "csp", None) if app else None
                if csp:
                    extra.append((b"content-security-policy", csp.encode()))
                settings = getattr(app.state, "settings", None) if app else None
                if settings is not None and settings.production:
                    extra.append(HSTS)
                current = list(message.get("headers", []))
                if admin:
                    current = [h for h in current if h[0].lower() != b"cache-control"]
                    extra += ADMIN_HEADERS
                message["headers"] = current + extra
            await send(message)

        await self.app(scope, receive, send_with_headers)


def _same_site(headers: dict[str, str]) -> bool:
    fetch_site = headers.get("sec-fetch-site")
    if fetch_site and fetch_site not in ("same-origin", "none"):
        return False
    origin = headers.get("origin")
    return not origin or urlparse(origin).netloc == headers.get("host")


class Uploads(StaticFiles):
    """The uploaded pictures. Each has a random name of its own and is never changed in place (a new picture
    gets a new name), so a browser may keep it for a year without asking again."""

    def file_response(self, *args: Any, **kwargs: Any):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    database = Database(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        database.create_all()
        if isinstance(app.state.bus, AdminBus):
            app.state.bus.start()
        for warning in settings.warnings():
            log.warning("Amaran: %s", warning)
        with database.sessions() as db:
            # the demo parent and its samples on localhost; on a public server, the samples alone
            if settings.seed_demo:
                seed(db)
            else:
                seed_library(db)
        # Rooms that were open when the server last stopped come back before the first connection.
        await app.state.rooms.restore()
        app.state.rooms.start()
        yield
        await app.state.rooms.shutdown()
        if isinstance(app.state.bus, AdminBus):
            await app.state.bus.stop()

    app = FastAPI(title="DIDIK Main Bersama", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    app.state.db = database
    app.state.limiter = RateLimiter()
    app.state.mailer = Mailer(settings.mail)
    app.state.rooms = RoomManager(allow_bots=settings.allow_bots, store=RoomStore(database))
    # What happens on the site is recorded only when the owner has a control room to read it in.
    app.state.bus = AdminBus(database, settings.admin.timezone) if settings.admin else NullBus()
    app.state.rooms.bus = app.state.bus
    app.add_middleware(Guard)

    @app.exception_handler(RequestValidationError)
    async def _invalid(_request: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse({"message": "Semak semula maklumat.", "errors": malay_errors(error.errors())}, status_code=422)

    @app.exception_handler(HTTPException)
    async def _http(_request: Request, error: HTTPException) -> JSONResponse:
        body = error.detail if isinstance(error.detail, dict) else {"message": error.detail}
        return JSONResponse(body, status_code=error.status_code, headers=getattr(error, "headers", None))

    @app.get("/api/health", include_in_schema=False)
    def health() -> JSONResponse:
        """For the container and the uptime monitor: 200 while the server and its database answer."""
        try:
            with database.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001 - any database failure means unhealthy
            log.exception("Pemeriksaan kesihatan: pangkalan data tidak menjawab")
            return JSONResponse({"ok": False, "database": False}, status_code=503, headers={"Cache-Control": "no-store"})
        return JSONResponse({"ok": True, "database": True, "rooms": len(app.state.rooms.by_code)}, headers={"Cache-Control": "no-store"})

    for router in (auth.router, quizzes.router, uploads.router, rooms.router):
        app.include_router(router)

    @app.websocket("/ws/{key}")
    async def socket(ws: WebSocket, key: str) -> None:
        await room_socket(ws, key)

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", Uploads(directory=settings.upload_dir, check_dir=False), name="uploads")
    if settings.admin:
        mount_admin(app, settings)
    mount_web(app, settings.web_dir)
    return app
