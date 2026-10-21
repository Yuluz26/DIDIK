"""Pictures for questions. Every upload is decoded and re-encoded as WebP, so only plain pixels are
ever stored or served: no metadata (location, camera), no scripts hidden in files, no odd formats."""

from __future__ import annotations

import secrets
import warnings
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from PIL import Image, ImageOps
from sqlalchemy.orm import Session

from ..deps import get_db, limit, require_user
from ..models import Upload, User

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

MAX_SIDE = 1280
ALLOWED = {"JPEG", "PNG", "WEBP", "GIF"}
Image.MAX_IMAGE_PIXELS = 40_000_000


def reencode(data: bytes) -> tuple[bytes, int, int]:
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        try:
            image = Image.open(BytesIO(data))
            if image.format not in ALLOWED:
                raise ValueError
            image.load()
        except (OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
            raise HTTPException(422, "Fail ini bukan gambar yang boleh dibaca. Cuba JPG atau PNG.") from error

    image = ImageOps.exif_transpose(image)
    image = image.convert("RGBA" if image.mode in ("RGBA", "LA", "P") else "RGB")
    image.thumbnail((MAX_SIDE, MAX_SIDE))
    out = BytesIO()
    image.save(out, "WEBP", quality=82, method=4)
    return out.getvalue(), image.width, image.height


@router.post("", status_code=201)
async def upload(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)) -> dict:
    limit(request, "upload", 30, 600, key=str(user.id))
    settings = request.app.state.settings
    declared = int(request.headers.get("content-length") or 0)
    if declared > settings.max_upload_bytes:
        raise HTTPException(413, "Gambar terlalu besar. Had 5 MB.")

    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > settings.max_upload_bytes:
            raise HTTPException(413, "Gambar terlalu besar. Had 5 MB.")
    if not body:
        raise HTTPException(422, "Tiada gambar dihantar.")

    # Decoding is CPU work; keep it off the event loop so live rooms stay smooth.
    data, width, height = await run_in_threadpool(reencode, bytes(body))
    name = f"{secrets.token_hex(16)}.webp"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    (settings.upload_dir / name).write_bytes(data)
    db.add(Upload(owner_id=user.id, filename=name, width=width, height=height))
    db.commit()
    return {"url": f"/uploads/{name}", "width": width, "height": height}
