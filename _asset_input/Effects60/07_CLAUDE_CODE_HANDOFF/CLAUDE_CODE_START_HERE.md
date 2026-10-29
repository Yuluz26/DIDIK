# Claude Code Integration — DIDIK Legenda Elemental Weapons

Please inspect the repository architecture before editing. The `live/web` SvelteKit interface plays quiz-driven turn-based JRPG battles while `live/server` FastAPI/WebSocket remains authoritative for combat.

1. Read `asset_manifest.json`. Use `02_CHARACTER_VARIANTS/<lelaki|perempuan>/hero_<...>_<element>_on_768_canvas.png` for hero visual changes according to selected weapon. Keep hero LEFT and boss RIGHT (facing left).
2. For a correct quiz answer, animate player action: anticipate (140ms), hero slides/sways (180ms), selected elemental attack effect (12 frames at 100ms), boss hit reaction (240ms), retreat/idle (180ms). Damage only from server-confirmed correct answer.
3. For a wrong answer, boss counterattacks and player loses 1.5 hearts; no manual movement or dodging.
4. Render every effect using the 60 ordered PNG frames at `04_ATTACK_FRAMES/<element>/fx_<element>_frame_01.png ... _12.png`, or use animated APNG in supported browsers. Preload for performance.
5. Keep existing 8 2D game modes untouched. Do not reinstate the 4 retired 3D modes. Parents create only a quiz (>=10 questions) and choose Story Mode. Use server-verified combat state.
6. These hero images are static visual variants. Do NOT claim to have complete hero idle/attack/hurt/victory frame animation from this pack. Make controlled tween movement or commission proper pose sequences.
7. Test responsive phones, player readability, browser memory, wrong-answer damage, right-answer healing, five boss HP hits, keyboard controls for quiz choices, and `prefers-reduced-motion`.
8. Do not replace unrelated UI with generated picture previews. Keep playable quiz overlay as accessible UI elements.

No merge or deployment without approval. Record tests and screenshots from actual running gameplay, not concept compositions.
