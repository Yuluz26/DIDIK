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
WORLD_PACKS = {
    "lupar": ("Batch08/Batch08_BatangLupar_World_HD", "batang_lupar"),
    "larut": ("Batch09/Batch09_HutanLarut_World_HD", "hutan_larut"),
    "kancil": ("Batch10/Batch10_RimbaBayangan_World_HD", "rimba_bayangan"),
    "ledang": ("Batch11/Batch11_GunungLedang_World_HD", "gunung_ledang"),
}

# Points on each boss in its 640x680 close-up (positive) and on scenery beside it (negative).
CLOSEUP_POINTS = {
    "lupar": ([(282, 333), (339, 262), (371, 218), (422, 179), (486, 154), (538, 320), (563, 256), (550, 384),
               (600, 300), (470, 400), (250, 390)], [(100, 560), (330, 560)]),
    "larut": ([(256, 256), (128, 192), (435, 166), (256, 422), (435, 422), (256, 77), (358, 358), (128, 333),
               (192, 422), (435, 486), (340, 300)], [(320, 600)]),
    "kancil": ([(294, 141), (307, 282), (192, 307), (422, 294), (333, 358), (250, 60), (380, 200)],
               [(312, 420), (150, 450)]),
    "ledang": ([(282, 154), (282, 294), (115, 307), (461, 294), (282, 64), (200, 220), (380, 220)], [(320, 560)]),
}
# In the 1536x1024 concepts: the painted boss (points) and the small painted characters (centres).
CONCEPT_BOSS = {
    "lupar": [(1100, 520), (1250, 380), (1400, 450), (1450, 600), (1200, 300)],
    "larut": [(1180, 230), (1000, 250), (1380, 250), (1180, 450), (1330, 520), (1100, 520)],
    "kancil": [(1200, 250), (1200, 400), (1050, 420), (1350, 400), (1150, 170)],
    "ledang": [(1200, 250), (1200, 400), (1040, 420), (1400, 380), (1200, 170)],
}
CONCEPT_PEOPLE = {
    "lupar": [(157, 486), (306, 580), (400, 666)],
    "larut": [(212, 494), (340, 560), (580, 611), (345, 500)],
    "kancil": [(204, 545), (376, 600), (517, 686)],
    "ledang": [(204, 490), (376, 616), (274, 679), (330, 560)],
}
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
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "WEBP", quality=quality, method=6)
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


def naga() -> None:
    for pose in ("idle", "attack", "special", "hurt", "defeat"):
        src = B04 / "NAGA_CHINI" / f"naga_chini_{pose}.png"
        out = save_webp(tidy_alpha(Image.open(src), keep=0.01), OUT / "bosses" / "chini" / f"{pose}.webp")
        note(out, rel(src), "production pose still (Batch 04/06), stray edges removed", f"boss pose: {pose}",
             anchor="bottom-center")
    src = next((B03 / "03_BOSS_NAGA_CHINI").glob("01_naga_chini_battle_pose_transparent_*.png"))
    im = tidy_alpha(Image.open(src))
    im.thumbnail((640, 800), Image.LANCZOS)
    out = save_webp(im, OUT / "bosses" / "chini" / "reveal.webp")
    note(out, rel(src), "production full-body pose (Batch 03)", "boss reveal")


# ------------------------------------------------------------------ worlds


def world_chini() -> None:
    src = B03 / "01_BATTLE_BACKGROUND/02_tasik_chini_battle_background_FHD_1920x1080.png"
    im = Image.open(src).convert("RGB").resize((1600, 900), Image.LANCZOS)
    out = save_webp(im, OUT / "worlds" / "chini" / "battle.webp", 82)
    note(out, rel(src), "production clean battle background (Batch 03)", "battle and travel backdrop")


def soft_fill(arr: np.ndarray, mask: np.ndarray, sigma: float) -> np.ndarray:
    """Normalised convolution: fills the masked area with the blurred colours around it, widening the
    blur wherever the first pass finds nothing to borrow."""
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


def worlds_derived() -> None:
    session = sam_session()
    if session is None:
        print("rembg is not installed: keeping the derived boss cut-outs and backgrounds already in static/story/")
    for key, (pack, stem) in WORLD_PACKS.items():
        base = SRC / pack
        closeup_src = base / f"01_REFERENCE_ART/{stem}_boss_closeup_REFERENCE_NOT_SPRITE.png"
        concept_src = base / f"01_REFERENCE_ART/{stem}_source_concept_1536x1024.png"
        boss_out = OUT / "bosses" / key / "idle.webp"
        bg_out = OUT / "worlds" / key / "battle.webp"
        if session is not None:
            closeup = Image.open(closeup_src).convert("RGB")
            pos, neg = CLOSEUP_POINTS[key]
            solid = cutout(session, closeup, pos, neg)
            labels, count = ndimage.label(solid)
            sizes = ndimage.sum(solid, labels, range(1, count + 1))
            keep = np.isin(labels, [i + 1 for i, s in enumerate(sizes) if s > sizes.max() * 0.04])
            keep = ndimage.binary_erosion(ndimage.binary_fill_holes(keep), iterations=1)
            alpha = Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
            boss = closeup.convert("RGBA")
            boss.putalpha(alpha)
            save_webp(boss.crop(boss.getbbox()), boss_out, 88)

            concept = Image.open(concept_src).convert("RGB")
            arr = np.array(concept).astype(np.float32)
            painted_boss = ndimage.binary_dilation(cutout(session, concept, CONCEPT_BOSS[key]), iterations=18)
            people = np.zeros(painted_boss.shape, np.uint8)
            for x, y in CONCEPT_PEOPLE[key]:
                people[max(0, y - 85): y + 55, max(0, x - 62): x + 62] = 255
            people[0:200, 1000:1536] = 255  # the painted title, boss bar and minimap
            blend = cv2.GaussianBlur(people, (0, 0), 8)[:, :, None] / 255.0
            arr = arr * (1 - blend) + soft_fill(arr, people, 14) * blend
            big = (painted_boss * 255).astype(np.uint8)
            blend = cv2.GaussianBlur(big, (0, 0), 25)[:, :, None] / 255.0
            arr = arr * (1 - blend) + soft_fill(arr, big, 60) * blend
            bg = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).crop((0, 112, 1362, 878))
            bg = bg.filter(ImageFilter.GaussianBlur(1.3)).resize((1600, 900), Image.LANCZOS)
            save_webp(bg, bg_out, 80)

        if boss_out.exists():
            note(boss_out, rel(closeup_src), "DERIVED interim cut-out (SAM segmentation of a reference close-up); "
                 "needs a clean multi-pose sprite before public release", "boss sprite, all states animated in code",
                 anchor="bottom-center")
        if bg_out.exists():
            note(bg_out, rel(concept_src), "DERIVED interim backdrop (painted HUD, characters and boss filled, "
                 "softened); needs an authored clean background", "battle and travel backdrop")
        reveal = OUT / "worlds" / key / "reveal.webp"
        im = Image.open(closeup_src).convert("RGB")
        save_webp(im, reveal, 82)
        note(reveal, rel(closeup_src), "reference close-up used only as a cinematic still", "boss reveal cutscene")


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
        src = B02 / f"element_attack_spritesheets/fx_{el}_12frames_4x3.png"
        out = save_webp(Image.open(src).convert("RGBA"), OUT / "fx" / f"{el}_sheet.webp", 88)
        note(out, rel(src), "production 12-frame sprite sheet (Batch 02)", "impact animation on the target",
             frames=12, frame=[256, 256])


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
    heroes()
    naga()
    world_chini()
    worlds_derived()
    ui()
    fx()
    sound()
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
