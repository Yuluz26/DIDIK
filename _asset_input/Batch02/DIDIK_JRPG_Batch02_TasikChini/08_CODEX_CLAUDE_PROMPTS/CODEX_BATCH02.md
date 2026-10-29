# CODEX CLOUD — DIDIK BATCH 02 INTEGRATION

You are working in `Yuluz26/DIDIK`, on the current safe Story Mode feature branch (verify its head, and make a new branch if needed). Read this Batch 02 `README_FIRST.md`, the `ASSET_MANIFEST.json`, and the existing **Batch 01** master specification. This batch supplements, but does not override, the factual game-mechanics specification.

## Objective
Make Tasik Chini's actual JRPG battle UI noticeably more polished while preserving question logic and backend authority. **Auto-exploration + 2D JRPG encounter screen**; remove movement and joystick from this Story Mode only. Do not create a pseudo-game by displaying the full AI screenshot as the background.

## Required work
1. Verify current architecture: FastAPI Python quiz mode and SvelteKit `live/web` story scenes. Read existing tests.
2. Remove all four deprecated 3D games `litar/penalti/lanun/menara` in registry, frontend routes, 3D-only dependencies, homepage and tests; preserve eight original 2D games.
3. Copy only `GAME_READY_*` SVG/PNG from `06_GAME_READY_UI` into the app's story asset directory. Prefer SVG render for sharp responsive UI; add proper descriptive alt labels for icons and never present an asset as answer text.
4. Use five gold-ringed 2D elemental icons and correct six-heart half-heart UI. Render boss HP as five independently animated bars with game-state-driven updates.
5. Use the cropped image sheets and original full images as **style references** to reproduce clean world and boss production assets. The panel crops are not transparent sprites or playable maps; don't treat them as such.
6. Create actual Tasik Chini dedicated battle scene: hero left, Naga Chini on right, 5-stage minor encounters, high-quality readable BM question panel, answer result cinematics, elemental effects, and victory/defeat states.
7. Implement the precise rule: right +0.5 player heart and 1 boss hit, wrong −1.5 player hearts and 0 boss hit. All combat events server validated. A wrong answer cannot make the boss impossible to finish.
8. Add asset registry to code (type, path, logical size, alpha, fallback, load policy). Ensure preview and test use actual components. Don't place concept crops in production sprite paths.
9. Test min 10 questions, keyboard/touch answer, solo/party race conditions, 5-bar boss, 6 hearts and state replay/reconnect; run Python and Svelte checks and screenshot actual gameplay.
10. Make safe commits and Draft PR, no merge/deploy. Clearly list missing art production items and don't claim unproduced MP4, boss sprites or clean battle bg exist.

## Visual acceptance
Premium modern 2D JRPG + Malay folklore, consistent chibi proportions, proper environmental depth, no primitive geometric bosses, no big static game screenshot posing as gameplay. Reference art supplies the aspiration; the app supplies the interactable mechanics.

Implement now; don't stop at a design plan.

## Game-ready new animated VFX atlas
Load `06_GAME_READY_UI/element_attack_spritesheets/fx_{api,angin,petir,tanah,air}_12frames_4x3.png`. 12 frames in a 4×3 atlas; each cell 256×256; play once at 85ms/frame on authorised correct-answer `story-hit` event with the chosen element. Do not animate damage before backend outcome. Use GIFs only as visual previews.
