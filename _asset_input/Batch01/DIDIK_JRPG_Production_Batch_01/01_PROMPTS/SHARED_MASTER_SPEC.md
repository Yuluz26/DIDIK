# DIDIK — JRPG STORY MODE REBUILD: MASTER IMPLEMENTATION BRIEF

> **AUTHORITATIVE SPECIFICATION** for Codex Cloud and Claude Code. Read this together with `05_ORIGINAL_MASTER_LIST/` and `02_ASSET_SPEC/ASSET_MANIFEST.csv`. The attached images are **visual references**, not verified game-ready sprites, videos, clean backgrounds, or art licences.

## 0. Mission / non-negotiables

Build an actual browser-playable **JRPG-style turn-based educational adventure** within the EXISTING DIDIK repository, not a promotional mockup. The protagonist and companion characters progress through a cinematic story automatically. **No WASD, arrow-key locomotion, touch joystick, platforming, dodge, or free-roaming action RPG controls are required in this Story Mode.** Students interact by reading the narrative, choosing a character/element, answering quiz questions, and tapping Continue. Combat actions play cinematic animations automatically based on server-validated answers.

The visual target is a premium original 2D Malay-folklore JRPG aesthetic: rich Malaysian tropics and architecture, expressive chibi game sprites, impressive legendary bosses, ornate yet readable HUD, animated world transitions, and polished attack/counterattack feedback. The earlier basic pixel-canvas scrolling corridor is NOT the visual acceptance target. The FIVE previously supplied high-detail reference images are artistic mood targets; do not use a flattened generated gameplay screenshot as a static game background and claim it is playable.

**DELETE/RETIRE ALL FOUR OLD 3D GAME MODES**: `litar` (Litar Kart), `penalti` (Sepakan Penalti), `lanun` (Peti Lanun) and `menara` (Menara 118). This includes actual registry, routes/handlers, imports, player/host integrations, selection UI, marketing, obsolete tests and unused packages after dependency checks, not only CSS hiding. Preserve all eight existing 2D games and all unrelated DIDIK functionality. Check actual repository names first and handle deprecated saved sessions gracefully. NO 3D game engine in the new mode; remove Three.js if actually unused elsewhere.

**Parents/teachers only create a quiz and choose Story Mode.** They must never author maps, configure bosses, HP values or manually assign fifty questions. Keep all eight supported quiz question formats when compatible, or document mode-specific constraints clearly.

## 1. Repository / current branch / code audit

Repository: `Yuluz26/DIDIK`.
Existing Draft PR: `https://github.com/Yuluz26/DIDIK/pull/1`, feature branch: `feat/legenda-story-mode` (verify head SHA and active branch live; do not blindly assume default branch is `main`). Existing live architecture appears to use FastAPI + WebSockets for room/game authority and SvelteKit for UI; Laravel exists in the same repository. Read code, not memories: `live/server/didik_live/game/modes/story.py`, mode registry, `live/server/didik_live/game/room.py`, `live/server/didik_live/questions.py`, `live/web/src/lib/games/story/`, parent quiz/editor flow, shared UI and tests. Preserve existing auth/quiz DB contracts and room links/QR joins.

1. Inventory dependencies, actual routes, mode list and DB. Read all files in attached asset pack, including original world-level lists.
2. Create an actionable gap ledger `docs/jrpg-asset-gap.md`: `asset_id, filename, required_state, source, production_status, usage, licensing, needed_before_merge`.
3. Start from a safe feature branch based on the current story development branch, or continue it if working-tree state is clean. Do not force-push, delete user work, deploy or merge without approval.
4. Report pre-existing CI errors separately from regressions caused by your changes. The legacy Laravel workflow was previously observed failing due to PHP 8.0 vs project PHP >=8.3; verify rather than guessing.
5. Reuse tested WebSocket/server quiz components instead of recreating a parallel account or quiz database.

## 2. Exact UX / game state machine

`select_character → world_intro → auto_travel → encounter_intro → normal_battle → answer_feedback → encounter_clear → auto_travel (repeat five times) → unlock_elements → boss_reveal → boss_battle → world_clear → next_world_intro ... → campaign_victory`.

Every transition must be implemented as a real, testable state; animations can be skipped (or reduced) without skipping server state. The 4–5 sites originally discussed are now **five fixed worlds**.

**Five worlds and their bosses, in this exact order:**
1. Tasik Chini — **Naga Chini**, jade-blue mythical lake dragon, lotus-covered lake, timber bridges, lakeside homes, mossy carved ruins, turquoise falls.
2. Batang Lupar — **Bujang Senang**, giant MYTHICAL CROCODILE (not a human), Sarawak-inspired river, stilt villages, jetties, mangrove roots, sunset.
3. Hutan Larut — **Gajah Rimba**, colossal elephant guardian, deep Malaysian rainforest, tangled trees, ferns, relic shrines, shafts of light.
4. Rimba Bayangan — **Sang Kancil Bayangan**, sinister HUMANOID MOUSE-DEER/KANCIL-inspired illusionist (not a generic deer/elk), moonlit purple enchanted forest, spirit lights.
5. Gunung Ledang — **Penunggu Kabus**, epic mountain guardian manifested by sacred mist (not automatically a goddess/princess), mountain bridges, cascading falls and misty sanctuary.

All fantasy designs should respectfully take inspiration from regional folklore; do not pretend that invented variants are historically accurate. Malay UI copy should sound natural (Malaysian Bahasa Melayu).

### Exact learning-driven encounter and HP logic

Parent creates quiz, minimum **10 questions**. A single ten-question set supports the entire Story Mode (intelligent rotation across later worlds, reshuffle choices when possible, anti-repeat priority, no need for fifty questions). Per world: **5 minor question encounters** and **5 successful boss hits**. Starting player HP = **6 hearts** with half-heart precision (backend can store 12 half-hearts). On ANY correct answer, heal +0.5 HP, capped at 6. On ANY incorrect answer, enemy/boss deals an UNAVOIDABLE **−1.5 HP**. A successful boss question grants one cinematic player free-hit and subtracts **exactly 1 of the 5 boss bars**. Wrong boss answers NEVER reduce boss HP; rotate/retry questions until five successful hits or player defeat. For regular encounters, clearly decide whether wrong answers require a retry before an obstacle counts as cleared; document and test it. Never allow a wrong answer to silently count as knowledge success or trap the player in unwinnable state. On HP=0: defeat cutscene + restart at fair current-world checkpoint, preserving other players' progress as intended.

### Five elemental weapons

After five normal encounters in a world, reveal and unlock **Api, Angin, Petir, Tanah, Air**. Player can select and switch element before answering each boss question. Element alters visual attack choreography, particles, optional world-appropriate bonus score/weakness; do NOT secretly inflict >1 boss HP or override question correctness. Visual attack must display only after positive server validation. Wrong answer triggers enemy's cinematic unavoidable counterattack.

### Party and solo

Solo: one child, automatic story travel and encounters, with full progression, retry and victory.
Party: join DIDIK's existing room with link/QR/code; children answer questions individually (do not reveal answer keys), retain individually tracked hearts/hero/element, cooperative **shared boss HP** and synchronization/acknowledgement of every correct hit; protect against duplicate messages and multiple-hit races, disconnect/rejoin, cross-world and stale player events. Do not let a faster player finish everything before other students have a meaningful chance; propose and implement a simple phase barrier, cooperative ready state or fair participation design. State remains authoritative on server with clear event IDs/state versioning.

## 3. Battle presentation: cinematic JRPG, NOT free-action

Story view / auto travel is a visual transition showing heroes journeying automatically; it is **not** a manual tilemap playground. Encounters switch to a distinct 2D JRPG battle scene with heroes on one side, legendary enemy on the other, perspective/scale consistent with references, idle loop, dramatic clash on answer, victory return to story. Include:
- Hero selection with male and female Malay-inspired avatars (Hang Tuah, Hang Jebat, Mahsuri, Tun Teja, Puteri Saadong, Bendahara; optional Laksamana separate character only if distinct), costume silhouettes, no identity misrepresentation.
- Hero idle, select/action anticipation, attack 5 elements, struck, defeat, victory; animations rather than single still image translating across screen.
- Five bosses: arrival/reveal, idle/breathing, telegraph, one or two attack signatures, stagger/hit, phase shift at lower HP, defeat. Effects can use code-driven particles layered around the image, but don't just distort a full screenshot.
- A question panel integrated into scene with clear BM choices; answer lock feedback, accessible text, visual slash/counterattack, number popups, heart loss/gain and boss-bar transitions.
- Cinematic intro/transition/victory screens; reduced-motion fallback / skip controls; touch-first portrait and landscape layout.
- Quiz state never misrepresents scoring or instantaneous boss HP.

## 4. Asset pipeline / production-quality standards

Read `02_ASSET_SPEC/ASSET_MANIFEST.csv`. The `03_VISUAL_REFERENCE/` material is **concept art and board graphics**, not cut-up sprites. Generated moodboards may contain inaccurate text, unrelated weapon names and design contradictions. This document, NOT texts embedded in the images, defines mechanics and names. In particular, a concept image showing Bujang Senang as a human is an artist error: the intended boss is a crocodile.

Establish `live/web/static/assets/story/` (or existing repo's approved equivalent) structured by `heroes/`, `bosses/`, `worlds/`, `ui/`, `fx/`, `cutscenes/`, `audio/`. Maintain a machine-readable asset manifest with author, licence, source, size, alpha/transparency, animation frame rects, anchor points and use case. Images with text/HUD baked in must remain moodboards, not actual game assets.

**Required asset sets:**
- 5 isolated/looping **battle backgrounds** (hero left, boss right, keep central readability and HUD-safe areas); optional normal-encounter and boss-variant per world.
- 5 visually distinctive **boss sprite rigs** with transparent alpha, at least idle/attack/hurt/defeat states; sprite sheets, parts/puppet rig, or other programmable 2D animation source. No flattening hero and boss into the background.
- At least 2 strong starter heroes: Hang Tuah (male) and Mahsuri (female), full character select portrait + consistent battle sprites/state animations; gradually expand to other named roster.
- 5 elemental **separate icon assets** + hit/charge effects, 6 full/half/empty heart states, five-segment boss bar, combat UI panels, story panels, reward/victory/defeat layouts.
- Per-world opening cinematic still frames/animatable layers, boss reveals and transitions; optional sound bed and SFX must be actually sourced/generated and properly licensed. Trailer source storyboard is **not** a video. Only claim video delivery if exported and verified actual mp4/webm.

Suggested naming: `world_01_chini/battle_bg_v01.webp`, `boss_chini/{idle,windup,attack,hurt,defeat}_XX.png`, `hero_tuah/idle_{direction}_XX.png`, `ui/element_api.png`. Align all anchor points, camera stage orientation, colour grade, subject scale, pixel density and output resolution. Prefer high-quality illustrated 2D / HD pixel art over poorly aligned low-resolution crops.

When truly usable visual assets are unavailable, **do not pass off reference images as sprite sheets**. Build a transparent placeholder asset adapter and document the specific unresolved production dependencies. Do not attempt to auto-remove baked-in text by blindly cropping and claim completion. You may improve/replace authored assets using properly licensed sources or local generated work subject to actual tool availability; avoid uploading copyrighted proprietary Zelda or Final Fantasy materials.

## 5. Technical implementation instructions

- Integrate with the existing SvelteKit client and Python FastAPI DIDIK Live real-time room server; use existing Laravel components only where actually wired, not a parallel reimplementation.
- Introduce a focused finite state machine with durable server-side progression, question selection, answer grade, half-heart HP, co-op boss HP, retries and real-time messages. Define typed event payloads, versioning and reconnect snapshots. Render everything as reactive pure game state.
- Remove existing Story Mode manual `move` / `engage` controls and server positional ticker if no longer needed by Story Mode; ensure other 2D games still receive their movements. Replace the old top-down scrollable visual-only canvas with real JRPG stage scene components.
- Choose a performant 2D renderer (existing canvas, PixiJS or Phaser if justified) for animations; 2D only, and do not force add a framework where Svelte + sprite sequences and CSS/Canvas can achieve it.
- Asset preloading by world, memoised textures and lazy chapter loads, 60fps target where practical and adaptive effects on mobile; avoid re-decoding each frame. Responsive 16:9 design with narrow-mobile fallbacks and safe area handling. Make focus/controls keyboard accessible for questions even though walking is automatic.
- Prefer no new database table if existing persistence supports it; otherwise migration with rollback. Preserve backwards compatibility, server trust boundaries, anti-replay protection and room expiry.

## 6. Work plan with tangible checkpoints — do NOT stop at planning

**Milestone A — audit + legacy 3D cleanup:** inspect repo, update registry/routes/imports/content, test 8 2D games still work, document removals.
**Milestone B — world 1 production vertical slice:** rebuild Tasik Chini as auto-story + genuine dedicated battle screen. Implement hero choice (Hang Tuah + Mahsuri), normal encounters ×5, quiz question overlay, all 5 elemental attacks, 5 HP Naga Chini cinematic boss battle, lose/retry and world clear. Its quality must be visually approved before scaling.
**Milestone C — expand worlds 2–5:** unique bosses, matching backgrounds, transitions, stage lighting, boss choreography and final ending; do not palette-swap World 1 and call it done.
**Milestone D — solo/co-op reliability:** shared boss HP, individualized quiz/HP, fair group pacing and reconnection.
**Milestone E — production polish:** phone UX, sound, reduced-motion, consistent sprites, 16:9 responsive UI, transitions, video promo if media tools are available.
**Milestone F — verification:** run Python tests, Svelte check/build, browser end-to-end interactive tests including correct/wrong/HP, party race tests and screenshot/video captures from actual game. Fix failures before final summary; always separate old Laravel failures from new regressions.

If Cloud Codex session runs out of time/context, make commits/checkpoints and leave concise `docs/JRPG_NEXT_STEPS.md` with exact remaining steps and tests, not a vague claim of done. Use subagents **only when the environment supports them** and scopes are non-overlapping (backend state, frontend scene, QA/asset audit); do not claim agents ran unless they did.

## 7. Minimum acceptance criteria

- Exactly **0 active 3D games**; the eight existing 2D game modes remain healthy.
- Parent can create just **10 questions**, choose Legenda Story Mode and launch; no game configuration knowledge required.
- No WASD/joystick/dodge/free-movement UX anywhere within Story Mode. Auto-travel visibly triggers **separate JRPG battle scenes**.
- Five stages and five distinct boss designs, with five question obstacles + five *successful* boss hits each world; questions reused sensibly.
- Correct +0.5 player heart (max 6) and one free boss hit; wrong −1.5 player heart and zero boss HP loss; boss has **five** segmented bars, authoritative server-side state.
- Selectable Api/Angin/Petir/Tanah/Air with actually different animations/effects; two usable hero genders and safe expansion path to full roster.
- Solo and co-op share same grade system, deterministic co-op boss state, fairness and reconnect.
- Real playable UI, not screenshot pasted behind transparent click targets, no baked-in fake HUD, full accessibility for answering and reduced-motion support.
- Types/checks and backend/browser tests pass; final mobile and desktop screenshots **taken from running code**, with PR and commits identified. Video files, if claimed, exist and can be played.

## 8. Required final handoff

Report exact branch/PR, files changed, removed 3D dependencies and modes, inventory of production-ready vs reference-only asset IDs, world/gameplay completion checklist, automated tests and actual results, interactive screenshots, preview commands, known gaps, and what still needs an art specialist. Keep Draft PR for review; **no automatic merge or deployment**.

**Start by inspecting repository + all ZIP contents; then implement real code. The screenshots attached here are for visual direction, not evidence that game assets already exist.**
