# CODEX / CLAUDE CODE — Integrate DIDIK JRPG Batch 04

Inspect the existing DIDIK repository and attached Batch 01-04 asset packs. Use this batch for HD battle-state visuals: 6 still poses for Hang Tuah, 6 for Mahsuri, and 5 for Naga Chini. These are separate high-detail RGBA PNG stills, NOT true sprite frame animations. Follow `poses_manifest.json` for filenames and anchor guidance.

1. Use the existing DIDIK FastAPI/WebSocket question checking and the approved five-world Story Mode design.
2. The intended game is **auto story progression + dedicated JRPG quiz battle**. Remove any requirement to move the character manually (no joystick/WASD/dodge). On story encounters, transition to battle automatically.
3. For a correct answer: stage a hero attack/cast with a pose transition and FX, remove 1 boss HP, restore +0.5 player HP (cap six). For a wrong answer: show the boss's attack/special pose, deduct 1.5 player HP; wrong boss answers do not damage the boss. Never let the client author grade/hit/health outcomes.
4. Preserve five selectable elements: Api / Angin / Petir / Tanah / Air. Use effects and icon assets from Batch 02. Keep a clear five-segment boss HP bar and half-heart UI. Parent just makes >=10 questions and selects Story Mode; rotate questions fairly.
5. Treat the battle screenshot in `03_BATTLE_COMPOSITION_REFERENCE` as **concept art**, not as actual game output. Compose backgrounds, actors, weapons, UI, text, animations separately. Create smooth transitions using tween/shake/splash/particles and implement real animation frames/rigging if quality demands it; don't mislabel still poses as finished animation.
6. Remove ALL FOUR 3D games from registry/selection and unused related implementation: Litar Kart, Sepakan Penalti, Peti Lanun, Menara 118. Retain the eight other 2D games and unrelated application behaviour.
7. Prioritise one functional, polished Tasik Chini vertical slice, then expand. Test desktop/mobile, real quiz grading, solo/party, reconnect and progress, then capture real browser screenshots. Work on a feature branch and draft PR, no merge/deploy.

**Final delivery:** branch/PR, tests, running-game screenshots and honest list of any remaining sprite/animation work.
