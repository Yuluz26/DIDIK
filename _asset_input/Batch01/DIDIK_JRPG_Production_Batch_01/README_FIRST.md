# DIDIK — JRPG Story Mode: Codex/Claude Code + Visual Batch 01

## Download & use

1. Extract this ZIP and the latest DIDIK repo in your coding environment.
2. **Codex Cloud:** attach this ZIP and paste the entire contents of `01_PROMPTS/CODEX_CLOUD_START_HERE.md`; include `01_PROMPTS/SHARED_MASTER_SPEC.md` in context.
3. **Claude Code:** place files in workspace, then paste `01_PROMPTS/CLAUDE_CODE_START_HERE.md`; direct Claude to read shared spec and asset manifest before editing.
4. Use `05_ORIGINAL_MASTER_LIST/` for the full per-world assets; `02_ASSET_SPEC/ASSET_MANIFEST.csv` declares availability and what still needs production.

## What has actually been delivered

- **Two execution prompts** + authoritative master implementation spec: yes.
- **First batch of new generated imagery:** five moodboards/art direction sheets: yes.
- **Previously approved visual key art for the five worlds:** included for convenience/reference: yes.
- **Six small character look-reference crops:** extracted from a board, explicitly NON-production: yes.
- **Clean isolated alpha PNG character sprites, bosses, UI components, animation sprite sheets:** **NOT yet delivered**. Do not mistake image mockups for game-ready assets. These require separate purposeful art production.
- **Video files:** NONE. Promo/story frames in references are still images, not exported video clips.
- **Code / deployment / PR modifications in this package:** NONE. The prompts instruct Codex/Claude Code what to implement; we have not executed them here.

## Important changes in gameplay

**No player free movement.** Auto story travel, then distinct **JRPG turn-based** question battle scenes. Correct answer (+0.5 HP; boss -1 HP), wrong answer (-1.5 HP; unavoidable enemy attack); 6 player hearts, 5 boss bars, 5 elemental weapons after 5 normal encounters, 5 worlds, solo or party. Remove four old 3D games Litar Kart, Sepakan Penalti, Peti Lanun, Menara 118, keep eight existing 2D games.

## Copyright / art notes

The reference art should be used only to establish visual direction and to communicate to art production. Draw/rebuild usable UI and sprite layers rather than attempting to extract a complete animated game from a flattened scene. Check external assets' usage rights before release.
