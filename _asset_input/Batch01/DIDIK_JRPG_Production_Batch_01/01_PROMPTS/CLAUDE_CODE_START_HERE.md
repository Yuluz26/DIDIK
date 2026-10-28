# Claude Code — DIDIK JRPG implementation

Read `SHARED_MASTER_SPEC.md`, all `02_ASSET_SPEC/` material and original master list before coding. This is an implementation request, **not** just a planning task. You are the senior game engineering lead and must coordinate code, QA, and asset use inside the existing DIDIK repo.

## Agent workflow (if available)
Use available parallel agents deliberately, in non-overlapping files:
- **Architecture/server:** inspect room/quiz contract; implement state machine and scoring/checkpoint/co-op safeguards.
- **Frontend/game scene:** implement auto-story stages, character selection, distinct JRPG battle scene, cinematic transitions and touch-first HUD.
- **Asset QA:** inspect all reference art, produce a source/licence-aware manifest and flag which images are not deployable sprites, without editing backend code.
- **QA/tests:** model 10-question boss progression, 6 half-heart rules, multi-client races and mobile/desktop browser screenshots.

If parallel agents are unavailable, execute those workstreams sequentially. Do not claim an agent or visual asset has done work without real evidence.

## Developer constraints
- Do not change unrelated site design, existing Laravel structure, authentication, or the eight surviving 2D games.
- Remove Litar Kart, Sepakan Penalti, Peti Lanun, Menara 118 from active registry + dependencies as verified; no 3D game.
- The current Story Mode movement/engage flow must be superseded: **no manual player navigation**. The player primarily interacts by **answering questions and selecting elements**, then watches authentic JRPG combat animations.
- Validate every battle event on server; animation only visualizes authoritative results.
- Do not auto merge or deploy. Leave a safe Draft PR, commits, tests, screenshots, and a precise status report.

**Proceed with the high-quality Tasik Chini vertical slice first, then generalize.** Every detail in `SHARED_MASTER_SPEC.md` remains mandatory.
