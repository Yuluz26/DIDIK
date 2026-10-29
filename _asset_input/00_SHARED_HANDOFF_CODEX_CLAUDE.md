# CODEX / CLAUDE CODE HANDOFF — DIDIK JRPG STORY MODE

## Mandatory design
- Parents create a quiz (min 10 questions), then choose Legenda Story Mode; no world editor or special boss setup.
- Exploration is automatic cinematic travel; encounters cause a scene change to a dedicated turn-based JRPG battle.
- No joystick, WASD or live action-dodge mechanics.
- In each of five worlds, five obstacle questions and a boss with 5 HP bars. Rotate questions on failed boss answers to avoid unwinnable encounters.
- Six hearts per student; incorrect -1.5 HP, correct +0.5 HP up to 6. In coop, players have independent hearts; shared boss HP is authoritative.
- All five unlocked elemental weapons are API keys `api`,`angin`,`petir`,`tanah`,`air`, NOT a sixth 'shadow' element.
- Boss battle animation on quiz result: `correct -> heal 0.5, hero attack, boss -1`; `wrong -> boss counterattack, hero -1.5`.
- Story progress until fifth boss; victory. Handle failure and retry at current-world checkpoint.
- Remove the four old 3D games (`litar`,`penalti`,`lanun`,`menara`) safely. Preserve the eight existing 2D modes.
- Build and test on a feature branch; do not deploy/merge by default.

## Asset use
- Read `asset_manifest.json` from each pack. Do not treat a 1536x1024 concept screenshot as a separated 2D scene, 3D model, interactive environment, or sprite sheet.
- Boss/story scenes from packs 08-11 contain artwork, UI and/or characters baked together. Reconstruct a layered scene with new independent art before implementing a real battle renderer.
- `03_REUSABLE_UI` elements are real PNG alpha layers, but text and HP numbers must be rendered dynamically.
- MP4 files are recorded cinematics built using still-image pan/scale/compositing, not proof of finished player/boss animation.
- Batch 06's Naga Chini poses are manually extracted and may have imperfect cropping. Correct anchor/alpha and make real transitions before shipping.
- Synthesized WAV in Batch 12 is intended for a temporary interface sound demonstration; commission/create better sound design before a public release.
- Use user-supplied reference images as inspiration only; match composition and brand art direction, not proprietary characters/assets of other games.

## What remains
- World 2–5 separate clean boss transparent sprites, independently authored clean battle backgrounds, per-state animation frames, close-up cutscene portraits, real soundtracks and high-quality sound effects.
- Actual runtime integration, multiplayer playtesting, mobile responsive battle scenes and art QA.
- These ZIP files provide useful HD concept refs, video animatics, reusable UI, boss poses, transition frames and developer specs; they are **not complete games**.
