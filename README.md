# DIDIK — Claude Code Prompt Pack

This pack contains five staged prompts for planning, designing, building, hardening, and polishing DIDIK.

## Recommended workflow

1. `docs/01-PRD.md` — Define the product and requirements. Do not implement yet.
2. `docs/02-DESIGN-UI-UX.md` — Establish the design direction and system. Do not begin full implementation yet.
3. `docs/03-MVP.md` — Implement the approved MVP.
4. `docs/04-PRODUCTION.md` — Audit and harden the MVP for real-world use.
5. `docs/05-POLISH-UP.md` — Refine UI/UX and verify regressions.

Run one phase at a time. Review and approve each phase's deliverables before moving to the next. Keep the approved PRD and design specification as the source of truth.

## Skills and libraries

Before each relevant phase, Claude Code should inspect the repository's instructions and available skills. Use Taste Skill, UI/UX Pro Max, Impeccable, and other existing tools only when they are actually available and relevant. Do not claim to have used unavailable tools, install dependencies without authorization, or assume their capabilities without reading their instructions.

## Project principles

- Primary interface language: Bahasa Melayu.
- Audience: Malaysian parents and children.
- Visual direction: cute, attractive, accessible, carefully art-directed pastel neumorphism.
- Admins can manage quizzes, questions, game concepts, and collections of external Quizizz links.
- Treat Quizizz links as external resources unless an authorized and verified integration is established.
- Preserve existing project structure and unrelated functionality.
- Do not deploy or change production infrastructure without explicit approval.
