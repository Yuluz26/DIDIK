# DIDIK — Analysis and Build Order

Written before design and implementation. Everything under "Verified" was checked in this session; everything under "Decided" is a default I chose because the question was left open, and can be reversed.

## 1. What was verified

| Area | Finding |
|---|---|
| Repository | Contains only the prompt pack (`README.md`, `docs/01-05`), the PRD, and `.claude/skills/`. No application code, no `CLAUDE.md` or `AGENTS.md`, so there are no existing conventions to inherit and nothing to preserve. |
| Runtime | PHP 8.3.6 with `pdo_mysql`, `pdo_sqlite`, `mbstring`, `intl`, `gd`, `dom`, `curl`, `zip`, `fileinfo`. Node 22. Composer 2.8.12 (running as root, needs `COMPOSER_ALLOW_SUPERUSER=1`). |
| Package registries | Packagist and npm both reachable. |
| Laravel versions | Packagist today: **13.37.0** (requires PHP `^8.3`, released 2026-10-16) and 12.70.0 (`^8.2`). |
| MySQL | No server installed. `mysql-server 8.0.46` is available from apt, so migrations and tests can be verified against real MySQL 8. Docker CLI exists but the daemon is not running, so Docker/Sail cannot be used or tested here. |
| Browser | Chromium is installed (Playwright), so screenshots, console errors and layout checks can really be run. |
| Design skills | **UI/UX Pro Max**: installed, usable (Python search tool, `--stack laravel` exists). **Taste Skill**: installed, usable, with the conflicts below. **Impeccable**: not installed. It will not be used and will not be claimed. |

## 2. Where Taste Skill conflicts with the brief

Taste Skill states it is "not for dashboards or app screens" and bans shadows on resting elements, soft radii, pill buttons and gradients. The PRD requires soft pastel neumorphism, which is shadows and rounded surfaces by definition. The brief says the PRD wins. So:

- **Used:** write the argument before the design, take the idea from the subject, copy-deck first, headlines at two lines or fewer, no eyebrow labels, no index numbering, no monospace, no emoji as icons, no rows of identical cards, no decorative floating shapes, running text in full ink at 16 px or more, one live element, real states and semantics, and the look-then-fix screenshot loop.
- **Not used:** the ban on resting shadows and rounded corners (needed for neumorphism), the "square or full pill" button rule, and its random direction dealing, because the art direction is fixed by the PRD. `draw.mjs` is run only with `--keep palette,type` to take composition options for the homepage.
- Recorded in the design document so it is not silent.

## 3. Decisions on the PRD's open questions

| # | Question | Decision | Why | Reversible? |
|---|---|---|---|---|
| 1 | Admin: Filament or custom | **Custom Blade admin** (changed from the PRD's Filament recommendation) | Filament was never approved, the README says not to add dependencies without authorisation, and the design brief rejects generic dashboard templates as the final look. Cost: more code to write. | Yes, the domain layer is independent of the admin UI. |
| 2 | Laravel version | **Laravel 13** (PRD said 12) | It is the current major and runs on this PHP. A new project should not start on the previous major. Cost: hosting must offer PHP 8.3 or newer. | Yes, before first deploy. |
| 3 | Hosting | Unknown, no deploy work | Database drivers for session, cache and queue, so no Redis or workers are needed. | n/a |
| 4 | Content | Demo seed in `local` and `testing` only: Bahasa Melayu, Matematik, Sains, Bahasa Inggeris, Prasekolah to Tahun 6 | Needed to see the product working. Never seeded in production. | Yes |
| 5 | KSSR mapping | Not in MVP | Content effort, no schema impact now. | Yes, nullable column later. |
| 6 | Characters | Original SVG mascot **Didi**, a mouse-deer (kancil), drawn in code | Kancil is a well-known Malaysian folk character, fits a quiz-adventure, and avoids using a third party's art. The files can be replaced by commissioned art. | Yes |
| 7 | Quizizz | Links only | No verified integration exists. | n/a |
| 8 | Local database | MySQL 8 via `.env`; tests run on SQLite for speed **and** on MySQL for parity | Parity matters because production is MySQL. | n/a |
| 9 | Auth | Small in-house login for the `admin` role, no starter kit | One or two admins. The admin account is created by an Artisan command, never by a seeder. | Yes |
| 10 | Frontend | Vite, plain CSS with custom properties, Alpine.js for the player and editor, no Tailwind | CSS tokens centralised in one place, small JS. | Yes |
| 11 | Fonts | Self-hosted through npm font packages | A third-party font CDN would send every child's IP address to Google. | Yes |

## 4. Build order and gates

Each step ends in a check. A step is not "done" until its gate has actually run.

1. **Design** → `docs/design/DESIGN.md`. Gate: every PRD screen has a layout spec; contrast pairs computed, not assumed.
2. **Scaffold** → Laravel 13, MySQL connection, Vite, token CSS, fonts. Gate: app boots, `migrate` runs on MySQL.
3. **Data layer** → migrations, models, enums, seeders. Gate: `migrate:fresh --seed` passes on MySQL and SQLite.
4. **Quiz engine** → attempts, server-side answer check, scoring. Gate: unit and feature tests, including "correct answer never leaves the server before answering".
5. **Public site + 3 game concepts** → Gate: all pages render, journeys pass in Chromium at 360, 768 and 1366 px, no console errors.
6. **Admin + Quizizz** → Gate: authorisation tests for every admin route, CRUD feature tests, publish workflow tests.
7. **Verification and docs** → full suite on MySQL, screenshot review, known limitations written down honestly.

Out of scope here: deployment, DNS, production configuration, hardening beyond the baseline already in the PRD (that is phase 4), and polish passes (phase 5).
