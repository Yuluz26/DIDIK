"""Builds the subject games' picture library from sources.json.

Every picture comes from Wikimedia Commons (NASA and other public-domain works, CC0, CC BY and CC BY-SA).
For each entry this script asks Commons for the file's licence and author, refuses anything outside the
licences DIDIK may use in a paid product, downloads the picture once (kept in .cache/), prepares it
(crop, cut-out, resize, WebP) and writes:

  web/static/game-assets/<key>.webp          the picture the games load
  web/static/game-assets/manifest.json       every picture: games, what it shows, author, licence, changes
  web/static/game-assets/CREDITS.txt         the same for people to read
  web/src/lib/subjects/assets.gen.ts         the sizes, so the page keeps room for a picture while it loads
  docs/interactive-revamp/ASSET-MANIFEST.md  the manifest as a table

Run from live/:   server/.venv/Scripts/python tools/game-assets/build.py [key-prefix ...]
With prefixes, only those pictures are remade (the manifest is still written whole).

Recipes ("make"):
  photo:W            the whole picture, W pixels wide at most
  cover:WxH[@x,y]    cropped to fill W by H, centred on the point x,y (percent; the middle if left out)
  tile:S[@x,y]       a square crop, S pixels
  disc:S             a planet on a black sky: cut to its disc, round, with a transparent sky
  glow:W             a bright thing on a black sky (rings, a comet, a galaxy): the dark becomes transparent and
                     the edges fade out ("feather": false keeps them, for a thing that reaches the edge)
  cut:W              a thing on a plain light background: the background becomes transparent
  keep:W             a picture that already has a transparent background, W pixels wide
  phase:S@k          the Moon's disc at a waxing phase: k of it lit (0 new, 0.5 first quarter, 1 full)
An optional "crop": [left, top, right, bottom] (percent) is taken first.
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
from pathlib import Path

import httpx
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
LIVE = HERE.parents[1]
OUT = LIVE / "web" / "static" / "game-assets"
CACHE = HERE / ".cache"
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "DIDIKAssetBot/1.1 (https://github.com/Yuluz26/DIDIK; educational quiz app) python-httpx/0.28"}

# What a paid educational product may use: no "non-commercial", no "no derivatives", nothing unknown.
ALLOWED = re.compile(r"^(public domain|pd\b.*|cc0.*|cc[ -]by([ -]sa)?[ -]\d\.\d.*|no restrictions|attribution)$", re.I)
SHARE_ALIKE = re.compile(r"by[ -]sa", re.I)

client = httpx.Client(headers=UA, timeout=60, follow_redirects=True)


def strip(html: str | None) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).replace("&amp;", "&").strip()


def ask(params: dict) -> dict:
    for attempt in range(6):
        r = client.get(API, params={"format": "json", **params})
        if r.status_code == 200 and r.text.startswith("{"):
            return r.json()
        time.sleep(3 + attempt * 5)
    raise SystemExit(f"Commons would not answer: {r.status_code}")


def lookup(files: list[str], width: int) -> dict[str, dict]:
    """Licence, author and a download address for each Commons file name."""
    out: dict[str, dict] = {}
    titles = [f"File:{f}" for f in files]
    for i in range(0, len(titles), 40):
        data = ask({"action": "query", "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": width, "titles": "|".join(titles[i : i + 40])})
        norm = {n["to"]: n["from"] for n in data["query"].get("normalized", [])}
        for page in data["query"]["pages"].values():
            name = norm.get(page["title"], page["title"]).removeprefix("File:")
            ii = (page.get("imageinfo") or [None])[0]
            if ii is None:
                raise SystemExit(f"Not on Commons: {name}")
            m = ii.get("extmetadata") or {}
            out[name] = {
                "licence": strip((m.get("LicenseShortName") or {}).get("value")),
                "licence_url": (m.get("LicenseUrl") or {}).get("value", ""),
                "author": strip((m.get("Artist") or {}).get("value"))[:160] or strip((m.get("Credit") or {}).get("value"))[:160],
                "thumb": ii.get("thumburl") or ii["url"],
                "full": ii["url"],
                "w": ii["width"],
                "h": ii["height"],
            }
    return out


def download(name: str, url: str) -> Image.Image:
    CACHE.mkdir(exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:120]
    path = CACHE / safe
    if not path.exists():
        for attempt in range(6):
            r = client.get(url)
            if r.status_code == 200:
                path.write_bytes(r.content)
                break
            time.sleep(4 + attempt * 6)
        else:
            raise SystemExit(f"Could not download {name}: {r.status_code}")
        time.sleep(0.4)
    im = Image.open(path)
    im.load()
    return im


# ---------------------------------------------------------------- preparing a picture


def flat(im: Image.Image, colour=(255, 255, 255)) -> Image.Image:
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        return Image.alpha_composite(Image.new("RGBA", im.size, colour + (255,)), im).convert("RGB")
    return im.convert("RGB")


def focus(spec: str) -> tuple[str, tuple[float, float]]:
    size, _, at = spec.partition("@")
    x, y = (float(v) for v in at.split(",")) if at else (50.0, 50.0)
    return size, (x / 100, y / 100)


def cover(im: Image.Image, w: int, h: int, at: tuple[float, float]) -> Image.Image:
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * scale)), max(h, round(im.height * scale))), Image.LANCZOS)
    left = min(max(0, round(im.width * at[0] - w / 2)), im.width - w)
    top = min(max(0, round(im.height * at[1] - h / 2)), im.height - h)
    return im.crop((left, top, left + w, top + h))


def bright_box(im: Image.Image, floor: int) -> tuple[int, int, int, int]:
    grey = im.convert("L").point(lambda v: 255 if v > floor else 0)
    return grey.filter(ImageFilter.MedianFilter(5)).getbbox() or (0, 0, im.width, im.height)


def disc(im: Image.Image, size: int) -> Image.Image:
    """A planet's disc, round and clean-edged, on nothing."""
    im = flat(im, (0, 0, 0))
    l, t, r, b = bright_box(im, 22)
    side = max(r - l, b - t)
    cx, cy = (l + r) / 2, (t + b) / 2
    box = tuple(round(v) for v in (cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2))
    square = Image.new("RGB", (side, side), (0, 0, 0))
    square.paste(im.crop(box), (0, 0))
    big = square.resize((size * 2, size * 2), Image.LANCZOS)
    mask = Image.new("L", big.size, 0)
    inset = round(size * 2 * 0.012)
    ImageDraw.Draw(mask).ellipse((inset, inset, big.width - inset, big.height - inset), fill=255)
    out = big.convert("RGBA")
    out.putalpha(mask.filter(ImageFilter.GaussianBlur(1.6)))
    return out.resize((size, size), Image.LANCZOS)


def glow(im: Image.Image, width: int, feather: bool = True) -> Image.Image:
    """Light on a black sky: how bright a point is becomes how solid it is."""
    im = flat(im, (0, 0, 0))
    im = im.crop(bright_box(im, 26))
    im = im.resize((width, max(1, round(im.height * width / im.width))), Image.LANCZOS)
    r, g, b = im.split()
    alpha = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 0 if v < 14 else min(255, round((v - 14) * 2.6)))
    # fade out towards the edges, so the picture has no frame against the sky it is laid on
    edge = Image.new("L", im.size, 0)
    mx, my = round(im.width * 0.07), round(im.height * 0.07)
    ImageDraw.Draw(edge).ellipse((mx, my, im.width - mx, im.height - my), fill=255)
    edge = edge.filter(ImageFilter.GaussianBlur(max(4, min(im.size) * 0.09)))
    out = im.convert("RGBA")
    out.putalpha(ImageChops.multiply(alpha, edge) if feather else alpha)
    return out


def cut(im: Image.Image, width: int) -> Image.Image:
    """A thing photographed on a plain light background, with the background taken away."""
    im = flat(im)
    w = min(im.width, 1200)
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    corner = im.getpixel((3, 3))
    diff = ImageChops.difference(im, Image.new("RGB", im.size, corner)).convert("L")
    solid = diff.point(lambda v: 255 if v > 26 else 0)
    # the background is what can be reached from the edges without crossing the thing
    seed = Image.new("L", (im.width + 2, im.height + 2), 0)
    seed.paste(solid, (1, 1))
    ImageDraw.floodfill(seed, (0, 0), 128)
    mask = seed.crop((1, 1, im.width + 1, im.height + 1)).point(lambda v: 0 if v == 128 else 255)
    mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA")
    out.putalpha(mask)
    box = mask.point(lambda v: 255 if v > 40 else 0).getbbox()
    if box:
        out = out.crop(box)
    return out.resize((width, max(1, round(out.height * width / out.width))), Image.LANCZOS)


def phase(moon: Image.Image, lit: float) -> Image.Image:
    """A waxing Moon: the lit part runs from the right limb to the terminator, an ellipse whose half-width
    goes from the whole radius (new) through nothing (first quarter) to the whole radius the other way (full)."""
    size = moon.width
    r = size / 2
    half = r * (1 - 2 * lit)
    shade = Image.new("L", moon.size, 255)
    px = shade.load()
    for y in range(size):
        dy = (y + 0.5 - r) / r
        span = (1 - dy * dy) ** 0.5 if abs(dy) < 1 else 0
        edge = r + half * span
        for x in range(size):
            if x + 0.5 < edge - 1.5:
                px[x, y] = 26  # earthshine: the dark part is dim, not gone
            elif x + 0.5 < edge + 1.5:
                px[x, y] = 26 + round((x + 0.5 - (edge - 1.5)) / 3 * 229)
    red, green, blue, alpha = moon.split()
    lit_rgb = [ImageChops.multiply(band, shade) for band in (red, green, blue)]
    return Image.merge("RGBA", (*lit_rgb, alpha))


def prepare(im: Image.Image, entry: dict) -> tuple[Image.Image, str]:
    changes = []
    if entry.get("crop"):
        l, t, r, b = entry["crop"]
        im = im.crop((round(im.width * l / 100), round(im.height * t / 100), round(im.width * r / 100), round(im.height * b / 100)))
        changes.append("dipotong")
    kind, _, spec = entry["make"].partition(":")
    if kind == "photo":
        im = flat(im)
        w = min(int(spec), im.width)
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        changes.append("dikecilkan")
    elif kind == "phase":
        # the Moon's disc with the part the Sun lights at this phase (0 new, 0.5 first quarter, 1 full)
        size, _, lit = spec.partition("@")
        im = phase(disc(im, int(size)), float(lit))
        changes.append("latar langit dibuang; fasa dilukis dengan menggelapkan bahagian yang tidak disinari")
    elif kind == "keep":
        # a picture that already has a transparent background: only made smaller
        im = im.convert("RGBA")
        w = min(int(spec), im.width)
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        changes.append("dikecilkan")
    elif kind in ("cover", "tile"):
        size, at = focus(spec)
        w, h = (int(size), int(size)) if kind == "tile" else (int(v) for v in size.split("x"))
        im = cover(flat(im), w, h, at)
        changes.append("dipotong dan dikecilkan")
    elif kind == "disc":
        im = disc(im, int(spec))
        changes.append("latar langit dibuang, dikecilkan")
    elif kind == "glow":
        im = glow(im, int(spec), entry.get("feather", True))
        changes.append("latar gelap dijadikan lut sinar, dikecilkan")
    elif kind == "cut":
        im = cut(im, int(spec))
        changes.append("latar dibuang, dikecilkan")
    else:
        raise SystemExit(f"Unknown recipe: {entry['make']}")
    if entry.get("note"):
        changes.append(entry["note"])
    return im, "; ".join(changes)


# ---------------------------------------------------------------- the build


def main(only: list[str]) -> None:
    sources = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    keys = [s["key"] for s in sources]
    assert len(keys) == len(set(keys)), "the same key twice in sources.json"
    found = lookup(sorted({s["file"] for s in sources}), 1600)
    old = {}
    manifest_path = OUT / "manifest.json"
    if manifest_path.exists():
        old = {m["key"]: m for m in json.loads(manifest_path.read_text(encoding="utf-8"))["assets"]}

    manifest = []
    for entry in sources:
        info = found[entry["file"]]
        if not ALLOWED.match(info["licence"]):
            raise SystemExit(f"{entry['key']}: licence \"{info['licence']}\" may not be used ({entry['file']})")
        dest = OUT / f"{entry['key']}.webp"
        wanted = not only or any(entry["key"].startswith(p) for p in only)
        fresh = old.get(entry["key"])
        if dest.exists() and fresh and fresh.get("make") == entry["make"] and fresh.get("crop") == entry.get("crop") and fresh.get("feather", True) == entry.get("feather", True) and fresh["file"] == entry["file"] and not (wanted and only):
            changes = fresh["changes"]
            with Image.open(dest) as done:
                size = done.size
        else:
            # big originals come down at a size that is plenty for the recipe
            url = info["thumb"] if max(info["w"], info["h"]) > 1700 and not entry["file"].lower().endswith(".svg") else info["full"]
            if entry["file"].lower().endswith(".svg"):
                url = info["thumb"]
            im, changes = prepare(download(entry["file"], url), entry)
            dest.parent.mkdir(parents=True, exist_ok=True)
            im.save(dest, "WEBP", quality=entry.get("quality", 84 if im.mode == "RGBA" else 80), method=6)
            size = im.size
            print(f"made {entry['key']}  {size[0]}x{size[1]}  {dest.stat().st_size // 1024} KB")
        manifest.append({
            "key": entry["key"],
            "path": f"game-assets/{entry['key']}.webp",
            "width": size[0],
            "height": size[1],
            "bytes": dest.stat().st_size,
            "games": entry["games"],
            "shows": entry["shows"],
            "kind": entry.get("kind", "photo"),
            "source": "Wikimedia Commons",
            "file": entry["file"],
            "author": info["author"],
            "licence": info["licence"],
            "share_alike": bool(SHARE_ALIKE.search(info["licence"])),
            "make": entry["make"],
            **({"crop": entry["crop"]} if entry.get("crop") else {}),
            **({"feather": False} if entry.get("feather") is False else {}),
            "changes": changes,
        })

    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({"assets": manifest}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    listed = {m["path"].removeprefix("game-assets/") for m in manifest}
    for stray in OUT.rglob("*.webp"):
        if stray.relative_to(OUT).as_posix() not in listed:
            stray.unlink()
            print("removed", stray.relative_to(OUT))

    lines = [
        "Pictures in this folder are used by DIDIK's subject games. All come from Wikimedia Commons under the",
        "licence shown (public domain, CC0, CC BY or CC BY-SA). Each was resized and saved as WebP; other changes",
        "are noted. Works under CC BY-SA remain under that licence.",
        "",
    ]
    for m in manifest:
        lines += [f"{m['key']}.webp", f"    {m['shows']}", f"    \"{m['file']}\" by {m['author'] or 'unknown'}. {m['licence']}. Changes: {m['changes']}.", ""]
    (OUT / "CREDITS.txt").write_text("\n".join(lines), encoding="utf-8", newline="\n")

    sizes = ",\n".join(f"\t'{m['key']}': [{m['width']}, {m['height']}]" for m in manifest)
    (LIVE / "web" / "src" / "lib" / "subjects" / "assets.gen.ts").write_text(
        "// Written by tools/game-assets/build.py from sources.json. Do not edit by hand.\n"
        "// The size of every picture in static/game-assets, so a game keeps its room while it loads.\n\n"
        f"export const ASSET_SIZES: Record<string, [number, number]> = {{\n{sizes}\n}};\n",
        encoding="utf-8",
        newline="\n",
    )

    doc = LIVE.parent / "docs" / "interactive-revamp" / "ASSET-MANIFEST.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    total = sum(m["bytes"] for m in manifest)
    by_licence: dict[str, int] = {}
    for m in manifest:
        by_licence[m["licence"]] = by_licence.get(m["licence"], 0) + 1
    table = [
        "# DIDIK Interactive Discovery: asset manifest",
        "",
        "Written by `live/tools/game-assets/build.py` from `live/tools/game-assets/sources.json`. Do not edit by hand:",
        "change `sources.json` and run the script. The machine-readable copy is `live/web/static/game-assets/manifest.json`.",
        "",
        f"**{len(manifest)} pictures, {total / 1024 / 1024:.1f} MB in all.** Every one is hosted locally (nothing is loaded from another",
        "site while a child plays) and comes from Wikimedia Commons, where the licence and author below were read from the",
        "file's own page by the build script. The script refuses any licence outside public domain, CC0, CC BY and CC BY-SA.",
        "",
        "| Licence | Pictures |",
        "| --- | --- |",
        *[f"| {k} | {v} |" for k, v in sorted(by_licence.items(), key=lambda kv: -kv[1])],
        "",
        "Kinds: `observation` a real photograph or spacecraft image; `enhanced` real data in enhanced or false colour;",
        "`visualisation` a scientific or modern illustration; `historic` a historical artwork or photograph; `photo` an ordinary photograph.",
        "",
        "| Key | Games | Shows | Kind | Commons file | Author | Licence | Changes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        *[
            f"| `{m['key']}` | {', '.join(m['games'])} | {m['shows']} | {m['kind']} | {m['file']} | {m['author'] or 'unknown'} | {m['licence']} | {m['changes']} |"
            for m in manifest
        ],
        "",
    ]
    doc.write_text("\n".join(table), encoding="utf-8", newline="\n")
    print(f"{len(manifest)} pictures, {total // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
