# DIDIK JRPG — BATCH 02 (TASIK CHINI VERTICAL SLICE + CONSISTENCY KIT)

## What's inside

This ZIP contains **real extracted per-world / per-boss / per-hero / FX reference crops** from new AI design boards; **original game-usable UI SVGs and transparent PNG exports**; and implementation prompts for Codex and Claude Code.

- `01_VISUAL_CONCEPT_BOARDS/` — 2 full new art-direction boards.
- `02_WORLD_ART_REFERENCES/` — 5 separate world concept crops.
- `03_BOSS_ART_REFERENCES/` — 5 boss concept crops.
- `04_HERO_ART_REFERENCES/` — 6 hero portrait concept crops.
- `05_ELEMENT_FX_REFERENCES/` — 5 separate element-effect reference crops (the references use a *Bayangan* variant, which is NOT one of DIDIK's authorised 5 game elements; the true set is Api/Angin/Petir/Tanah/Air).
- `06_GAME_READY_UI/` — **original** independent SVG and PNG transparent icons (5 elements, full/half/empty hearts) and scalable blank panel / answer button / boss-HP bar designs.
- `08_CODEX_CLAUDE_PROMPTS/` — implementation instructions.
- `09_PREVIEWS/` — contact sheet.
- `ASSET_MANIFEST.json` — status, dimensions and purpose per file.

### Very important: provenance and limitations

`REFERENCE_CROP` means a crop from a mixed AI concept sheet, with embedded background and potentially artefacts. It's neither source-separated animation nor a production-ready sprite. **Do not load these as live characters, boss models, battle maps or collision geometry.** Crops are deliberately kept at native pixel dimensions; increasing dimensions would not increase detail.

The `GAME_READY_VECTOR` and `GAME_READY_RASTER` entries refer **only to the UI icon/frame assets authored independently for this package**. Text in UI/gameplay should be live, accessible HTML/Svelte, not baked into PNG.

No actual video file, hero animation sprite sheet, transparent boss pose sequence, or final full-res clean battle background has been produced in this batch. These remain production tasks for the game asset pipeline.

### Required game design invariants

- JRPG turn-based *battle screen* with auto-story transitions; no joystick, WASD, manual movement or dodge in Story Mode.
- Parents only create quiz (at least 10 questions) and select Story Mode.
- 5 fixed world/boss pairs, 5 minor encounters + boss with 5 successful hits each world.
- Player: 6 hearts, right answer +0.5 capped, wrong −1.5 unavoidable; boss 5 bars and −1 only on correct.
- Elements: **Api / Angin / Petir / Tanah / Air**, never replace Tanah by Bayangan.
- Remove four old 3D games entirely (`litar`, `penalti`, `lanun`, `menara`), preserve eight old 2D modes.
- All grading/HP/boss state server-authoritative; party shares boss HP with personal player HP.
- Preserve unrelated DIDIK source/UI, do not merge/deploy without approval.

### Original icon design

Icons are independent 256-unit transparent SVG, PNG exports 512x512; elements and hearts are safe to use in frontend with ordinary asset copying and references. Rendering dimensions in app: recommended 52–72 CSS pixels icons (44+ mobile tappable); heart 18–28 CSS pixels.

### Suggested next production batch

**Batch 03:** clean world-1 battle background with empty safe zones; Hang Tuah and Mahsuri consistent battle sprite rigs (idle/attack/hurt/victory); Naga Chini separate alpha-cut boss rig (idle/attack/hit/defeat), attack frame variants. The AI concept boards alone do not meet these criteria.

### Newly added original elemental combat FX

`06_GAME_READY_UI/element_attack_spritesheets/` contains 5 separate 12-frame RGBA attack-effect atlases and 5 animated GIF previews. Each atlas is 4×3 frames at 256×256 pixels per frame. Time about 85 ms per frame, trigger **only after the server validates a correct answer**; wrong answers play boss counterattack instead. This atlas is code-generated original 2D VFX, not an animated hero or boss character.
