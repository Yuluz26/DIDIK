# Instructions for Codex / Claude Code — DIDIK Batch 05

Extract the ZIP and read `README_FIRST.md`, `04_DOCS/asset_manifest.json` and the existing DIDIK JRPG specifications before implementation.

1. Use the five PNG files from `01_ELEMENTAL_FX_TRANSPARENT/` as **single-frame, transparent VFX artwork**. Preserve alpha. For example, in a PixiJS/Phaser/Svelte Web Animations layer, tween opacity, position, rotation and scale, plus add custom particles and sound as needed.
2. Trigger **one** elemental cinematic attack on server-confirmed correct quiz answers, NOT as an independent manual free hit.
3. Wrong answer => boss/enemy counterattack and −1.5 hearts. The two preview images are only art direction; animate actual boss and hero layers for the real scene.
4. Keep hero HP within 0...6 with 0.5 precision. Boss has 5 bars. Prevent double submissions and state desynchronisation in multiplayer.
5. Render image overlays above a separate battle background, with the hero on left and Naga Chini on right; do not rasterize UI text into a background.
6. Avoid client-side answer validation. Gameplay sequence should be auto progression -> battle scene -> quiz -> correct/wrong animation -> next encounter -> boss -> next world.
7. Do NOT reintroduce any 3D games, joystick, WASD movement or dodge into Story Mode. Remove Litar Kart, Sepakan Penalti, Peti Lanun, Menara 118 while preserving the eight other 2D games.
8. If assets need extra frames, generate or create them separately and mark them in the manifest. Never label a static PNG as an animation or video.
9. Run frontend build/typecheck and backend gameplay tests. Capture real browser screenshots for review, not concept-art mockups.
10. Keep feature development in branch/PR; do not merge or deploy without permission.

**Visual quality target:** polished, HD JRPG with Malay folklore themes; preserve images at their native resolution and scale them appropriately in-game.
