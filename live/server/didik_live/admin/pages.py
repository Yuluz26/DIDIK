"""Mounting the control room: its secret address, its pages and its files.

The same address shows the sign-in page to a visitor and the dashboard to the owner. The dashboard's own
scripts and styles are handed only to a signed-in session; the sign-in page's few files are open (they
are served from the secret path, which is the only way to find them). Every response is `no-store` and
asks search engines to stay away (see app.Guard).
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import FileResponse, HTMLResponse, Response
from sqlalchemy.orm import Session

from ..activity import zone
from ..config import Settings
from ..deps import get_db
from . import api
from .auth import COOKIE, find_session
from .socket import admin_socket

STATIC = Path(__file__).resolve().parent / "static"
OPEN_FILES = {"login.css", "login.js", "mark.svg"}
FILE_NAME = re.compile(r"^[a-z0-9-]+\.(js|css|svg)$")
TYPES = {".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml"}


def mount_admin(app: FastAPI, settings: Settings) -> None:
    admin = settings.admin
    assert admin is not None
    app.state.admin_prefix = admin.prefix
    app.state.admin_tz = zone(admin.timezone)
    app.state.host_names = {}

    # The pages name their own files by absolute address, so they work with or without a trailing slash.
    pages = {name: (STATIC / f"{name}.html").read_text(encoding="utf-8").replace("__BASE__", admin.prefix) for name in ("login", "app")}
    router = APIRouter(prefix=admin.prefix, include_in_schema=False)
    router.include_router(api.public)
    router.include_router(api.private)

    @router.get("")
    @router.get("/")
    def page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
        signed_in = find_session(db, request.cookies.get(COOKIE)) is not None
        return HTMLResponse(pages["app" if signed_in else "login"])

    @router.get("/_/{name}")
    def asset(name: str, request: Request, db: Session = Depends(get_db)) -> Response:
        if not FILE_NAME.match(name):
            raise HTTPException(404, "Tidak dijumpai.")
        if name not in OPEN_FILES and find_session(db, request.cookies.get(COOKIE)) is None:
            raise HTTPException(404, "Tidak dijumpai.")
        path = STATIC / name
        if not path.is_file():
            raise HTTPException(404, "Tidak dijumpai.")
        return FileResponse(path, media_type=TYPES[path.suffix])

    @router.websocket("/ws")
    async def live(ws: WebSocket) -> None:
        await admin_socket(ws)

    app.include_router(router)
