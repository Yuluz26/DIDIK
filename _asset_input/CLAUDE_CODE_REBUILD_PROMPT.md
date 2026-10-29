I want you to directly rebuild DIDIK Story Mode into a premium, fully playable, cinematic JRPG educational game using the assets I have supplied.

## STEP 1 — READ ALL PROJECT CONTEXT

You are working inside my existing DIDIK GitHub repository.

Before making changes:

1. Inspect the entire relevant codebase, especially `live/server` and `live/web`.
2. Read the existing Story Mode implementation and understand how the FastAPI WebSocket server communicates with the SvelteKit frontend.
3. Read these instructions completely:

`_asset_input/Batch01/DIDIK_JRPG_Production_Batch_01/01_PROMPTS/CLAUDE_CODE_START_HERE.md`

`_asset_input/Batch01/DIDIK_JRPG_Production_Batch_01/01_PROMPTS/SHARED_MASTER_SPEC.md`

4. Inspect the extracted Batch 01–12 folders, their asset manifests, images, sprite sheets, UI components, MP4 files and integration guides.
5. Identify which assets are production-ready, which are static pose references, and which are concept art only.

## STEP 2 — REMOVE ALL 3D GAMES

Completely retire these four 3D modes:

- Litar Kart
- Sepakan Penalti
- Peti Lanun
- Menara 118

Remove obsolete registrations, integrations, unused dependencies and outdated marketing references.

Preserve the existing eight 2D game modes.

## STEP 3 — IMPLEMENT THE NEW JRPG GAMEPLAY

The old manual Zelda-like movement approach is no longer the desired gameplay.

The new flow must be:

Automatic Story Exploration → Enemy Encounter → JRPG Battle Scene → Question → Cinematic Attack/Counterattack → Victory → Automatic Progression.

There must be no mandatory joystick, WASD movement or manual dodging in Story Mode.

Parents should only create their quiz questions and select Story Mode.

Implement five Malaysian folklore worlds:

1. Tasik Chini — Naga Chini.
2. Batang Lupar — Bujang Senang.
3. Hutan Larut — Gajah Rimba.
4. Rimba Bayangan — Sang Kancil Bayangan.
5. Gunung Ledang — Penunggu Kabus.

## STEP 4 — COMBAT REQUIREMENTS

- Support Solo and Party.
- Minimum ten parent-created questions.
- Five quiz encounters before the boss in each world.
- Six hearts per player.
- Correct answer: restore 0.5 heart, capped at six.
- Wrong answer: unavoidable enemy attack, dealing 1.5 hearts.
- Five selectable elemental weapons: Fire, Wind, Lightning, Earth, Water.
- Unlock elemental weapons after clearing five obstacle encounters.
- Bosses have five HP bars.
- Correct boss answers produce a cinematic attack and remove one boss HP bar.
- Wrong boss answers trigger a cinematic counterattack.
- Fair question recycling if only ten questions are provided.
- All question validation, HP and boss progression must remain server-authoritative.

## STEP 5 — ART AND ASSET INTEGRATION

Use the HD assets in `_asset_input/Batch01` through `Batch12`.

Do not recreate everything with primitive CSS rectangles or poorly proportioned procedural Canvas drawings.

Prioritise the existing HD artwork, independent battle backgrounds, transparent hero/boss poses, UI overlays and elemental FX.

Create real animation timelines using the appropriate pose and effect assets.

Do not use an MP4 animatic or static concept screenshot as a substitute for functional gameplay.

Optimise asset loading, avoid unnecessarily large bundled images and preserve visual quality.

Keep the art direction consistent with the supplied references.

## STEP 6 — DEVELOPMENT APPROACH

Work in milestones:

A. Audit and cleanup.
B. Complete the Tasik Chini JRPG vertical slice.
C. Implement all five worlds.
D. Integrate solo/party gameplay.
E. Polish animations, transitions, UI and responsiveness.
F. Run backend tests, Svelte typecheck/build and real browser gameplay tests.

Use specialised subagents for backend, frontend, asset integration and QA when helpful.

Keep unrelated functionality unchanged.

## STEP 7 — DELIVERY

After each milestone, provide:

- Actual files changed.
- Working gameplay implementation.
- Tests executed and their results.
- Screenshots captured from the running game.
- Known limitations.

Maintain a development branch and commit finished milestones.

Push to the feature branch and prepare a Draft Pull Request when appropriate. Do not merge or deploy without approval.

Start by inspecting the repository and assets, then proceed with implementation. Do not stop after writing a plan.
