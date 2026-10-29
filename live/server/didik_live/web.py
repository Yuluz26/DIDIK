"""Serving the built web app (live/web/build) from the same origin as the API and the sockets.

The page's few inline scripts are hashed into the Content-Security-Policy, so the policy allows
exactly those scripts and nothing injected. The page is re-read when a new build replaces it, so
`npm run build` takes effect without restarting the server.
"""

from __future__ import annotations

import base64
import hashlib
import mimetypes
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, Response

# Windows takes file types from the registry, which may not know these; with `nosniff` an image sent
# as application/octet-stream is never drawn.
for _type, _ext in (("image/webp", ".webp"), ("audio/wav", ".wav"), ("image/svg+xml", ".svg")):
    mimetypes.add_type(_type, _ext)

INLINE_SCRIPT = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S | re.I)

NOT_BUILT = """<!doctype html><html lang="ms"><meta charset="utf-8"><title>DIDIK Main Bersama</title>
<body style="font:18px/1.6 system-ui;max-width:40rem;margin:4rem auto;padding:0 1rem">
<h1>Antara muka belum dibina</h1>
<p>Pelayan berjalan, tetapi fail web belum ada. Jalankan sekali:</p>
<pre style="background:#eef3f0;padding:1rem;border-radius:12px">cd live/web
npm install
npm run build</pre>
<p>Kemudian muat semula halaman ini.</p></body></html>"""


def policy(script_hashes: list[str]) -> str:
    scripts = " ".join(f"'sha256-{h}'" for h in script_hashes)
    return "; ".join(
        [
            "default-src 'self'",
            f"script-src 'self' {scripts}".strip(),
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: blob:",
            "font-src 'self'",
            "connect-src 'self'",
            "media-src 'self' data: blob:",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
        ]
    )


class Shell:
    """The SPA's one HTML page and the policy that matches its inline scripts."""

    def __init__(self, web_dir: Path, app: FastAPI) -> None:
        self.web_dir = web_dir
        self.app = app
        self.html: str | None = None
        self._stamp: float | None = -1.0  # never a real mtime, so the first refresh always runs
        self.refresh()

    def path(self) -> Path | None:
        return next((self.web_dir / n for n in ("200.html", "index.html") if (self.web_dir / n).is_file()), None)

    def refresh(self) -> None:
        path = self.path()
        stamp = path.stat().st_mtime if path else None
        if stamp == self._stamp and (self.html is not None or path is None):
            return
        self._stamp = stamp
        self.html = path.read_text(encoding="utf-8") if path else None
        hashes = [
            base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
            for body in (INLINE_SCRIPT.findall(self.html) if self.html else [])
        ]
        self.app.state.csp = policy(hashes)


# Files whose name carries a hash of their content, and the story art asked for with the build's
# version (?v=), never change. Everything else may be replaced by a new build: the browser keeps it but
# asks each time, and gets a bodiless 304 while it is unchanged.
IMMUTABLE = "public, max-age=31536000, immutable"
CHECK = "no-cache"
# The build writes these beside every text file (svelte.config.js, precompress).
ENCODINGS = (("br", ".br"), ("gzip", ".gz"))


def etag_of(path: Path) -> str:
    stat = path.stat()
    return '"' + hashlib.md5(f"{stat.st_mtime_ns}-{stat.st_size}".encode(), usedforsecurity=False).hexdigest() + '"'


def file_response(request: Request, path: Path, cache: str) -> Response:
    """A file from the build: 304 when the browser already has it, the precompressed copy when the
    browser takes one."""
    tag = etag_of(path)
    if tag in (t.strip() for t in request.headers.get("if-none-match", "").split(",")):
        return Response(status_code=304, headers={"ETag": tag, "Cache-Control": cache})
    headers = {"Cache-Control": cache, "ETag": tag, "Vary": "Accept-Encoding"}
    accepted = request.headers.get("accept-encoding", "")
    media_type = mimetypes.guess_type(path.name)[0]
    for encoding, suffix in ENCODINGS:
        packed = path.with_name(path.name + suffix)
        if encoding in accepted and packed.is_file():
            headers["Content-Encoding"] = encoding
            return FileResponse(packed, headers=headers, media_type=media_type)
    return FileResponse(path, headers=headers, media_type=media_type)


def mount_web(app: FastAPI, web_dir: Path) -> None:
    shell = Shell(web_dir, app)
    root = web_dir.resolve()

    @app.get("/{path:path}", include_in_schema=False)
    def web(path: str, request: Request) -> Response:
        if path.startswith(("api/", "ws/", "uploads/")):
            raise HTTPException(404, "Tidak dijumpai.")
        shell.refresh()
        if shell.html is None:
            return HTMLResponse(NOT_BUILT, status_code=503)
        if path:
            candidate = (root / path).resolve()
            if candidate.is_file() and candidate.is_relative_to(root):
                fixed = path.startswith("_app/immutable/") or (path.startswith("story/") and "v" in request.query_params)
                return file_response(request, candidate, IMMUTABLE if fixed else CHECK)
            # A script or style from an older build (a page left open across an update) must fail
            # as missing, not arrive as the HTML page, so the app can fall back instead of choking.
            if path.startswith("_app/"):
                raise HTTPException(404, "Tidak dijumpai.")
        return HTMLResponse(shell.html, headers={"Cache-Control": "no-cache"})
