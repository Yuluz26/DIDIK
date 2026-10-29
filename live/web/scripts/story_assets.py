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
import os
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
    row = {"file": path.relative_to(OUT).as_posix(), "source": source, "status": status, "use": use}
    if path.suffix == ".webp":
        im = Image.open(path)
        row.update(size=list(im.size), alpha=im.mode == "RGBA")
    manifest.append({**row, "bytes": path.stat().st_size, **extra})


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


POSE_SHEETS = SRC / "Batch04/DIDIK_JRPG_Assets_Batch04_HD_Animation/01_ORIGINAL_HD_POSE_SHEETS"
POSES = ("idle", "ready", "attack", "cast", "hurt", "victory")


def pose_sheet(sheet: Path) -> dict[str, Image.Image]:
    """The six poses of a hero's sheet (three by two, each over a name plate), whole from head to feet.
    The pack's own extracted poses cut the feet off, so the poses are cut from the sheet: the navy
    name plates are blanked out, touching poses are parted at the emptiest column between them, and
    each pose keeps its figure and the sparks and petals around it. Every pose has the same height
    with its feet on the bottom edge, so all six share one scale and one ground."""
    rgba = np.array(Image.open(sheet).convert("RGBA"))
    h, w = rgba.shape[:2]
    alpha = rgba[..., 3].copy()
    r, g, b = (rgba[..., i].astype(int) for i in range(3))
    navy = (b > r + 18) & (np.maximum(np.maximum(r, g), b) < 120) & (alpha > 200)
    band = np.zeros_like(navy)
    for y0, y1 in ((465, 545), (990, 1070)):
        band[y0:y1] = True
    labels, _ = ndimage.label(navy & band)
    for ys, xs in ndimage.find_objects(labels):
        if xs.stop - xs.start > 120 and ys.stop - ys.start > 25:
            alpha[max(0, ys.start - 7):ys.stop + 7, max(0, xs.start - 26):xs.stop + 26] = 0
    solid = alpha > 20
    for y0, y1 in ((0, h // 2), (h // 2, h)):
        for x0, x1 in ((w // 3 - 50, w // 3 + 50), (2 * w // 3 - 50, 2 * w // 3 + 50)):
            solid[y0:y1, x0 + int(np.argmin(solid[y0:y1, x0:x1].sum(axis=0)))] = False
    labels, count = ndimage.label(solid)
    centres = ndimage.center_of_mass(solid, labels, range(1, count + 1))
    sizes = ndimage.sum(solid, labels, range(1, count + 1))
    masks = {}
    for i, pose in enumerate(POSES):
        cx0, cx1, cy0, cy1 = (i % 3) * w / 3, (i % 3 + 1) * w / 3, (i // 3) * h / 2, (i // 3 + 1) * h / 2
        ids = [k + 1 for k, (cy, cx) in enumerate(centres) if cx0 <= cx < cx1 and cy0 <= cy < cy1 and sizes[k] > 40]
        main = max(ids, key=lambda k: sizes[k - 1])
        near = ndimage.binary_dilation(labels == main, iterations=40)
        floor = max(300, sizes[main - 1] * 0.004)
        keep = np.isin(labels, [k for k in ids if k == main or (sizes[k - 1] >= floor and (near & (labels == k)).any())])
        masks[pose] = ndimage.binary_dilation(keep, iterations=2) & (alpha > 0)
    boxes = {p: (np.nonzero(m.any(1))[0], np.nonzero(m.any(0))[0]) for p, m in masks.items()}
    tall = max(ys[-1] - ys[0] + 1 for ys, _ in boxes.values())
    out = {}
    for pose, m in masks.items():
        ys, xs = boxes[pose]
        piece = rgba.copy()
        piece[..., 3] = np.where(m, alpha, 0)
        crop = piece[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]
        canvas = np.zeros((tall, crop.shape[1], 4), np.uint8)
        canvas[tall - crop.shape[0]:] = crop
        out[pose] = Image.fromarray(canvas, "RGBA")
    return out


def heroes() -> None:
    for hero, sheet, portrait in (("tuah", "Hang_Tuah_Six_Poses.png", "01_hang_tuah"), ("mahsuri", "Mahsuri_Six_Poses.png", "02_mahsuri")):
        for pose, im in pose_sheet(POSE_SHEETS / sheet).items():
            out = save_webp(im, OUT / "heroes" / hero / f"{pose}.webp")
            note(out, rel(POSE_SHEETS / sheet), "production pose sheet (Batch 04), cut whole with the name plates removed",
                 f"battle pose: {pose}", anchor="bottom-center")
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
    for heart in ("full", "half", "empty"):
        src = B02 / f"heart_icons/heart_{heart}.png"
        out = save_webp(Image.open(src).convert("RGBA"), OUT / "ui" / f"heart_{heart}.webp", 92)
        note(out, rel(src), "production UI icon (Batch 02)", "half-heart HUD")
    frames = sorted((B12 / "02_TRANSITION_ALPHA_FRAMES").glob("world_transition_*.png"))
    sheet = Image.new("RGBA", (640 * 4, 360 * 3))
    for i, f in enumerate(frames):
        sheet.paste(Image.open(f).convert("RGBA"), ((i % 4) * 640, (i // 4) * 360))
    out = save_webp(sheet, OUT / "fx" / "transition_4x3.webp", 85)
    note(out, [rel(f) for f in frames], "production alpha frames (Batch 12), packed 4x3", "world transition wipe",
         frames=12, frame=[640, 360])


# The emblems: a Google Noto Emoji picture (_asset_input/NotoEmoji/, Apache 2.0, fetched from
# fonts.gstatic.com/s/e/notoemoji/latest/<code>/512.png) on a gold-rimmed medallion in the world's or
# the element's own colours. A world's rim carries rivets, so it never reads as an element.
NOTO = SRC / "NotoEmoji"
# key: (emoji code point, light centre, dark edge)
ELEMENT_EMBLEMS = {"api": ("1f525", "#ff8a4c", "#6e1a0e"), "angin": ("1f32a", "#4fb8c4", "#0d3a52"),
                   "petir": ("26a1", "#7d70ec", "#1d1550"), "tanah": ("1faa8", "#d9a368", "#4a2a12"),
                   "air": ("1f4a7", "#7fd0ff", "#0c3a78")}
WORLD_EMBLEMS = {"chini": ("1fab7", "#43c9b8", "#0b4048"), "lupar": ("1f40a", "#f0a050", "#5a2a10"),
                 "larut": ("1f333", "#86c95a", "#163f1f"), "kancil": ("1f319", "#a47ae6", "#24104a"),
                 "ledang": ("1f3d4", "#7fa6d6", "#1b2c50")}


def hex_rgb(colour: str) -> np.ndarray:
    return np.array([int(colour[i:i + 2], 16) for i in (1, 3, 5)], float)


def medallion(code: str, light: str, dark: str, rivets: bool, size: int = 160) -> Image.Image:
    big = size * 4
    yy, xx = np.mgrid[0:big, 0:big].astype(float)
    c = big / 2
    r = np.hypot(xx - c, yy - c) / c
    rgba = np.zeros((big, big, 4))
    # the gold rim: a ring shaded from a bright top to a deep bottom, edged in dark brown
    t = np.clip((yy / big - 0.1) / 0.8, 0, 1)[..., None]
    gold = hex_rgb("#ffe7a3") * (1 - t) + hex_rgb("#b8761e") * t
    rim = (r <= 0.97) & (r > 0.8)
    rgba[r <= 1.0] = [*hex_rgb("#3b2208"), 255]
    rgba[rim, :3] = gold[rim]
    rgba[rim, 3] = 255
    # a fine bright line on the rim's inner and outer edges
    for edge in (0.94, 0.83):
        line = np.abs(r - edge) < 0.012
        rgba[line, :3] = rgba[line, :3] * 0.4 + 255 * 0.6
    # the disc: the colour glows from just above the middle out to the dark edge
    d = np.clip(np.hypot(xx - c, yy - c * 0.86) / (c * 0.86), 0, 1)[..., None] ** 1.3
    disc = r <= 0.8
    body = hex_rgb(light) * (1 - d) + hex_rgb(dark) * d
    rgba[disc, :3] = body[disc]
    rgba[disc, 3] = 255
    ring = disc & (np.abs(r - 0.755) < 0.012)
    rgba[ring, :3] = rgba[ring, :3] * 0.55 + hex_rgb(light) * 0.45
    if rivets:
        for k in range(12):
            a = k * np.pi / 6
            px, py = c + np.cos(a) * c * 0.885, c + np.sin(a) * c * 0.885
            dot = np.hypot(xx - px, yy - py) < big * 0.022
            rgba[dot, :3] = hex_rgb("#fff4cf")
    im = Image.fromarray(rgba.astype(np.uint8), "RGBA")
    # the picture, with a soft shadow under it
    pic = Image.open(NOTO / f"emoji_u{code}.png").convert("RGBA")
    pic.thumbnail((int(big * 0.62),) * 2, Image.LANCZOS)
    at = ((big - pic.width) // 2, (big - pic.height) // 2 + int(big * 0.01))
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    shade = Image.new("RGBA", pic.size, (0, 0, 0, 150))
    shade.putalpha(pic.getchannel("A").point(lambda v: v * 150 // 255))
    shadow.alpha_composite(shade, (at[0], at[1] + int(big * 0.03)))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(big * 0.02)))
    im.alpha_composite(pic, at)
    # a gloss across the top of the disc
    gloss = np.zeros((big, big), float)
    g = ((xx - c) / (c * 0.62)) ** 2 + ((yy - c * 0.5) / (c * 0.3)) ** 2 < 1
    gloss[g & disc] = 34
    im.alpha_composite(Image.merge("RGBA", [Image.new("L", im.size, 255)] * 3 + [Image.fromarray(gloss.astype(np.uint8)).filter(ImageFilter.GaussianBlur(big * 0.02))]))
    return im.resize((size, size), Image.LANCZOS)


def emblems() -> None:
    for el, (code, light, dark) in ELEMENT_EMBLEMS.items():
        out = save_webp(medallion(code, light, dark, rivets=False), OUT / "ui" / f"element_{el}.webp", 90)
        note(out, rel(NOTO / f"emoji_u{code}.png"), "Google Noto Emoji (Apache 2.0) on a drawn medallion", "element picker and HUD")
    for key, (code, light, dark) in WORLD_EMBLEMS.items():
        out = save_webp(medallion(code, light, dark, rivets=True), OUT / "ui" / f"symbol_{key}.webp", 90)
        note(out, rel(NOTO / f"emoji_u{code}.png"), "Google Noto Emoji (Apache 2.0) on a drawn medallion", "world map and world intro")


# The living battlefields: one short animated painting per world (_asset_input/WorldVideos/, 1280x720,
# 8 s, supplied by the project owner) with the water, mist and the boss moving. They fill the battle scene
# on their own; the still painting is only the fallback. Each frame is held to the video's own first frame
# (SIFT points, a similarity transform per frame), which takes out the camera's drift, zoom and shake, and
# the first frame is placed on the world's battlefield painting (the middle of many guesses). Every frame
# is then redrawn over one fixed 16:9 window of the painting: the largest that every frame covers.
# That window goes to views.ts, so the game lays the hero, the enemies and the masked boss over the video
# exactly where the painting has them. The last second is blended into the first, so the loop has no jump.
# The video's own sound goes into a separate file, and its first frame is kept as a still.
WORLD_VIDEOS = {"chini": "Tasik Chini", "lupar": "Batang Lupar", "larut": "Hutan Larut", "kancil": "Rimba Bayangan", "ledang": "Gunung Ledang"}
VIDEO_SIZE = (1280, 720)
LOOP_BLEND = 24
VIEWS_TS = ROOT / "live/web/src/lib/games/legenda/views.ts"


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def seamless_loop(frames: list[np.ndarray]) -> list[np.ndarray]:
    """A loop nobody notices: it is cut where an early frame and a late one look most alike (the water,
    mist and boss in nearly the same place), and the frames just past the cut are faded, on an eased curve,
    into the start, so the last frame leads straight into the first."""
    blend = LOOP_BLEND
    count = len(frames)
    small = [cv2.resize(cv2.cvtColor(f.astype(np.uint8), cv2.COLOR_BGR2GRAY), (160, 90), interpolation=cv2.INTER_AREA).astype(np.float32) for f in frames]
    # the loop keeps at least two thirds of the clip
    starts = range(0, count // 6)
    ends = range(count - count // 6 - blend, count - blend)
    start, end = min(((a, b) for a in starts for b in ends), key=lambda ab: float(np.abs(small[ab[0]] - small[ab[1]]).mean()))
    clip = frames[start:end + blend]
    length = end - start
    out = list(clip[:length])
    for i in range(blend):
        t = (i + 1) / (blend + 1)
        t = t * t * (3 - 2 * t)
        # frame i comes mostly from just past the cut at first, and wholly from the start by the end
        out[i] = clip[length + i] * (1 - t) + clip[i] * t
    return out


def world_videos() -> None:
    import subprocess

    sift = cv2.SIFT_create(6000)
    # a k-d tree finds the nearest points far faster than comparing every pair, with the same result here
    matcher = cv2.FlannBasedMatcher({"algorithm": 1, "trees": 5}, {"checks": 64})
    ow, oh = VIDEO_SIZE
    # DIDIK_VIDEO_KEYS=chini,lupar redoes only those worlds
    only = {k.strip() for k in os.environ.get("DIDIK_VIDEO_KEYS", "").split(",") if k.strip()}
    views = json.loads(VIEWS_TS.read_text(encoding="utf-8").split("=", 1)[1].rsplit(";", 1)[0]) if VIEWS_TS.exists() else {}
    for key, name in WORLD_VIDEOS.items():
        if only and key not in only:
            continue
        src = SRC / "WorldVideos" / f"{name}.mp4"
        if not src.exists():
            print(f"{src.name} not found: keeping worlds/{key}/scene.mp4")
            continue
        ref = cv2.cvtColor(np.array(Image.open(OUT / "worlds" / key / "field.webp").convert("RGB")), cv2.COLOR_RGB2GRAY)
        fh, fw = ref.shape
        k2, d2 = sift.detectAndCompute(ref, None)
        cap = cv2.VideoCapture(str(src))
        frames = []
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frames.append(frame)
        vh, vw = frames[0].shape[:2]

        def similarity(kp_a, des_a, kp_b, des_b, threshold: float) -> np.ndarray:
            good = [a for a, b in matcher.knnMatch(des_a, des_b, k=2) if a.distance < 0.75 * b.distance]
            pa = np.float32([kp_a[a.queryIdx].pt for a in good])
            pb = np.float32([kp_b[a.trainIdx].pt for a in good])
            m, _ = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=threshold)
            return np.vstack([m, [0, 0, 1]])

        def params_of(m: np.ndarray) -> tuple[float, float, float, float]:
            return np.hypot(m[0, 0], m[1, 0]), np.arctan2(m[1, 0], m[0, 0]), m[0, 2], m[1, 2]

        def matrix(sc: float, r: float, tx: float, ty: float) -> np.ndarray:
            return np.array([[sc * np.cos(r), -sc * np.sin(r), tx], [sc * np.sin(r), sc * np.cos(r), ty], [0, 0, 1]])

        # Each frame is held to the video's own first frame: the same picture, so hundreds of points agree
        # and the camera's drift, zoom and shake come out to a fraction of a pixel.
        k0, d0 = sift.detectAndCompute(cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY), None)
        to_first, to_painting = [], []
        for i, frame in enumerate(frames):
            k1, d1 = sift.detectAndCompute(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), None)
            s = np.eye(3) if i == 0 else similarity(k1, d1, k0, d0, 1.5)
            to_first.append(params_of(s))
            # and, every few frames, to the painting: each gives one guess at where the first frame lies on it
            if i % 6 == 0:
                to_painting.append(params_of(similarity(k1, d1, k2, d2, 3) @ np.linalg.inv(s)))
        to_first = ndimage.uniform_filter1d(np.array(to_first), size=5, axis=0, mode="nearest")
        # the first frame's place on the painting: the middle of all the guesses
        first_on_painting = matrix(*np.median(np.array(to_painting), axis=0))
        mats = [(first_on_painting @ matrix(*p))[:2] for p in to_first]
        # the window every frame covers, on the painting: inside each frame's four corners, then 16:9 about its middle
        left, top, right, bottom = 0.0, 0.0, float(fw), float(fh)
        for m in mats:
            c = (m @ np.array([[0, vw, vw, 0], [0, 0, vh, vh], [1, 1, 1, 1]], float)).T
            left, right = max(left, c[0, 0], c[3, 0]), min(right, c[1, 0], c[2, 0])
            top, bottom = max(top, c[0, 1], c[1, 1]), min(bottom, c[2, 1], c[3, 1])
        cx, cy = (left + right) / 2, (top + bottom) / 2
        w = min(right - left, (bottom - top) * ow / oh) * 0.995
        h = w * oh / ow
        x0, y0 = cx - w / 2, cy - h / 2
        to_out = np.array([[ow / w, 0, -x0 * ow / w], [0, oh / h, -y0 * oh / h], [0, 0, 1]])
        composed = [cv2.warpAffine(f, (to_out @ np.vstack([m, [0, 0, 1]]))[:2], (ow, oh), flags=cv2.INTER_LANCZOS4).astype(np.float32)
                    for f, m in zip(frames, mats)]
        composed = seamless_loop(composed)
        n = len(composed)

        out = OUT / "worlds" / key / "scene.mp4"
        temp = out.with_name("scene.part.mp4")
        # one keyframe group for the whole clip, so a browser going back to the start never waits on a seek
        cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{ow}x{oh}", "-r", "24", "-i", "-",
               "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p", "-g", str(n), "-keyint_min", str(n),
               "-sc_threshold", "0", "-movflags", "+faststart", "-an", str(temp)]
        enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for f in composed:
            enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
        enc.stdin.close()
        if enc.wait():
            sys.exit(f"ffmpeg failed on {src.name}")
        temp.replace(out)
        note(out, rel(src), "supplied animated battlefield, steadied on the painting, cut to one 16:9 window, seamless loop",
             "living battlefield, world intro, boss reveal, host screen", frames=n, size=[ow, oh])
        still = save_webp(Image.fromarray(cv2.cvtColor(np.clip(composed[0], 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)), OUT / "worlds" / key / "scene.webp", 82)
        note(still, rel(src), "the living battlefield's first frame", "poster while the video loads")
        sound = OUT / "worlds" / key / "scene.m4a"
        temp = sound.with_name("scene.part.m4a")
        subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(src), "-vn", "-c:a", "aac", "-b:a", "96k", str(temp)], check=True)
        temp.replace(sound)
        note(sound, rel(src), "the supplied video's own sound", "world intro and boss reveal")
        views[key] = {k: round(v, 4) for k, v in {"x": x0 / fw, "y": y0 / fh, "w": w / fw, "h": h / fh}.items()}
        print(key, views[key], f"{out.stat().st_size / 1e6:.1f} MB")
    VIEWS_TS.write_text(
        "// Written by live/web/scripts/story_assets.py (videos): the 16:9 window of each world's battlefield painting\n"
        "// that its living video shows, as fractions of the painting. The battle scene shows this window.\n"
        f"export const VIEWS: Record<string, {{ x: number; y: number; w: number; h: number }}> = {json.dumps(views)};\n",
        encoding="utf-8")


def fx() -> None:
    for el, stem in ELEMENTS.items():
        src = B05 / f"FX_{stem}_HD.png"
        im = Image.open(src).convert("RGBA")
        im = im.crop(im.getbbox())
        # only the enemy's projectile uses it, drawn at most about a tenth of the scene across
        im.thumbnail((360, 360), Image.LANCZOS)
        out = save_webp(im, OUT / "fx" / f"{el}.webp", 82)
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
        # soft glows: a lighter encoding does not show, and phones load these during the boss fight
        out = save_webp(sheet, OUT / "fx" / f"{el}_slash.webp", 80)
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


def boss_intros() -> None:
    """The five bosses' introduction portraits (BossIntro: one sheet of five on a transparent ground with
    a messy matte, and the same sheet on white). The outline comes from the white copy, how far each
    pixel is from white; the colours from the larger sheet. The names and labels under each are left out."""
    sheet_path, white_path = SRC / "BossIntro" / "boss_intro_sheet.png", SRC / "BossIntro" / "boss_intro_sheet_white.webp"
    if not sheet_path.exists() or not white_path.exists():
        print("BossIntro not found: keeping the introduction portraits already in static/story/worlds/")
        return
    hd = Image.open(sheet_path).convert("RGB")
    white = Image.open(white_path).convert("RGBA")
    ground = Image.new("RGBA", white.size, (255, 255, 255, 255))
    ground.alpha_composite(white)
    width, height = hd.size
    away = (255 - np.array(ground.convert("RGB").resize((width, height), Image.LANCZOS)).astype(np.float32)).max(axis=2)
    colours = np.array(hd).astype(np.float32)
    # each boss's cell, above its name (in pixels of the 1536 x 1024 sheet)
    cells = {"chini": (0, 0, 512, 470), "lupar": (512, 0, 1020, 470), "larut": (1020, 0, 1536, 470),
             "kancil": (0, 470, 776, 1024), "ledang": (776, 470, 1536, 1024)}
    for key, (x0, y0, x1, y1) in cells.items():
        cell = away[y0:y1, x0:x1]
        solid = cell > 30
        labels, count = ndimage.label(ndimage.binary_closing(solid, iterations=2))
        sizes = ndimage.sum(solid, labels, range(1, count + 1))
        main = int(np.argmax(sizes)) + 1
        bottom = np.nonzero(labels == main)[0].max()
        near = ndimage.binary_dilation(labels == main, iterations=14)
        keep = np.zeros_like(solid)
        for i in range(1, count + 1):
            part = labels == i
            # the boss and the wisps around it, never the name underneath
            if i == main or ((part & near).any() and np.nonzero(part)[0].max() <= bottom + 4):
                keep |= part
        alpha = np.clip((cell - 14) / 46, 0, 1) * ndimage.binary_dilation(keep, iterations=2)
        im = Image.fromarray(np.dstack([colours[y0:y1, x0:x1], alpha * 255]).astype(np.uint8), "RGBA")
        im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox())
        out = save_webp(im, OUT / "worlds" / key / "intro.webp", 88)
        note(out, [rel(sheet_path), rel(white_path)], "production boss introduction portrait (supplied sheet, cut out; about 500 px)",
             "boss reveal before the fight", anchor="bottom-center")


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
            note(save_webp(sheet, OUT / "banners" / f"{key}_sheet.webp", 80), rel(sheet_src),
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
    steps = {"heroes": heroes, "battlefields": battlefields, "ui": ui, "emblems": emblems, "fx": fx, "banners": banners, "weapons": hero_weapons, "intros": boss_intros, "videos": world_videos, "sound": sound}
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else []
    old = OUT / "manifest.json"
    if only and old.exists():
        # a partial run keeps the rows of the steps it does not run
        prefixes = {"heroes": "heroes/", "battlefields": tuple(f"worlds/{k}/{n}" for k in FIELD_ORDER for n in ("field", "boss", "minion_")), "ui": ("ui/heart_", "fx/transition"), "emblems": ("ui/element_", "ui/symbol_"), "fx": tuple(f"fx/{el}" for el in ELEMENTS), "banners": "banners/", "weapons": ("heroes/tuah/weapon/", "heroes/mahsuri/weapon/"), "intros": tuple(f"worlds/{k}/intro" for k in FIELD_ORDER), "videos": tuple(f"worlds/{k}/scene" for k in ([k.strip() for k in os.environ.get("DIDIK_VIDEO_KEYS", "").split(",") if k.strip()] or FIELD_ORDER)), "sound": "audio/"}
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
