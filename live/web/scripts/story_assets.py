"""Builds the Legenda Story Mode art in static/story/ from the supplied packs in _asset_input/.

Run from the repository root with Pillow, numpy, scipy and opencv-python-headless installed:

    python live/web/scripts/story_assets.py

Worlds 2-5 have no clean boss sprites or battle backgrounds in the packs, only concept art with the
boss, HUD and small characters painted in. For those, the script derives interim art and says so in
static/story/manifest.json:

- boss cut-outs from the close-up references, with point-prompted segmentation (rembg's SAM model).
  This step needs `pip install "rembg[cpu]"` and downloads the SAM model once. Without rembg the
  cut-outs already in static/story/bosses/ are kept.
- battle backgrounds from the 1536x1024 world concepts: the painted HUD, small characters and boss
  are filled with a soft colour field, cropped to 16:9 and softened slightly, so the boss sprite and
  the game's own HUD sit on top.

Everything else is converted from production-ready pack files without changing the art.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "_asset_input"
OUT = ROOT / "live" / "web" / "static" / "story"

B02 = SRC / "Batch02/DIDIK_JRPG_Batch02_TasikChini/06_GAME_READY_UI"
B03 = SRC / "Batch03/DIDIK_JRPG_Batch03_HD_TasikChini"
B04 = SRC / "Batch04/DIDIK_JRPG_Assets_Batch04_HD_Animation/02_EXTRACTED_POSES"
B05 = SRC / "Batch05/DIDIK_JRPG_Batch05_HD_ElementalCombat/01_ELEMENTAL_FX_TRANSPARENT"
B12 = SRC / "Batch12/Batch12_Final_UI_Transitions_SFX_HD"
FX60 = SRC / "Effects60/04_ATTACK_FRAMES"
B14 = SRC / "Batch14/DIDIK_Legenda_Batch14_Transition_Text_HD"
HW = SRC / "HeroElements/didik_element_weapons_pack/assets/heroes"
# The transition banners the story shows; keep in step with show(...) in LegendaPlayer.svelte.
BANNERS_USED = {"dunia_seterusnya", "pertarungan_bermula", "elemen_dibuka", "boss_muncul", "boss_dikalahkan", "cuba_lagi",
                "kemenangan", "pilih_elemen", "jawapan_betul", "jawapan_salah", "boss_akan_menyerang", "serangan_balas",
                "nyawa_berkurang"}
# The weapon pack names the elements in English; the server and the game use these ids.
HW_IDS = {"fire": "api", "wind": "angin", "lightning": "petir", "earth": "tanah", "water": "air"}
# The supplied battlefield paintings (_asset_input/Battlefields/) and, in 1536-wide pixels: where the painting
# has its own hearts, boss panel and element row (replaced by the live HUD), the points that pick the boss out
# for SAM, and the body centres of the two small enemies and the hero.
BATTLEFIELDS = {
    "chini": dict(file="tasik_chini_battlefield.jpg", clip_below=540, hearts=(250, 18, 492, 66), panel=(978, 16, 1332, 122), dock=(1028, 738, 1482, 852),
                  boss=[(1165, 300), (1250, 200), (1330, 330), (1260, 480), (1190, 640), (1370, 600), (1050, 420)],
                  who={"minA": (240, 500), "hero": (400, 570), "minB": (530, 670)}),
    "lupar": dict(file="batang_lupar_battlefield.png", hearts=(252, 18, 510, 78), panel=(988, 8, 1335, 128), dock=(1008, 878, 1488, 1004),
                  boss=[(1100, 520), (1250, 380), (1400, 450), (1450, 600), (1200, 300)],
                  who={"minA": (150, 505), "hero": (285, 570), "minB": (395, 650)}),
    "larut": dict(file="hutan_larut_battlefield.png", hearts=(252, 18, 510, 78), panel=(988, 12, 1340, 122), dock=(1020, 878, 1480, 996),
                  boss=[(1180, 230), (1000, 250), (1380, 250), (1180, 450), (1330, 520), (1100, 520)],
                  who={"minA": (225, 495), "hero": (370, 570), "minB": (560, 640)}),
    "kancil": dict(file="rimba_bayangan_battlefield.png", hearts=(252, 18, 510, 78), panel=(975, 16, 1335, 130), dock=(1018, 884, 1484, 1004),
                   boss=[(1200, 250), (1200, 400), (1050, 420), (1350, 400), (1150, 170)],
                   who={"minA": (215, 525), "hero": (375, 585), "minB": (500, 670)}),
    "ledang": dict(file="gunung_ledang_battlefield.png", hearts=(252, 18, 510, 78), panel=(958, 8, 1318, 124), dock=(1012, 876, 1486, 1004),
                   boss=[(1200, 250), (1200, 400), (1040, 420), (1400, 380), (1200, 170)],
                   who={"minA": (215, 478), "hero": (360, 560), "minB": (275, 680)}),
}
FIELD_ORDER = ["chini", "lupar", "larut", "kancil", "ledang"]
ELEMENTS = {"api": "FIRE_CRESCENT_SLASH", "angin": "WIND_VORTEX", "petir": "LIGHTNING_THUNDERBURST",
            "tanah": "EARTHSHATTER", "air": "WATER_CRESCENT_TIDE"}

manifest: list[dict] = []


def note(path: Path, source: str | list[str], status: str, use: str, **extra) -> None:
    im = Image.open(path)
    manifest.append({
        "file": path.relative_to(OUT).as_posix(),
        "source": source,
        "status": status,
        "use": use,
        "size": list(im.size),
        "alpha": im.mode == "RGBA",
        "bytes": path.stat().st_size,
        **extra,
    })


def save_webp(im: Image.Image, path: Path, quality: int = 86) -> Path:
    """Writes to a temporary file and renames it, so an interrupted or overlapping run never leaves a
    half-written image behind."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".part")
    # method 6: the slowest, smallest encoding; the same quality as 4, about a tenth smaller
    im.save(temp, "WEBP", quality=quality, method=6)
    temp.replace(path)
    return path


def tidy_alpha(im: Image.Image, keep: float = 0.02) -> Image.Image:
    """Drops the stray slivers left by the manual pose extraction (gold rule lines, neighbour edges)
    and crops to the figure, so every pose has the same bottom-centre anchor."""
    im = im.convert("RGBA")
    alpha = np.array(im)[:, :, 3]
    solid = alpha > 24
    labels, count = ndimage.label(solid)
    if count:
        sizes = ndimage.sum(solid, labels, range(1, count + 1))
        wanted = [i + 1 for i, s in enumerate(sizes) if s >= sizes.max() * keep]
        mask = np.isin(labels, wanted)
        mask = ndimage.binary_dilation(mask, iterations=2)
        alpha = np.where(mask, alpha, 0).astype(np.uint8)
    out = np.array(im)
    out[:, :, 3] = alpha
    result = Image.fromarray(out)
    return result.crop(result.getbbox())


def rel(path: Path) -> str:
    return path.relative_to(SRC).as_posix()


# ------------------------------------------------------------------ heroes and Naga Chini


def heroes() -> None:
    for hero, folder, portrait in (("tuah", "HANG_TUAH", "01_hang_tuah"), ("mahsuri", "MAHSURI", "02_mahsuri")):
        for pose in ("idle", "ready", "attack", "cast", "hurt", "victory"):
            src = B04 / folder / f"{folder.lower()}_{pose}.png"
            out = save_webp(tidy_alpha(Image.open(src)), OUT / "heroes" / hero / f"{pose}.webp")
            note(out, rel(src), "production pose still (Batch 04), stray edges removed", f"battle pose: {pose}",
                 anchor="bottom-center")
        src = next((B03 / "02_HERO_CHARACTERS").glob(f"{portrait}_battle_pose_transparent_*.png"))
        im = tidy_alpha(Image.open(src))
        im.thumbnail((600, 800), Image.LANCZOS)
        out = save_webp(im, OUT / "heroes" / hero / "portrait.webp")
        note(out, rel(src), "production full-body pose (Batch 03)", "character select, world clear")


def soft_fill(arr: np.ndarray, mask: np.ndarray, sigma: float) -> np.ndarray:
    """Normalised convolution: fills the masked area with the blurred colours around it, widening the
    blur wherever the first pass finds nothing to borrow. Wide blurs run on a quarter-size copy."""
    if sigma >= 24:
        h, w = mask.shape
        small = soft_fill(cv2.resize(arr, (w // 4, h // 4), interpolation=cv2.INTER_AREA),
                          cv2.resize(mask.astype(np.uint8), (w // 4, h // 4), interpolation=cv2.INTER_NEAREST), sigma / 4)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)
    valid = (mask == 0).astype(np.float32)
    result = None
    need = np.ones(mask.shape, bool)
    for s in (sigma, sigma * 2.5, sigma * 6, sigma * 15):
        num = cv2.GaussianBlur(arr * valid[:, :, None], (0, 0), s)
        den = cv2.GaussianBlur(valid, (0, 0), s)
        layer = num / np.maximum(den, 1e-4)[:, :, None]
        if result is None:
            result = layer.copy()
        ok = den > 0.08
        result[need & ok] = layer[need & ok]
        need &= ~ok
        if not need.any():
            break
    result[need] = layer[need]
    return result


def shift_fill(img: np.ndarray, hole: np.ndarray, protect: np.ndarray | None = None, scale: float = 0.5) -> np.ndarray:
    """Fills `hole` with new scenery built from the rest of the painting (OpenCV's shift-map inpainting,
    run at `scale`), so what shows through a gap around a cut-out is water, stone and leaves, not a flat
    smear. The new scenery is blended in with Poisson cloning, so its colours meet the painting without a
    seam. `protect` marks painted parts that stay (the title plate, the minimap): the scenery is not
    allowed to copy from them. Falls back to the blur when OpenCV has no xphoto."""
    if not hasattr(cv2, "xphoto"):
        return soft_fill(img.astype(np.float32), hole.astype(np.uint8) * 255, 40)
    h, w = hole.shape
    banned = hole if protect is None else (hole | protect)
    small = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    holes = cv2.resize(banned.astype(np.uint8) * 255, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    filled = np.zeros_like(small)
    cv2.xphoto.inpaint(small, (holes == 0).astype(np.uint8) * 255, filled, cv2.xphoto.INPAINT_SHIFTMAP)
    big = cv2.resize(filled, (w, h), interpolation=cv2.INTER_CUBIC)
    pad = 16
    dst = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_REFLECT)
    src = cv2.copyMakeBorder(big, pad, pad, pad, pad, cv2.BORDER_REFLECT)
    mask = np.zeros(dst.shape[:2], np.uint8)
    mask[pad:pad + h, pad:pad + w] = hole.astype(np.uint8) * 255
    x, y, bw, bh = cv2.boundingRect(mask)
    merged = cv2.seamlessClone(src, dst, mask, (x + bw // 2, y + bh // 2), cv2.NORMAL_CLONE)
    return merged[pad:pad + h, pad:pad + w]


def sam_session():
    try:
        from rembg import new_session, remove
    except ImportError:
        return None
    return new_session("sam"), remove


def cutout(session, image: Image.Image, positive, negative=()) -> np.ndarray:
    sess, remove = session
    prompt = [{"type": "point", "data": list(p), "label": 1} for p in positive]
    prompt += [{"type": "point", "data": list(p), "label": 0} for p in negative]
    return np.array(remove(image, session=sess, sam_prompt=prompt))[:, :, 3] > 100


def field_masks(key: str, im: Image.Image) -> dict[str, np.ndarray]:
    """SAM masks of the boss and the three small characters of a battlefield. Cached in
    _asset_input/Battlefields/masks/ so a rerun does not need rembg or the model."""
    cache = SRC / "Battlefields" / "masks" / f"{key}.npz"
    if cache.exists():
        return dict(np.load(cache))
    session = sam_session()
    if session is None:
        sys.exit(f"{cache} is missing and rembg is not installed")
    spec = BATTLEFIELDS[key]
    masks = {"boss": cutout(session, im, spec["boss"])}
    for who, (cx, cy) in spec["who"].items():
        m = cutout(session, im, [(cx, cy - 32), (cx, cy), (cx, cy + 26), (cx - 18, cy - 4), (cx + 18, cy - 4)])
        window = np.zeros_like(m)
        window[max(0, cy - 95): cy + 70, max(0, cx - 80): cx + 80] = True
        m &= window
        labels, count = ndimage.label(m)
        if count:
            at = labels[cy, cx] or labels[cy - 20, cx] or np.bincount(labels[labels > 0]).argmax()
            m = labels == at
        masks[who] = ndimage.binary_fill_holes(m)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, **masks)
    return masks


def sprite_from(arr: np.ndarray, mask: np.ndarray, grow: int = 2) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """A cut-out of the painting: its pixels, feathered at the edge, cropped to its box."""
    solid = ndimage.binary_dilation(mask, iterations=grow) if grow else mask
    alpha = ndimage.gaussian_filter(solid.astype(np.float32), 0.9)
    rgba = np.dstack([arr, alpha * 255]).astype(np.uint8)
    box = Image.fromarray((solid * 255).astype(np.uint8)).getbbox()
    return Image.fromarray(rgba, "RGBA").crop(box), box


def patch_fill(img: np.ndarray, boxes: list[tuple[int, int, int, int]], avoid: np.ndarray) -> np.ndarray:
    """Covers each box with a patch of the same painting: the nearby area of the same size whose surrounding
    ring matches best, blended in with Poisson cloning. Keeps the dirt path's texture where a blur or
    inpainting smears it. `avoid` marks places a patch must not be taken from (the boss)."""
    h, w = img.shape[:2]
    out = img.copy()
    taken = avoid.copy()
    own = np.zeros_like(avoid)
    for x0, y0, x1, y1 in boxes:
        taken[max(0, y0 - 14): y1 + 14, max(0, x0 - 14): x1 + 14] = True
        own[y0:y1, x0:x1] = True
    integral = np.pad(taken.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))

    def blocked(x0, y0, x1, y1) -> int:
        return integral[y1, x1] - integral[y0, x1] - integral[y1, x0] + integral[y0, x0]

    for x0, y0, x1, y1 in boxes:
        bw, bh, r = x1 - x0, y1 - y0, 8
        ex0, ey0, ex1, ey1 = x0 - r, y0 - r, x1 + r, y1 + r
        if ex0 < 0 or ey0 < 0 or ex1 > w or ey1 > h:
            continue
        ring = np.ones((bh + 2 * r, bw + 2 * r), bool)
        ring[r: r + bh, r: r + bw] = False
        target = img[ey0:ey1, ex0:ex1].astype(np.float32)
        valid = ring & ~own[ey0:ey1, ex0:ex1] & ~avoid[ey0:ey1, ex0:ex1]
        count = max(1, int(valid.sum()))
        best, best_at = None, None
        for cy in range(max(0, ey0 - 220), min(h - bh - 2 * r, ey0 + 220), 5):
            for cx in range(max(0, ex0 - 280), min(w - bw - 2 * r, ex0 + 280), 5):
                if abs(cx - ex0) < bw // 2 and abs(cy - ey0) < bh // 2:
                    continue
                if blocked(cx, cy, cx + bw + 2 * r, cy + bh + 2 * r):
                    continue
                diff = img[cy: cy + bh + 2 * r, cx: cx + bw + 2 * r].astype(np.float32) - target
                score = float((diff * diff)[valid].sum()) / count
                if best is None or score < best:
                    best, best_at = score, (cx, cy)
        if best_at is None:
            continue
        cx, cy = best_at
        src = img[cy + r: cy + r + bh, cx + r: cx + r + bw]
        mask = np.full((bh, bw), 255, np.uint8)
        out = cv2.seamlessClone(src, out, mask, (x0 + bw // 2, y0 + bh // 2), cv2.NORMAL_CLONE)
    return out


def battlefields() -> None:
    """The five battlefields: the supplied painting with its boss, its three small characters and the parts
    the game now draws live (hearts, boss panel, element row) taken out, plus the boss and the two small
    enemies as separate cut-outs, and layout.ts with where everything stands."""
    entries = {}
    for key in FIELD_ORDER:
        spec = BATTLEFIELDS[key]
        src = SRC / "Battlefields" / spec["file"]
        im = Image.open(src).convert("RGB")
        width, height = im.size
        arr = np.array(im).astype(np.float32)
        masks = field_masks(key, im)
        if "clip_below" in spec:  # the segmentation leaked into the stone arena under the boss
            masks["boss"][spec["clip_below"]:, :] = False
        # a boss with holes in it shows the backdrop through them: close the small ones
        masks["boss"] = ndimage.binary_fill_holes(ndimage.binary_closing(masks["boss"], iterations=3))
        # pieces of the painted boss name and bar, the compass and the title plate that SAM took along: small
        # pieces whose middle lies in one of those places are not the boss
        labels, count = ndimage.label(masks["boss"])
        if count > 1:
            sizes = ndimage.sum(masks["boss"], labels, range(1, count + 1))
            ui_places = [spec["panel"], spec["hearts"], (1320, 0, labels.shape[1], 222), (0, 0, 252, 104)]
            for i, centre in enumerate(ndimage.center_of_mass(masks["boss"], labels, range(1, count + 1))):
                cy, cx = centre
                if sizes[i] < sizes.max() * 0.05 and any(x0 <= cx <= x1 and y0 <= cy <= y1 for x0, y0, x1, y1 in ui_places):
                    masks["boss"][labels == i + 1] = False


        # the small enemies' painted health bars are not part of the enemy
        for who in ("minA", "minB"):
            m = masks[who]
            red = (arr[..., 0] > 170) & (arr[..., 1] < 70) & (arr[..., 2] < 70)
            m = m & ~ndimage.binary_dilation(red & m, iterations=2)
            labels, count = ndimage.label(m)
            if count > 1:
                m = labels == np.bincount(labels[labels > 0]).argmax()
            masks[who] = m
        bars = np.zeros_like(masks["boss"])
        red = (arr[..., 0] > 170) & (arr[..., 1] < 70) & (arr[..., 2] < 70)
        for who in ("minA", "minB"):
            ys, xs = np.nonzero(masks[who])
            window = np.zeros_like(red)
            window[max(0, ys.min() - 40): ys.min() + 4, max(0, xs.min() - 30): xs.max() + 30] = True
            bars |= ndimage.binary_dilation(red & window, iterations=3)

        # the field: everything that moves or is live is filled with the colours around it
        out = arr.copy()

        # SAM misses parts of the small characters (red clothes, the sword tip) and their health bars have
        # outlines: take out a generous box around each instead of only the mask, and cover it with a patch
        # of the same painting
        boxes = []
        for who in ("hero", "minA", "minB"):
            ys, xs = np.nonzero(masks[who])
            x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
            if who == "hero":
                boxes.append((max(0, x0 - 12), max(0, y0 - 14), x1 + 46, y1 + 10))
            else:
                boxes.append((max(0, x0 - 12), max(0, y0 - 38), x1 + 12, y1 + 8))
        keep_away = ndimage.binary_dilation(masks["boss"], iterations=24)
        for name in ("hearts", "panel", "dock"):
            hx0, hy0, hx1, hy1 = spec[name]
            keep_away[hy0:hy1, hx0:hx1] = True
        out = patch_fill(np.clip(out, 0, 255).astype(np.uint8), boxes, keep_away).astype(np.float32)
        # the boss's place and the parts drawn live (hearts, boss panel, element row) become new scenery
        # built from the rest of the painting, so nothing flat shows if the boss moves or has a gap
        gone = ndimage.binary_dilation(masks["boss"], iterations=8)
        for name in ("hearts", "panel", "dock"):
            x0, y0, x1, y1 = spec[name]
            gone[y0:y1, x0:x1] = True
        painted = np.zeros_like(gone)  # the title plate and the minimap stay as painted
        painted[0:104, 0:252] = True
        painted[0:222, 1320:] = True
        painted &= ~gone
        out = shift_fill(np.clip(out, 0, 255).astype(np.uint8), gone, painted).astype(np.float32)
        field = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        field_out = save_webp(field, OUT / "worlds" / key / "field.webp", 88)
        note(field_out, rel(src), "supplied battlefield painting with its boss, small characters, hearts, boss "
             "panel and element row taken out (filled with the surrounding colours); the title plate and minimap "
             "stay as painted", "battlefield backdrop")

        # the boss and the two small enemies, cut from the painting itself
        boss_img, bbox = sprite_from(arr, masks["boss"])
        boss_out = save_webp(boss_img, OUT / "worlds" / key / "boss.webp", 90)
        note(boss_out, rel(src), "boss cut out of the supplied painting with SAM (native painting detail)",
             "boss, drawn over the field where it stands", anchor="bottom-center")
        entry = {"boss": bbox}
        for who, name in (("minA", "minion_a"), ("minB", "minion_b")):
            img, box = sprite_from(arr, masks[who])
            note(save_webp(img, OUT / "worlds" / key / f"{name}.webp", 90), rel(src),
                 "small enemy cut out of the supplied painting with SAM (native painting detail, small)", "road enemy",
                 anchor="bottom-center")
            entry[who] = box
        hx0, hy0, hx1, hy1 = Image.fromarray((masks["hero"] * 255).astype(np.uint8)).getbbox()
        entry["hero"] = ((hx0 + hx1) / 2, hy1)
        entry["size"] = (width, height)
        entries[key] = entry

    def box(b, size):
        w, h = size
        return f"box({b[0] / w:.4f}, {b[1] / h:.4f}, {(b[2] - b[0]) / w:.4f}, {(b[3] - b[1]) / h:.4f})"

    rows = []
    for key in FIELD_ORDER:
        e, spec = entries[key], BATTLEFIELDS[key]
        size = e["size"]
        w, h = size
        hud = {n: spec[n] for n in ("hearts", "panel", "dock")}
        rows.append("\t{ ar: " + f"{w} / {h}" + ", boss: " + box(e["boss"], size) + ", minA: " + box(e["minA"], size)
                    + ", minB: " + box(e["minB"], size) + f", hero: {{ x: {e['hero'][0] / w:.4f}, y: {e['hero'][1] / h:.4f} }}, "
                    + ", ".join(f"{n}: " + box(hud[n], size) for n in hud) + " }")
    text = (LAYOUT_HEAD + "export const FIELDS: Field[] = [\n" + ",\n".join(rows) + "\n];\n")
    (ROOT / "live/web/src/lib/games/legenda/layout.ts").write_text(text, encoding="utf-8")


LAYOUT_HEAD = """// Where everything stands on each world's battlefield, as fractions of the scene (left, top, width, height).
// Generated by scripts/story_assets.py from the supplied battlefield paintings: do not edit by hand.

export interface Box {
	x: number;
	y: number;
	w: number;
	h: number;
}

export interface Field {
	/** Width over height of the painting. */
	ar: number;
	boss: Box;
	minA: Box;
	minB: Box;
	/** Where the hero's feet stand. */
	hero: { x: number; y: number };
	hearts: Box;
	panel: Box;
	dock: Box;
}

const box = (x: number, y: number, w: number, h: number): Box => ({ x, y, w, h });

// The order is chini, lupar, larut, kancil, ledang.
"""


# ------------------------------------------------------------------ UI, effects, sound


def ui() -> None:
    for el in ELEMENTS:
        src = B02 / f"element_icons/element_{el}.png"
        im = Image.open(src).convert("RGBA")
        im.thumbnail((160, 160), Image.LANCZOS)
        out = save_webp(im, OUT / "ui" / f"element_{el}.webp", 90)
        note(out, rel(src), "production UI icon (Batch 02)", "element picker")
    for heart in ("full", "half", "empty"):
        src = B02 / f"heart_icons/heart_{heart}.png"
        out = save_webp(Image.open(src).convert("RGBA"), OUT / "ui" / f"heart_{heart}.webp", 92)
        note(out, rel(src), "production UI icon (Batch 02)", "half-heart HUD")
    symbols = {"chini": "world_01_tasik_chini", "lupar": "world_01_batang_lupar", "larut": "world_02_hutan_larut",
               "kancil": "world_03_rimba_bayangan", "ledang": "world_04_gunung_ledang"}
    for key, stem in symbols.items():
        src = B12 / f"01_UI_GAME_READY/{stem}_symbol.png"
        im = Image.open(src).convert("RGBA")
        im = im.crop(im.getbbox())
        im.thumbnail((160, 160), Image.LANCZOS)
        out = save_webp(im, OUT / "ui" / f"symbol_{key}.webp", 90)
        note(out, rel(src), "production UI emblem (Batch 12)", "world map and world intro")
    frames = sorted((B12 / "02_TRANSITION_ALPHA_FRAMES").glob("world_transition_*.png"))
    sheet = Image.new("RGBA", (640 * 4, 360 * 3))
    for i, f in enumerate(frames):
        sheet.paste(Image.open(f).convert("RGBA"), ((i % 4) * 640, (i // 4) * 360))
    out = save_webp(sheet, OUT / "fx" / "transition_4x3.webp", 85)
    note(out, [rel(f) for f in frames], "production alpha frames (Batch 12), packed 4x3", "world transition wipe",
         frames=12, frame=[640, 360])


def fx() -> None:
    for el, stem in ELEMENTS.items():
        src = B05 / f"FX_{stem}_HD.png"
        im = Image.open(src).convert("RGBA")
        im = im.crop(im.getbbox())
        im.thumbnail((720, 720), Image.LANCZOS)
        out = save_webp(im, OUT / "fx" / f"{el}.webp", 86)
        note(out, rel(src), "production transparent VFX still (Batch 05)", "attack burst, tweened in code")
    attack_frames()


def clean_frame(im: Image.Image) -> Image.Image:
    """Drops the neighbouring cell's bleed from a frame cut out of a contact sheet: pieces that touch a
    side edge and are small next to the main piece."""
    a = np.array(im.convert("RGBA"))
    solid = a[..., 3] > 28
    near = ndimage.binary_dilation(solid, iterations=6)  # the fragments of one effect stay joined
    labels, count = ndimage.label(near)
    if count < 2:
        return im.convert("RGBA")
    sizes = ndimage.sum(solid, labels, range(1, count + 1))
    big = sizes.max()
    w = solid.shape[1]
    keep = np.zeros(count + 1, bool)
    for i, box in enumerate(ndimage.find_objects(labels), 1):
        touches = box[1].start <= 1 or box[1].stop >= w - 1
        keep[i] = not (touches and sizes[i - 1] < big * 0.45 and sizes[i - 1] != big)
    a[..., 3] = np.where(keep[labels], a[..., 3], 0)
    return Image.fromarray(a)


def attack_frames() -> None:
    """The five elements' 12-frame attack effects, packed 4 by 3 (each frame 314x418) into one sheet."""
    if not FX60.exists():
        print("Effects60 not found: keeping the sheets already in static/story/fx/")
        return
    for el in ELEMENTS:
        frames = sorted((FX60 / el).glob(f"fx_{el}_frame_*.png"))
        assert len(frames) == 12, (el, len(frames))
        sheet = Image.new("RGBA", (314 * 4, 418 * 3))
        for i, f in enumerate(frames):
            sheet.paste(clean_frame(Image.open(f)), ((i % 4) * 314, (i // 4) * 418))
        out = save_webp(sheet, OUT / "fx" / f"{el}_slash.webp", 90)
        note(out, [rel(f) for f in frames], "production 12-frame attack effect (Effects60 pack; AI-generated frames "
             "cut from a contact sheet, neighbour bleed removed, native 314x418 per frame)",
             "attack and counterattack effect, played frame by frame", frames=12, frame=[314, 418], columns=4)


def clean_weapon(im: Image.Image) -> Image.Image:
    """A hero from the weapon pack, cleaned: the magenta key colour left inside the picture (between the arm and
    the body, inside swirls) made transparent, pink fringes pulled back, and the shards of the neighbouring
    cell or other stray pieces far from the figure removed."""
    a = np.array(im.convert("RGBA")).astype(np.float32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    al = np.where((r > 190) & (b > 190) & (g < 120) & (np.abs(r - b) < 70), 0, al)
    solid = al > 24
    edge = ndimage.binary_dilation(~solid, iterations=3) & solid
    fringe = edge & (np.minimum(r, b) - g > 35) & (np.abs(r - b) < 90)
    a[..., 0] = np.where(fringe, g + 0.35 * (r - g), r)
    a[..., 2] = np.where(fringe, g + 0.35 * (b - g), b)
    near = ndimage.binary_dilation(solid, iterations=18)
    labels, count = ndimage.label(near)
    if count > 1:
        sizes = ndimage.sum(solid, labels, range(1, count + 1))
        al = np.where(labels == (int(np.argmax(sizes)) + 1), al, 0)
    a[..., 3] = al
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def hero_weapons() -> None:
    """Each hero holding each element's weapon (the weapon pack, concept art). The five of a hero are cut to
    one shared box, so the figure stays where it is when the element changes."""
    if not HW.exists():
        print("HeroElements not found: keeping the weapon sprites already in static/story/heroes/")
        return
    for hero in ("tuah", "mahsuri"):
        cleaned = {}
        for english, el in HW_IDS.items():
            cleaned[el] = (HW / hero / english / "equipped_ready.png", clean_weapon(Image.open(HW / hero / english / "equipped_ready.png")))
        boxes = [im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox() for _, im in cleaned.values()]
        box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        for el, (src, im) in cleaned.items():
            im = im.crop(box)
            im.thumbnail((900, 700), Image.LANCZOS)
            out = save_webp(im, OUT / "heroes" / hero / "weapon" / f"{el}.webp", 88)
            note(out, rel(src), "CONCEPT hero holding the element's weapon (AI-generated, magenta key cleaned); a taller, "
                 "more realistic style than the base chibi poses, one pose only", "hero while the element is active",
                 anchor="bottom-center")


def banners() -> None:
    """The transition text banners (Batch 14): the 22 static banners at 1280x320, and the six that are
    animated as 12-frame sheets (4 by 3 frames of 960x240). Also writes lib/games/legenda/banners.ts with
    the Malay text of each, which the game shows to screen readers."""
    csv_path = B14 / "asset_messages.csv"
    if not csv_path.exists():
        print("Batch14 not found: keeping the banners already in static/story/banners/")
        return
    import csv

    # only the banners the game shows (LegendaPlayer.svelte); the rest of the pack stays in Batch14
    rows = [r for r in csv.DictReader(csv_path.open(encoding="utf-8-sig")) if r["id"] in BANNERS_USED]
    animated = []
    for row in rows:
        key = row["id"]
        src = B14 / row["banner_png"]
        im = Image.open(src).convert("RGBA")
        im = im.resize((1280, 320), Image.LANCZOS)
        note(save_webp(im, OUT / "banners" / f"{key}.webp", 88), rel(src),
             "production banner text (Batch 14: vector-authored, Malay spelling fixed)", row["usage"])
        sheet_src = B14 / "06_SPRITESHEETS" / f"{key}_12frames_4x3.png"
        if sheet_src.exists():
            sheet = Image.open(sheet_src).convert("RGBA").resize((960 * 4, 240 * 3), Image.LANCZOS)
            note(save_webp(sheet, OUT / "banners" / f"{key}_sheet.webp", 86), rel(sheet_src),
                 "production animated banner (Batch 14, 12 frames)", row["usage"], frames=12, frame=[960, 240], columns=4)
            animated.append(key)
    lines = ["// The transition text banners (Batch 14). Generated by scripts/story_assets.py: do not edit by hand.", "",
             "export interface Banner {", "\ttext: string;", "\t/** Played as a 12-frame sheet; the rest are one picture. */", "\tanimated: boolean;", "}", "",
             "export const BANNERS: Record<string, Banner> = {"]
    for row in rows:
        text = row["ms_text"].replace("'", "\\'")
        lines.append(f"\t{row['id']}: {{ text: '{text}', animated: {str(row['id'] in animated).lower()} }},")
    lines.append("};")
    (ROOT / "live/web/src/lib/games/legenda/banners.ts").write_text("\n".join(lines) + "\n", encoding="utf-8")


def sound() -> None:
    folder = OUT / "audio"
    folder.mkdir(parents=True, exist_ok=True)
    for f in sorted((B12 / "03_SYNTH_SFX_DEMOS").glob("*.wav")):
        out = folder / f.name
        out.write_bytes(f.read_bytes())
        manifest.append({"file": out.relative_to(OUT).as_posix(), "source": rel(f), "bytes": out.stat().st_size,
                         "status": "synthesised demo SFX (Batch 12); replace with designed sound before release",
                         "use": "battle feedback"})


def main() -> None:
    if not SRC.exists():
        sys.exit("_asset_input/ not found")
    steps = {"heroes": heroes, "battlefields": battlefields, "ui": ui, "fx": fx, "banners": banners, "weapons": hero_weapons, "sound": sound}
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else []
    old = OUT / "manifest.json"
    if only and old.exists():
        # a partial run keeps the rows of the steps it does not run
        prefixes = {"heroes": "heroes/", "battlefields": "worlds/", "ui": "ui/", "fx": "fx/", "banners": "banners/", "weapons": ("heroes/tuah/weapon/", "heroes/mahsuri/weapon/"), "sound": "audio/"}
        dropped = tuple(p for name in only for p in ((prefixes[name],) if isinstance(prefixes[name], str) else prefixes[name]))
        manifest.extend(r for r in json.loads(old.read_text(encoding="utf-8"))["assets"] if not r["file"].startswith(dropped))
    for name, step in steps.items():
        if not only or name in only:
            step()
    manifest.sort(key=lambda row: row["file"])
    (OUT / "manifest.json").write_text(json.dumps({
        "about": "Legenda Story Mode art. Built by live/web/scripts/story_assets.py from _asset_input/. "
                 "Licence: supplied by the DIDIK project owner; AI-assisted art per the pack notes.",
        "assets": manifest,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    total = sum(row["bytes"] for row in manifest)
    print(f"{len(manifest)} assets, {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
