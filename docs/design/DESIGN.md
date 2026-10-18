# DIDIK — UI/UX Concept and Design System

Status: **Phase 2, approved to proceed to build by Yul** · Source of truth for tokens: `resources/css/tokens.css` (created in the build; this document specifies it).
Nothing in this document has been browser-tested yet. Verification results are reported separately in `docs/IMPLEMENTATION.md` after the build.

## 0. How the design tools were used

| Tool | Used | How | Where it disagreed |
|---|---|---|---|
| **UI/UX Pro Max** | Yes | `--design-system` (dials: variance 3, motion 3, density 3), `--domain style/color/typography/ux`, `--stack laravel` | The generated *pattern* (testimonial landing), *style* (Swiss minimal) and *colours* (SaaS blue/violet/gold) did not fit a children's product and were **not** adopted. Kept: Fredoka + Nunito (its "Playful Creative" pairing), the neumorphism entry (which flags **accessibility risk: high**), the UX rules below, and the Laravel guidance. It suggests Tailwind; this project uses plain CSS tokens instead. |
| **Taste Skill** | Yes, partly | Idea-from-subject method, argument-first copy, `draw.mjs --keep palette,type` for composition | It is "not for dashboards or app screens" and bans resting shadows and soft radii, which the PRD requires. **Adopted:** direction *One motif*, the "write claims then sections" method, headline ≤ 2 lines, no eyebrow labels, no index numbers, no monospace, no emoji icons, no card-grid rows, full-ink body text ≥ 16 px, one live element, the look-and-fix screenshot loop. **Redrawn:** the dealt hero blueprint (*Tabbed folder stack*: dark ground, condensed capitals) contradicts the pastel brief, so the hero is composed from the *One motif* direction text instead. **Not met on purpose:** its "four real photographs" floor, because a children's product should not use stock photos of people. Imagery is original illustration. |
| **Impeccable** | No | Not installed | — |

Rules from UI/UX Pro Max that are binding here: never convey meaning by colour alone; focusable error summary on admin forms; a non-drag alternative for reordering; `scroll-padding` so sticky UI never hides focus; shared motion tokens and `prefers-reduced-motion`; `@error`, `old()`, `@csrf` on every form.

## 1. Concept: *Seberang Sungai*

**The idea.** In the Malay folk tale, Sang Kancil crosses a river by stepping from stone to stone. On DIDIK, **that river crossing becomes the one motif, the round stepping stone**, and it runs through the whole system: the answer buttons, the subject tiles, the progress path, the level markers, the bullets, and the shape of the primary button.

Competitor test: Quizizz or Kahoot cannot say this sentence. It is specific to a Malaysian story every child in the audience already knows.

**The mascot.** *Didi*, a mouse-deer (kancil), is the child's guide. Original SVG drawn for this project (see §6.6).

**The live thing.** On the homepage a child answers one **real question** from the published bank, with the answers as three stones. Tap the right one and Didi hops onto it. It uses the same server-side answer check as the quizzes, and without JavaScript it degrades to the question text and a link into the full quiz.

**Why this suits the brief.** Neumorphism is soft discs and wells. A round stone is the natural neumorphic object, and a river path gives progress a meaning instead of a generic bar.

### Brand principles
1. **Calm, not loud.** Pastel is the field, never the text. One strong colour (pandan green) carries actions.
2. **Tactile and honest.** Raised means "you can press it". Sunken means "it holds something" or "this is chosen". Depth is never decoration.
3. **Never shame a wrong answer.** Wrong answers get a hint and an explanation, not a red cross.
4. **One idea, said once.** One motif, one mascot, one accent. No floating confetti, no random shapes.
5. **Readable first.** If the neumorphic look and legibility disagree, legibility wins.

### Voice (Bahasa Melayu)
Short, warm, direct, spoken Malay that a parent would use at the table. Address the child as *kamu*, parents as *anda*.

| Instead of | Write |
|---|---|
| "Tingkatkan pengalaman pembelajaran anda" | "Kuiz yang rasa macam permainan." |
| "Jawapan anda salah" | "Belum tepat. Cuba lagi." |
| "Tahniah atas pencapaian cemerlang!" | "Cemerlang! Didi bangga dengan kamu." |
| "Sila daftar untuk meneruskan" | (never; no sign-up for children) |

## 2. Sitemap and flows

```
/                           Laman utama (hero + soalan pantas)
/kuiz                       Semak imbas + tapis
/kuiz/{slug}                Pengenalan kuiz
/kuiz/{slug}/main           Pemain (konsep permainan ikut tetapan kuiz)
/kuiz/{slug}/keputusan/{id} Keputusan + semak jawapan
/pautan-quizizz             Koleksi pautan Quizizz
/pautan-quizizz/{slug}      Satu koleksi
/tentang                    Untuk ibu bapa
/privasi                    Notis privasi
/admin/log-masuk            Log masuk pentadbir
/admin                      Papan pemuka
/admin/kategori             Subjek dan topik
/admin/kuiz                 Senarai, cipta, sunting
/admin/kuiz/{id}/soalan     Editor soalan (satu skrin, simpan sekali gus)
/admin/pautan-quizizz       Pautan
/admin/koleksi-quizizz      Koleksi + susunan
```

**Child:** Home → *Mula bermain* → ▶ on a quiz row → first question → result with stars → *Main lagi* / another quiz. That is **two taps** from the homepage to the first question: the round play button on a quiz row goes straight to the player, and only the row's title opens the intro page (rules, attempts, concept) for parents. The hero's live question is the zero-tap entry.
**Parent:** Home → level chip → quiz → result → *Semak jawapan* (explanations).
**Admin:** Log masuk → Kuiz baharu → Maklumat + Permainan → Soalan (bulk) → Terbitkan (checks) → live.

## 3. Design system

### 3.1 Colour tokens

Ground and ink:

| Token | Value | Role |
|---|---|---|
| `--ground` | `#E8F0EB` | Page field, neumorphic base (pale pandan milk) |
| `--ink` | `#17241D` | All body text and headings |
| `--ink-2` | `#3E5247` | Secondary text, captions (never lighter) |
| `--brand` | `#1C6B4A` | Primary action fill, links, selected ring |
| `--brand-hover` | `#165A3D` | Primary hover/pressed |
| `--on-brand` | `#FFFFFF` | Text on brand |
| `--focus` | `#1D4ED8` | Focus ring only |
| `--river` | `#CFE6F2` | The flat river band |
| `--star-fill` / `--star-stroke` | `#F5C04A` / `#8C5E00` | Stars and medals (stroke carries the contrast) |

Feedback and subject pairs (every tint is always used with its own ink, never with another):

| Role | Tint | Ink | Icon |
|---|---|---|---|
| Betul (correct) | `#CDEBD8` | `#14532D` | check |
| Hampir (hint) | `#FFE1D2` | `#8A2F0B` | lightbulb |
| Maklumat | `#D3E8F8` | `#174F78` | info |
| Bahasa Melayu (peach) | `#FFDCCC` | `#7A3115` | book |
| Matematik (sky) | `#D3E8F8` | `#174F78` | calculator |
| Sains (butter) | `#FBEBB5` | `#6B4E00` | flask |
| Bahasa Inggeris (lilac) | `#E4DAF6` | `#4F3689` | languages |
| Lain-lain (mint) | `#CDEBD8` | `#1B5E3F` | shapes |

**Computed contrast (WCAG 2.2, measured, not assumed):**

| Pair | Ratio | Requirement | Result |
|---|---|---|---|
| ink on ground | 13.85 | 4.5 | pass |
| ink-2 on ground | 7.23 | 4.5 | pass |
| brand on ground | 5.57 | 4.5 | pass |
| on-brand on brand | 6.46 | 4.5 | pass |
| on-brand on brand-hover | 8.19 | 4.5 | pass |
| focus on ground / on white | 5.77 / 6.70 | 3.0 | pass |
| star-stroke on ground | 4.87 | 3.0 | pass |
| ok ink on ok tint | 7.15 | 4.5 | pass |
| hint ink on hint tint | 6.80 | 4.5 | pass |
| info ink on info tint | 6.87 | 4.5 | pass |
| subject inks on their tints | 6.06 to 7.18 | 4.5 | all pass |
| ink on every tint | 11.98 to 13.51 | 4.5 | all pass |

Known and accepted: the gold star *fill* is 1.45:1 on the ground. It is decorative; the dark stroke (4.87:1) defines the shape, and the score is always also written as text ("3 daripada 3 bintang"). Admin table row dividers (1.41:1) are decorative; admin **input borders use `--field-border` ≥ 3:1**.
A unit test (`DesignTokenContrastTest`) parses `tokens.css` and fails the build if a declared pair drops below its requirement.

Admin additions: `--admin-bg #F3F6F4`, `--panel #FFFFFF`, `--field-border #6F847A`, `--danger #B42318` (6.57:1 on white), `--warn-tint #FDEFC8` / `--warn-ink #7A4B00`.

### 3.2 Typography

| Role | Face | Size (fluid) | Weight | Line height |
|---|---|---|---|---|
| Display (hero only) | Fredoka | `clamp(2.5rem, 1.2rem + 5.5vw, 5rem)` | 600 | 1.02 |
| H2 / question | Fredoka | `clamp(1.75rem, 1.2rem + 2.2vw, 2.75rem)` | 600 | 1.12 |
| H3 | Fredoka | `clamp(1.25rem, 1.05rem + 1vw, 1.625rem)` | 500 | 1.2 |
| Body | Nunito | `1.125rem` (18 px) | 500 | 1.55 |
| Small / meta | Nunito | `0.9375rem` (15 px) | 700 | 1.4 |

Five steps, two families, no monospace, no uppercase tracked labels. Body never below 16 px; the smallest text anywhere is 15 px. Line length 45 to 70 characters for running text. Headlines are two lines or fewer at 360, 768 and 1366 px. Fonts are **self-hosted** through npm font packages (no Google Fonts request, so no child IP address leaves the site). `font-display: swap`; Latin subset only.

### 3.3 Space, radius, layout
- Spacing scale (4 px base): 4, 8, 12, 16, 24, 32, 48, 64, 96, 128. Gap between sections `clamp(64px, 10vw, 128px)`, always clearly larger than any gap inside a section.
- Radius: `12` (small controls), `20` (inputs, panels), `28` (large panels), `999` (stones, buttons, chips). Four values, nothing else.
- Container `min(100% - 2 × gutter, 72rem)`, gutter `clamp(16px, 4vw, 32px)`. Reading column 40rem.
- Breakpoints (mobile first): 30rem, 48rem, 64rem, 80rem. Checked at 360, 390, 768, 1024, **1366 × 768**, 1440.
- Tap targets: answers ≥ 64 px high, primary buttons ≥ 56 px, any other control ≥ 48 px (admin ≥ 44 px). Gap between targets ≥ 8 px.

### 3.4 Elevation (neumorphic surfaces)

Light comes from the top left. Shadows are tinted pandan-grey, never black.

| Token | Value | Use |
|---|---|---|
| `--light` / `--dark` | `rgba(255,255,255,.95)` / `rgba(98,128,112,.32)` | Shadow colours |
| `--raised-1` | `3px 3px 8px dark, -3px -3px 8px light` | Chips, small stones |
| `--raised-2` | `6px 6px 16px dark, -6px -6px 16px light` | Panels, answer stones, secondary buttons |
| `--raised-3` | `12px 12px 28px dark, -10px -10px 24px light` | Hover lift, hero stone |
| `--inset-1` | `inset 3px 3px 7px dark, inset -3px -3px 7px light` | Progress track, inputs |
| `--inset-2` | `inset 6px 6px 14px dark, inset -6px -6px 14px light` | Pressed, selected |

Rules:
1. **Raised = pressable. Inset = chosen or containing.** Never mix them up.
2. Neumorphism never carries meaning alone. Every selected state also has a 3 px `--brand` ring and a check icon. Every feedback state also has text and a shape.
3. The primary action is **not** neumorphic-low-contrast: it is a flat `--brand` stone with white text and a raised shadow.
4. Text never sits on a neumorphic edge; it sits inside a surface with its own padding.
5. No gradients. Flat fills only. No blur, no glass.

### 3.5 Motion
Tokens: `--dur-press 120ms`, `--dur-state 200ms`, `--dur-feedback 320ms`, `--dur-hop 520ms`; `--ease-out cubic-bezier(.2,.8,.2,1)`, `--ease-hop cubic-bezier(.34,1.4,.64,1)` (one soft overshoot, used only for the hop).
Only `transform` and `opacity` animate (plus box-shadow on press). Motion must mean something: press-in, answer result, a hop to the next stone, a star arriving. Nothing loops. No flashing. Under `prefers-reduced-motion: reduce`, every duration drops to ~0, the hop becomes an instant reposition, and stars appear without travel; all content and feedback stay.

### 3.6 Components and states

State matrix for every interactive component:

| State | Treatment |
|---|---|
| Rest | Raised (pressable) or flat (text) |
| Hover | `--raised-3` plus `translateY(-1px)`; cursor pointer. Pointer devices only |
| Focus-visible | 3 px `--focus` outline, 3 px offset, never removed. `scroll-padding-top` clears the sticky header |
| Pressed | `--inset-2`, no lift, 120 ms |
| Selected | `--inset-2` + 3 px `--brand` ring + check icon + `aria-pressed`/`aria-checked` |
| Disabled | `aria-disabled`, 55 % opacity on the shape only; the label stays readable; no hover |
| Success / hint | Tint + ink pair + icon + words |
| Error (forms) | Inline message with icon beside the field, plus a focusable summary above the form |
| Loading | Skeleton well (inset) with a text label for screen readers; a "Memuatkan soalan…" status |

Core components (all Blade, no JS unless noted):
- **Stone button** (`x-button`): `primary` (brand fill), `secondary` (raised ground), `quiet` (text), `icon` (48 px round), `danger` (admin). Fully round, 56 px high on public pages, 44 px in admin.
- **Answer stone** (`x-quiz.option`): full-width row, lettered disc (A to D) + label; true/false variant shows two large stones.
- **Subject stone** (`x-subject-tile`): large disc with the subject's icon in its tint, name and quiz count.
- **Quiz row** (`x-quiz-row`): leading subject disc, title, meta line (level, difficulty, number of questions), trailing round play button. Replaces a card grid.
- **Chip** (`x-chip`): level and difficulty filters; toggle with `aria-pressed`.
- **Field** (`x-field`): label above, helper text, inset well with a `--field-border` outline, inline error.
- **Alert** (`x-alert`): info, success, hint, danger, always with icon and words.
- **Progress**: dots (QA), star slots (Kutip Bintang), river path (Misi Berlevel), all with a text "Soalan 3 daripada 8".
- **Dialog** (`x-dialog`): native `<dialog>`, focus trapped by the browser, Escape closes, used for mobile menu and destructive confirmation.
- **Mascot** (`x-mascot mood="happy|think|cheer|hint|wave|sleep"`), **Star** (`x-star`), **Icon** (`x-icon`).
- **River band** (`x-river`): full-width flat `--river` band with a wavy top edge, separating halves of a page.

### 3.7 Icon and illustration direction
- Icons: 24 px grid, 2 px round-cap stroke, Lucide-style (ISC licence, a handful of files copied in as inline SVG; no icon dependency at runtime). Decorative icons are `aria-hidden`; meaningful icons have a text label beside them. No emoji anywhere in the interface.
- Illustration: flat shapes, no outlines on fills, features drawn in `--ink`, round caps, a single warm "gula melaka" caramel for Didi against the cool pandan ground. No gradients, no stock photography of people, no scatter of decorative shapes.

## 4. Game concepts

### 4.1 Comparison

| | **Soalan & Jawapan** | **Kutip Bintang** | **Misi Berlevel** (*Seberang Sungai*) |
|---|---|---|---|
| Key | `qa` | `stars` | `quest` |
| Visual identity | Clean card, dots progress | Star slots that light up | River path, stones, Didi hops |
| Core loop | Read, answer, read the note, next | Answer to light a star slot, watch the collection grow | Answer to move to the next stone, finish a level checkpoint, cross the river |
| Question presentation | One question per screen | One question per screen with the slot row above | One question per screen, path strip above |
| Answer behaviour | Tap an answer stone | Same | Same |
| Feedback | Tint + icon + words + explanation | Same, plus the slot lights gold (correct) or stays an empty stone (wrong) | Same, plus Didi hops; on a wrong answer Didi wobbles and still moves on, the stone is not lit |
| Reward | 1 to 3 stars at the end | Stars collected; a badge at the end | Level checkpoint "Tahap 1 selesai"; final medal |
| Progress | Dots | Row of star slots | Path of stones grouped by level |
| Mobile | Single column | Slot row scrolls horizontally if more than 10 questions | Path becomes a short strip of the current level only |
| Accessibility | Baseline | Count read as text, not only drawn | Position read as text ("Tahap 1, batu 3 daripada 5"); animation optional |
| Settings (validated JSON) | `progress`: `dots` or `bar` | `show_streak`: boolean | `level_size`: integer 3 to 10 (default 5) |
| Cost | Lowest | Low | Medium (path layout) |

**Decision: build all three in the MVP.** They are small because they share one engine and one set of components. Only the progress strip, the feedback flourish and the end-of-quiz reward differ, and each is one Blade view set.

### 4.2 Architecture
A concept is one PHP class (`key`, `name`, `description`, `defaults`, `rules`, `fields`, `view`) registered in `GameConceptRegistry`, plus one folder of Blade views under `resources/views/games/{key}`. The quiz stores only `game_concept` (string) and `game_settings` (JSON). An unknown or removed key falls back to `qa` at render time, so nothing breaks. Scoring lives in the quiz engine and never reads the concept, so switching concept cannot change a score. The admin form renders concept settings from the concept's `fields()` definition, so adding a concept needs no admin code.

Candidate concepts deferred (post-MVP): memory matching, treasure hunt, gentle timed challenge.

## 5. Screens

Layouts are mobile first; the desktop notes are what changes. "State" lists what must exist.

### 5.1 Public

| Screen | Mobile (360) | Desktop (1366 × 768) | States |
|---|---|---|---|
| **Homepage** | Wordmark + menu button. Headline *"Kuiz yang rasa macam permainan."* (≤ 2 lines), one sentence, **Mula bermain**. Live question: question text, three answer stones in a column, Didi above. River band. Subjects as four large discs 2 × 2. Level chips row. Three-ways-to-play list. Parents statement. Footer. | Left column: headline at the display size, sentence, button. Right: one very large stone cropped by the viewport edge carrying Didi, the question and three stones on an arc. Same sections, but "three ways to play" alternates sides. Footer wordmark spans full width. | Live question: loading, correct, hint, no question available (section hidden), JS off (static question + link) |
| **Semak imbas** `/kuiz` | Search field, level chip row (horizontal scroll with visible edge), subject select, then quiz rows. | Left 280 px filter column (subject, level, difficulty), right a two-column list of quiz rows. | Empty (Didi sleeping, *"Belum ada kuiz yang sepadan."* plus a clear-filters button), loading skeleton, many pages (pagination) |
| **Pengenalan kuiz** | Title, summary, meta (level, difficulty, N soalan, game concept name), rules in plain words, **Mula** button. | Two columns: info left, a large concept illustration right. | Unavailable (404 page with Didi and a link to all quizzes), attempts used up (shows best score, link to review) |
| **Pemain** | Top: quit button (back to intro, confirm), progress strip, "Soalan N daripada M". Question in H2. Answer stones stacked. After answering: feedback panel slides in above the Next button. | Centred column 40rem; progress strip wider. | Loading, resume, offline retry, last question (button says *Lihat keputusan*), feedback `end` mode (no correctness shown) |
| **Keputusan** | Didi (cheer / hint), stars, "6 daripada 8 betul", message, **Main lagi**, **Kuiz lain**, then *Semak jawapan* as `<details>` per question. | Result left, review right. | Not owner of attempt (friendly page), attempts used up |
| **Pautan Quizizz** | Intro line stating these are links to Quizizz and open in a new tab. Collections as sections with link rows (title, subject, level, **Buka di Quizizz** with an external-link icon). | Two-column link rows; collection title left. | No collections (empty state), broken links hidden, thumbnail missing (subject disc fallback) |
| **Untuk ibu bapa / Privasi** | Plain long-form text in the reading column. | Same. | — |
| **404 / 500 / 419 / 429** | Didi + one sentence + home link, in Bahasa Melayu. | Same. | — |

### 5.2 Admin (shares tokens, drops decoration)

Shell: left sidebar (Papan Pemuka, Kuiz, Kategori, Pautan Quizizz, Koleksi) with the wordmark, user and *Log keluar*; under 64 rem it becomes a top bar with a menu dialog. Flat panels on `--admin-bg`, 44 px controls, real table rows, no neumorphic depth on data views (depth appears only on the DIDIK buttons so the brand carries over).

| Screen | Content | States |
|---|---|---|
| **Log masuk** | Email, password, error summary, throttled after 5 tries | Invalid credentials, throttled |
| **Papan pemuka** | One strip of numbers (Diterbitkan, Draf, Percubaan 7 hari, Purata skor), then *Perlu perhatian* (drafts, quizzes with no questions) and *Soalan paling sukar* | Empty system (first-run prompt) |
| **Senarai kuiz** | Search, status filter, table (title, subject, level, status, questions, attempts, updated) with row actions | Empty, filtered-empty |
| **Borang kuiz** | Sections: Maklumat asas, Permainan (concept radios + generated settings), Peraturan kuiz, Penerbitan. Error summary. | Validation, publish blocked with reasons |
| **Editor soalan** | One long page of question blocks, **Simpan semua** in a sticky bar showing unsaved changes, move up/down, duplicate, delete with confirm dialog, add option, mark correct | Validation per field, no questions yet |
| **Kategori** | Subjects with nested topics, inline add/rename, delete blocked while in use | Empty |
| **Pautan Quizizz** | Table + form (title, URL, description, subject, level, tags, thumbnail, status) | Invalid URL message, broken status |
| **Koleksi** | Collection form + list of links with order buttons | Empty |

## 6. Wording, copy and mascot specs

### 6.1 Homepage copy deck (Bahasa Melayu)
- H1: **Kuiz yang rasa macam permainan.**
- Lead: *Soalan pendek dalam Bahasa Melayu untuk Prasekolah hingga Tahun 6. Sesuai bila sekolah tutup dan belajar di rumah.*
- Primary button: **Mula bermain**
- Live question heading: *Cuba satu soalan*; right: *Didi melompat ke batu seterusnya.*; hint: *Belum tepat. Cuba satu lagi.*; link after: *Teruskan dengan kuiz penuh*
- Subjects section H2: *Pilih mengikut tahun dan subjek.*
- Ways to play H2: *Tiga cara bermain, soalan yang sama.*
- Parents H2: *Tiada akaun. Tiada data peribadi.* Three plain lines: *Anak tak perlu daftar.* / *Kami tak simpan nama atau gambar.* / *Selepas setiap kuiz, setiap jawapan ada penjelasan.*
- Quizizz teaser H2: *Pautan Quizizz pilihan.* with the line *Ini pautan ke Quizizz. Ia dibuka di tab baharu.*

### 6.2 Result messages
3 stars *"Cemerlang! Didi bangga dengan kamu."* · 2 stars *"Bagus! Sikit lagi untuk tiga bintang."* · 1 star *"Tak apa. Setiap percubaan buat kita lebih tahu."* Everyone who finishes gets at least one star. Thresholds: 85 % and above is 3, 60 % and above is 2, otherwise 1.

### 6.3 Mascot: Didi
Head-and-shoulders mouse-deer: caramel fur `#E7B98A`, shade `#C88F5A`, cream belly `#FFF4E6`, ear inner `#F7C6C0`, features `--ink`. Big round eyes with a highlight, small nose, long ears, white spots. Moods change only eyes, mouth, brows, ears and arms, so one base drawing serves all: `happy`, `think`, `cheer` (arms up), `hint` (gentle, head tilted, small "oh"), `wave`, `sleep` (eyes closed, for empty states). Decorative by default (`aria-hidden`); where Didi carries information the sentence beside it carries the same words.

## 7. Responsive and accessibility specification

- **Layout:** no horizontal scroll at 360 px; text reflows at 200 % zoom; viewport meta without `user-scalable=no`.
- **Keyboard:** every action reachable and operable; order matches visual order; answer stones are real `<button>`s in a `role="group"` with an accessible question label; after a question loads, focus moves to the question heading; after an answer, focus moves to the feedback panel's *Seterusnya* button.
- **Screen readers:** `aria-live="polite"` region announces the feedback sentence; progress is text first; decorative SVG `aria-hidden`; every form field labelled; admin error summary takes focus and links to fields.
- **Target size:** ≥ 48 px, answers ≥ 64 px, ≥ 8 px gaps.
- **Contrast:** values in §3.1, guarded by an automated test.
- **Motion:** §3.5. No timer in the MVP (timed play is deferred).
- **Forms:** visible labels, `autocomplete` where relevant, paste allowed in password fields, no CAPTCHA.
- **Language:** `<html lang="ms">`; English words inside content (the Bahasa Inggeris quizzes) wrapped with `lang="en"` by the question renderer when a quiz is marked as English-medium.
- **Print / low bandwidth:** CSS and JS are small, no web fonts beyond two variable files, images lazy loaded with dimensions.

## 8. Design review checklist (used before sign-off)
1. Does the page read in one sentence ("Kuiz yang rasa macam permainan")? Is there exactly one primary action per screen?
2. Is every headline two lines or fewer at 360, 768 and 1366 px?
3. Is the stone motif present at four very different scales and never replaced by another shape?
4. Is neumorphism only on surfaces and secondary controls, with text and primary actions at full contrast?
5. Does any state rely on colour alone? Any text below 4.5:1, any control below 3:1?
6. Are all tap targets ≥ 48 px and answers ≥ 64 px?
7. Does the interface still work with motion reduced and with JS failing on the homepage?
8. Is any copy generic ("seamless", "unlock", "journey") or machine-sounding? Is it natural Malay?
9. Are all empty, loading, error and unavailable states designed?
10. Admin: can a first-time admin add a 10-question quiz and publish it without help, in about ten minutes?
11. Does anything look like a template (identical card rows, centred giant headings everywhere, random decoration)?

## 9. Implementation plan

1. **Tokens first:** `resources/css/tokens.css` (all values in §3), `base.css` (reset, type, focus, motion), then components, then page CSS. Admin CSS imports the same tokens.
2. **Blade components** in `resources/views/components` for everything in §3.6; icons as inline SVG files; mascot as a component with `mood`.
3. **Pages** in the order: layout, homepage, browse, intro, player (QA first, then Stars, then Quest), result, Quizizz, static pages, error pages.
4. **Admin** after the public journey works: auth, shell, quiz form, question editor, then categories and Quizizz.
5. **Verification:** screenshots at 360, 768, 1366; console errors; Taste Skill's `inspect.mjs` run and its findings split into intentional (shadows, rounded shapes, no photographs) and real (overflow, contrast, headline wraps); axe-style checks; keyboard pass on the player.

## 10. Decisions this design makes that Yul may want to change
1. Mascot is a kancil called **Didi** (original drawing). Replaceable by commissioned art without code changes.
2. Palette is **pandan green** with pastel subject tints, deliberately not the blue/pink "kids app" default.
3. Primary buttons are solid green, not neumorphic, for contrast.
4. All three game concepts ship in the MVP.
5. Fonts: **Fredoka** (headings) and **Nunito** (body), self-hosted.
6. Level grouping for *Misi Berlevel* uses a `level_size` setting instead of a separate levels table (simplifies the PRD data model).
