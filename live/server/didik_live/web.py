"""Serving the built web app (live/web/build) from the same origin as the API and the sockets.

The page's few inline scripts are hashed at start-up into the Content-Security-Policy, so the policy
allows exactly those scripts and nothing injected.
"""

from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, Response

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


def mount_web(app: FastAPI, web_dir: Path) -> None:
    fallback = next((web_dir / name for name in ("200.html", "index.html") if (web_dir / name).is_file()), None)
    shell = fallback.read_text(encoding="utf-8") if fallback else None
    hashes = [
        base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
        for body in (INLINE_SCRIPT.findall(shell) if shell else [])
    ]
    app.state.csp = policy(hashes)
    root = web_dir.resolve()

    @app.get("/{path:path}", include_in_schema=False)
    def web(path: str, request: Request) -> Response:
        if path.startswith(("api/", "ws/", "uploads/")):
            raise HTTPException(404, "Tidak dijumpai.")
        if shell is None:
            return HTMLResponse(NOT_BUILT, status_code=503)
        if path:
            candidate = (root / path).resolve()
            if candidate.is_file() and candidate.is_relative_to(root):
                immutable = path.startswith("_app/immutable/")
                headers = {"Cache-Control": "public, max-age=31536000, immutable" if immutable else "no-cache"}
                return FileResponse(candidate, headers=headers)
        return HTMLResponse(shell, headers={"Cache-Control": "no-cache"})
