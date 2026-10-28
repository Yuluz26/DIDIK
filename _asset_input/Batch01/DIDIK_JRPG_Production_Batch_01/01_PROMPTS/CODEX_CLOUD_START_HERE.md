# Codex Cloud — DIDIK JRPG implementation

You are working **directly on** the existing GitHub repository, not writing an abstract proposal. Read the complete `SHARED_MASTER_SPEC.md` and all asset documents in the attached ZIP. Treat that file as the authority on gameplay and asset use.

**Immediate mission:** Replace the previous WASD/top-down corridor implementation with cinematic auto-progression + separate JRPG quiz battles, remove all four old 3D game modes, and build a high-quality playable Tasik Chini vertical slice first (Hang Tuah, Mahsuri, Naga Chini). Continue to the remaining worlds if the environment and runtime allow.

## Cloud operating rules
- Inspect the GitHub branch and working tree; preserve all unrelated files. The development branch was `feat/legenda-story-mode` and PR #1, but verify actual branch before editing.
- Unzip and inspect every attachment; use concept boards for art direction only, never as complete sprites or deployed background with fake labels.
- If preview/browser/network limitations block game tests or image production, do not invent results. Commit what works, record gaps and give reproducible commands.
- Begin with repository audit and **code changes in same task**, not a lengthy PRD-only response.
- Commit logical increments with targeted tests. Keep PR draft until reviewer approves. Do not merge/deploy automatically.
- If subagent tooling is available, delegate independent code inspection, 3D cleanup, server mechanics review and browser test; integrate carefully. Otherwise work sequentially.

Read `SHARED_MASTER_SPEC.md` now and proceed stage-by-stage, prioritizing a playable, visually convincing JRPG fight over shallow five-world mockups.
