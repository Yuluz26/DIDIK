# DIDIK — Product Requirements Document

Status: **Draft for approval** · Phase 1 of 5 · Stack decision: **Laravel + MySQL** (confirmed by Yul)

Inputs inspected: `README.md`, `docs/01-PRD.md` (the brief). The repository contains no application code yet, so there is no existing structure to preserve. Local tooling observed: PHP 8.3, Node 22; Composer and MySQL were not confirmed available in the build environment (see Open Questions).

---

## 1. Vision and objectives

DIDIK is a Bahasa Melayu home-learning platform where a quiz feels like a small game, not a worksheet. It is built for Malaysian parents and children, and must stay useful when schools close (haze, floods, strikes) and a family has one shared phone.

Objectives:
1. A child can start a quiz within **two taps** of opening the site, with no account.
2. An admin can create, publish and retire content **without touching code**.
3. Quiz content is stored independently of how it is presented, so a new game concept never requires migrating questions.
4. The admin can keep a curated library of their own Quizizz links, clearly labelled as external.
5. The interface is calm, legible and visibly art-directed (soft pastel neumorphism with real contrast), not a template.

Non-goals: replacing Quizizz, importing or scraping Quizizz content, social features, child accounts with personal data, payments.

## 2. Users and use cases

| Persona | Needs | Key tasks |
|---|---|---|
| **Aina, 8, Tahun 2** | Big targets, short sessions, friendly feedback, no reading walls | Pick a subject, play a quiz, see stars, replay |
| **Puan Farah, parent** | Find the right level quickly, trust the content, hand a phone to the child | Browse by level and subject, start a quiz, read explanations afterwards |
| **Cikgu Amir / admin (Yul)** | Fast authoring, control over what is live | Write questions, assign a game concept, publish, add Quizizz links, check completion numbers |

## 3. Scope

### 3.1 MVP (in)
- Public site: homepage, browse and filter, quiz player, result screen, Quizizz collections page.
- Quiz engine with **multiple choice (single answer)** and **true/false** only.
- **Three game concepts**, implemented as presentation skins over the same quiz data:
  1. *Soalan & Jawapan* — clean question-and-answer, the baseline.
  2. *Kutip Bintang* — progress by collecting stars and a badge at the end.
  3. *Misi Berlevel* — questions grouped into themed levels with a progress path.
- Admin area: categories, quizzes, questions with answers and explanations, game concept and settings, draft/published/archived, Quizizz links and collections, basic statistics.
- Anonymous play with progress held in the browser session; no child data stored server-side beyond anonymous aggregate attempts.

### 3.2 Explicitly out of MVP
Memory matching, treasure hunt, gentle timed mode (candidate concepts for phase 2, the architecture must allow them); child or parent accounts; leaderboards; open-text and drag-drop questions; Quizizz import or embedding; multi-admin roles beyond one `admin` role; email; payments; native apps.

## 4. Functional requirements and acceptance criteria

Priority: **M** must (MVP), **S** should (MVP if time allows), **F** future.

### 4.1 Public platform
| ID | Requirement | Acceptance criteria | P |
|---|---|---|---|
| P1 | Homepage explains DIDIK in BM and offers subject entry points | Loads without login; primary action reaches a quiz list in one tap | M |
| P2 | Browse and filter by subject, topic, school level, difficulty, age range | Filters combine; empty result shows a helpful state; URL reflects filters | M |
| P3 | Only `published` quizzes within their availability window are visible | Draft/archived quizzes return 404 publicly | M |
| P4 | Responsive 360 px to 1440 px | No horizontal scroll at 360, 768, 1366 px | M |
| P5 | Accessibility baseline | WCAG 2.2 AA contrast, full keyboard use, visible focus, tap targets ≥ 44 px, `prefers-reduced-motion` honoured | M |
| P6 | BM interface via Laravel localisation files, ready for a second language | No hard-coded UI strings in Blade templates | M |

### 4.2 Quiz system
| ID | Requirement | Acceptance criteria | P |
|---|---|---|---|
| Q1 | Quiz → ordered questions → options; one or more correct options defined by admin | Correct answer is never sent to the browser before the answer is submitted | M |
| Q2 | Per-question explanation and points | Explanation shown after answering; points feed the score | M |
| Q3 | Quiz settings: attempts allowed, feedback mode (instant / at end), shuffle questions, shuffle options | Settings change behaviour without code changes | M |
| Q4 | Friendly feedback and a completion screen with score, stars and review of mistakes | Result screen reachable only after final answer; review lists explanations | M |
| Q5 | Optional timer per quiz | Disabled by default; expiry finalises the attempt | F |
| Q6 | Progress survives an accidental refresh within the session | Resuming returns to the current question | S |

### 4.3 Game concepts
| ID | Requirement | Acceptance criteria | P |
|---|---|---|---|
| G1 | Admin picks a game concept per quiz | Concept is a registered key plus validated JSON settings | M |
| G2 | Concepts are presentation only | Switching concept on a quiz leaves questions and attempts untouched | M |
| G3 | New concept added by registering one class and one view set | No change to quiz or question tables | M |

### 4.4 Admin dashboard
| ID | Requirement | Acceptance criteria | P |
|---|---|---|---|
| A1 | Authenticated admin only | Unauthenticated access redirects to login; throttled login | M |
| A2 | CRUD for categories, quizzes, questions, options | Validation errors in BM; soft delete | M |
| A3 | Fast question entry | Add many questions in one screen without page reloads between each; reorder by drag | M |
| A4 | Status workflow draft → published → archived | Publishing requires ≥ 1 question and a correct answer on each | M |
| A5 | Availability dates and visibility | Quiz outside its window is hidden | S |
| A6 | Duplicate a quiz | Copy starts as draft | S |
| A7 | Basic stats | Per quiz: started, completed, average score, hardest question | S |

### 4.5 Quizizz link collection
| ID | Requirement | Acceptance criteria | P |
|---|---|---|---|
| L1 | CRUD for link records: title, URL, description, subject, school level, tags, optional thumbnail | Saved and listed in admin | M |
| L2 | URL validation | Must be `https` and host `quizizz.com` or a subdomain; otherwise rejected with a clear message | M |
| L3 | Curated collections of links, ordered | A link can sit in many collections | M |
| L4 | Public page lists published collections; each item has an obvious **Buka di Quizizz** action | Opens in a new tab with `rel="noopener noreferrer"`; labelled as an external site | M |
| L5 | Unavailable-link handling | Admin can mark a link `broken`; public hides it; no automatic scraping or live checks in MVP | M |
| L6 | Optional manual "check link" (HTTP HEAD from admin action) | Result shown to admin only; failure never blocks saving | F |

**Quizizz constraints.** Quizizz links are treated as plain external URLs. We do not import, scrape, embed in an iframe, or convert them to native quizzes. No API integration is assumed. If Yul wants import or embedding, that needs a verified, authorised route with Quizizz first; it is logged as an open question, not a plan.

## 5. Non-functional requirements
- **Performance:** mobile LCP ≤ 2.5 s on a mid-range phone over 4G; server-rendered pages; images in WebP with explicit dimensions; quiz player under ~150 KB of JS.
- **Availability on poor connections:** quiz data fetched once per attempt; the player works if the connection drops between questions (answers queued, synced at the end). Offline-first PWA is future.
- **Security:** see section 9.
- **Maintainability:** conventional Laravel structure, no unnecessary packages, feature tests for quiz logic.
- **Observability:** Laravel log to file, error page in BM, no third-party tracking.

## 6. Information architecture and journeys

```
/                     Homepage
/kuiz                 Browse + filters
/kuiz/{slug}          Quiz intro (level, count, concept)
/kuiz/{slug}/main     Player
/kuiz/{slug}/keputusan/{attempt}   Result
/pautan-quizizz       Quizizz collections
/pautan-quizizz/{slug}
/tentang   /privasi
/admin/...            Login, dashboard, kategori, kuiz, soalan, pautan, koleksi, statistik
```

Journey, child: Home → *Mula Bermain* → pick subject → quiz intro → play → result with stars → *Main Lagi* or another quiz.
Journey, parent: Home → filter by Tahun and subject → quiz → result review with explanations.
Journey, admin: Login → *Kuiz Baharu* → set details and concept → add questions in bulk → preview → publish.

## 7. Data model (MySQL 8, InnoDB, utf8mb4)

| Table | Key columns | Notes |
|---|---|---|
| `users` | id, name, email, password, role | Admins only in MVP |
| `categories` | id, parent_id, name, slug, type (`subject`/`topic`), position | Self-referencing for subject → topic |
| `school_levels` | id, name, slug, min_age, max_age, position | e.g. Prasekolah, Tahun 1–6 |
| `quizzes` | id, slug, title, summary, category_id, school_level_id, difficulty, status, game_concept, game_settings (JSON), settings (JSON: attempts, feedback, shuffle), available_from/until, created_by, soft deletes | Content separate from presentation |
| `questions` | id, quiz_id, type (`single`/`truefalse`), body, explanation, points, position, soft deletes | |
| `question_options` | id, question_id, body, is_correct, position | |
| `quiz_levels` | id, quiz_id, title, position | Used by *Misi Berlevel*; questions get nullable `quiz_level_id` |
| `attempts` | id, uuid, quiz_id, started_at, completed_at, score, max_score, session_hash | No name or personal data |
| `attempt_answers` | id, attempt_id, question_id, option_id, is_correct | Powers per-question stats |
| `quizizz_links` | id, title, url, description, category_id, school_level_id, thumbnail_path, status (`draft`/`published`/`broken`/`archived`), soft deletes | |
| `quizizz_collections` | id, title, slug, description, status, position | |
| `quizizz_collection_link` | collection_id, link_id, position | Many-to-many |
| `tags`, `taggables` | polymorphic | For quizzes and links |

Key indexes: `quizzes(status, available_from)`, `quizzes(slug)` unique, `questions(quiz_id, position)`, `attempts(quiz_id, completed_at)`.

## 8. Recommended technical architecture

- **Laravel 12** (PHP 8.3), **MySQL 8**, server-rendered **Blade** with **Alpine.js** for the quiz player; **Vite** for assets; plain CSS with design tokens (the design phase decides whether Tailwind is worth it). No SPA framework.
- **Admin:** two options for decision.
  - *Filament 3/4* — fastest to a polished CRUD with drag-reorder, repeaters and bulk question entry; adds one significant dependency.
  - *Custom Blade admin* — no dependency, more build time, fully matches the art direction.
  - **Recommendation: Filament for the admin, custom Blade for the public site.** Admin users are one or two people; speed of authoring matters more than admin aesthetics. This needs Yul's approval because it adds a dependency.
- **Game concepts:** a `GameConcept` interface and a registry (`GameConceptRegistry`) mapping a key to a Blade view set and a settings validator. Quizzes store the key and JSON settings only.
- **Domain structure:** `app/Models`, `app/Services/QuizEngine` (starting an attempt, scoring, server-side answer checking), `app/Games`, `app/Http/Controllers/Public`, `app/Filament`.
- **Answer checking is server-side:** the player receives questions without `is_correct`; each answer is posted and checked, and the explanation is returned.
- **Hosting:** unknown, shared hosting or VPS decides queue/cache choices. MVP uses `database` driver for sessions, cache and queue to avoid extra services. No deployment actions without approval.

## 9. Security and child privacy
- Collect no child names, emails, photos or precise location. Attempts are anonymous, linked to a hashed session token.
- Malaysia's **PDPA 2010** applies to any personal data; keeping children anonymous avoids most of it. Final privacy notice wording needs a human or legal review.
- No third-party trackers or ad scripts. If analytics is added, use a cookieless, self-hosted option.
- Admin: bcrypt/argon hashing, login throttling, CSRF, session fixation protection, optional 2FA (future), HTTPS-only cookies in production.
- All admin input validated; Blade escaping by default; question HTML limited to a safe subset if rich text is allowed.
- Uploads: image mime/size allow-list, stored outside web root or re-encoded.
- External links: `rel="noopener noreferrer"`, no iframes, host allow-list for Quizizz URLs.
- Rate-limit attempt creation and answer endpoints.

## 10. Testing strategy
- **Feature tests (Pest or PHPUnit):** public visibility rules, attempt lifecycle, server-side scoring, Quizizz URL validation, admin authorisation.
- **Unit tests:** scoring, game concept registry, settings validation.
- **Browser/manual:** keyboard-only quiz run; screen reader pass on player; 360, 768, 1366 px checks; reduced-motion check.
- **Accessibility:** automated axe scan plus manual contrast verification of the pastel palette.
- **Success criteria:** see section 11.

## 11. Success measures
- Child starts a quiz in ≤ 2 taps from the homepage.
- Admin adds a 10-question quiz in ≤ 10 minutes.
- 100 % of public pages pass automated WCAG 2.2 AA checks; zero contrast failures on text.
- Mobile LCP ≤ 2.5 s on throttled 4G.
- Quiz completion rate ≥ 60 % once real traffic exists (to be baselined; no target before data).

## 12. Assumptions, risks, dependencies

**Assumptions:** one or two admins; content authored by Yul; public traffic modest at launch; Quizizz links are supplied manually.

| Risk | Impact | Mitigation |
|---|---|---|
| Pastel neumorphism fails contrast | Accessibility failure | Neumorphism only on surfaces and controls; text always on high-contrast tokens; contrast verified in phase 2 |
| Scope creep into many game types | Delay | Three concepts only; registry makes the rest additive |
| Filament adds upgrade burden | Maintenance | Pin versions; keep domain logic outside Filament |
| Quizizz changes or removes links | Dead links | `broken` status and manual check; no dependence on their API |
| Child-privacy misstep | Legal and trust | Anonymous by design; review before launch |
| Hosting unknown | Rework | Database drivers by default; confirm before phase 4 |

**Dependencies:** PHP 8.3+, Composer, Node 22 for Vite, MySQL 8, a place to host.

## 13. Phased roadmap
1. **PRD** (this document) — approval.
2. **Design/UI-UX** — tokens, neumorphism rules with contrast checks, characters, player and admin wireframes. Uses taste-skill and ui-ux-pro-max.
3. **MVP** — Laravel scaffold, migrations and seeders, quiz engine, three concepts, public pages, admin, Quizizz module.
4. **Production** — security review, performance, backups, error handling, deployment plan (needs hosting decision).
5. **Polish** — UI/UX refinement and regression pass.
6. *Later:* memory matching, treasure hunt, timed mode, parent accounts, PWA/offline.

## 14. Open questions (need Yul's decision)
1. **Admin:** Filament (recommended) or a custom Blade admin?
2. **Hosting:** shared hosting, VPS, or managed (Forge, Laravel Cloud)? Affects queue, cache and storage choices.
3. **Domain:** is DIDIK public-facing with a custom domain at launch?
4. **Content:** which subjects and school levels first? Is Bahasa Melayu content only, or also English-medium subjects like Maths and Science?
5. **Curriculum alignment:** should quizzes map to KSSR topics? It makes browsing better but needs content effort.
6. **Characters and illustrations:** will you supply them, or should the design phase propose an original set?
7. **Quizizz:** are you sure links only is enough, or do you want to approach Quizizz about a formal integration?
8. **Local environment:** Composer and MySQL were not confirmed in this cloud session. Should phase 3 target a local MySQL on your machine, or should I add Docker/Sail config?
