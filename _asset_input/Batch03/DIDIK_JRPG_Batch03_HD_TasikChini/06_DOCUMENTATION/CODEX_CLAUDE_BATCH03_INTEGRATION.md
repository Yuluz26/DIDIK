# DIDIK JRPG Batch 03 — Codex / Claude Code integration task

Work on a safe branch of `Yuluz26/DIDIK`, based on the existing Legenda feature branch if relevant, and first inspect the current project. **Do not merge or deploy automatically.**

Read `README_FIRST.md` and `ASSET_MANIFEST.json`. Implement **World 1 Tasik Chini** as a turn-based JRPG vertical slice integrated into the DIDIK quiz/room backend. No manual WASD/joystick movement in this Story Mode; auto-travel/scene transitions, then dedicated 2D battle scene.

## Assets
- Use the world background from `01_BATTLE_BACKGROUND` without hero/boss baked in.
- Overlay one alpha cutout hero (`02_HERO_CHARACTERS`) at left and one alpha Naga Chini (`03_BOSS_NAGA_CHINI`) at right, with responsive sizing.
- `04_UI_REFERENCE` includes *concept-only* UI; implement real CSS/Svelte interactive elements with quiz text from backend.
- Do not use `05_COMPOSITE_PREVIEWS` as finished interactive gameplay or as a background replacement.

## Mechanics
- Minimum 10 teacher/parent questions.
- 5 obstacle quiz encounters, then unlock fire/wind/lightning/earth/water options.
- Player starts at 6 hearts: wrong -1.5, correct +0.5 (max 6).
- Boss has five HP bars. Correct quiz answer grants one attack; wrong triggers unavoidable boss retaliation. Reuse available questions fairly if a wrong answer prevents five successful boss hits.
- Solo and multiplayer remain server-authoritative; party shares boss HP, individual player hearts.
- 5 folklore worlds in campaign; only World 1 has Batch03 production art, do not claim other worlds have equivalent assets.
- Remove all 3D game modes `litar`, `penalti`, `lanun`, `menara` safely; preserve 8 2D games.

## Quality / delivery
- Preserve image aspect ratio and alpha. Provide WebP responsive variants, lazy loading where appropriate, safe-size fallbacks.
- Add layered foreground/background, micro animation, attack flashes, screen shake respecting reduced motion; actual sprite frame sets require additional creation.
- Add tests, verify no answer keys leak to browser, use screenshots of **running gameplay** for proof.
- Report limitations honestly. Do not claim mockup composites are functional gameplay.
