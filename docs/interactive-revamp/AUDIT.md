# DIDIK Interactive Discovery: audit of the 36 subject games

Audited on the `claude/interactive-revamp` branch, cut from `14d4c48`. The subject games had not changed
since they were first written (no commits touch `live/web/src/lib/subjects/` after `67e136c`).

## 1. How the games are built today

- **Registry:** `live/web/src/lib/subjects/games.ts` (36 games, lazy loaders) and
  `live/server/didik_live/games.py` (the same keys, the question types each plays, and `deal_games`,
  which gives a quiz's questions to a subject's games in "Makmal Sains", "Ekspedisi Sejarah" and
  "Cahaya Ilmu"). A test keeps the two lists the same.
- **Contract:** every game is a Svelte component taking `GameProps` (`question`, `disabled`, `mine`,
  `reveal`, `onanswer`) and sends exactly what its question type's plain answer component sends. The
  server checks the answer; a game never knows the right answer before `reveal` arrives.
- **Shared engines:** `OrderPlay` (order), `SortPlay` (sort), `MatchPlay` (match), `LabelBoard`
  (diagram), with `Slots` and `Pairs` state in `kit.svelte.ts` and tap-or-drag in `questions/drag.ts`.
- **Pictures before this work:** 259 Fluent Emoji 3D stickers and 19 diagrams in `static/rajah`. Every
  game scene was drawn with CSS gradients and a little inline SVG; the things in a scene (planets,
  materials, animals, artefacts) were emoji stickers or coloured circles. There was no photograph or
  scientific image inside any game except the diagrams being labelled.

## 2. Problems found across the set

| Problem | Where | Fix |
| --- | --- | --- |
| Scenes are CSS shapes and emoji, so nothing looks like the real thing | all 36 | A local library of real pictures (`static/game-assets`), each with a verified source and licence |
| A game is given to any question of its type, whatever it is about | `deal_games`, and `question.game` set by an author | A shared lexicon says what an answer's words are; a game is used only for content it can show truthfully (`games._suits`, `games.game_for`), else the plain way of answering |
| Teropong showed "planets" (coloured glows) for answers about anything | Teropong | Only for answers that are all things in the sky; each shown as its real image |
| Orbit put any ordered list on "orbits" | Orbit | Only for planets in their true order from the Sun |
| Litar lit its bulb for "the right answer", whatever was in the gap | Litar | The bulb lights only for something that conducts; the lexicon knows what does |
| Magnet put "the first group" on the magnet, whatever it was | Magnet | Only for a magnetic / not magnetic sort whose things are known; attraction follows the material |
| Jirim drew solid, liquid and gas jars for any group names | Jirim | Only when the groups are states of matter |
| Kitaran drew a cycle for any ordered list | Kitaran | Only for stages the lexicon knows as a cycle |
| Unsur drew periodic-table tiles for any left-hand words | Unsur | Element tiles only for elements (with their real numbers); else a materials card or the plain way |
| Kiblat's needle implied a real direction for any choices | Kiblat | True bearings only when every choice is a direction; otherwise it is plainly a dial of choices |
| Stickers guessed from a word could be wrong (an early build showed a book for "buku lali") | OrderPlay, SortPlay pools | Games name their own pictures from the lexicon; the sticker guess is only a fallback |
| A few scenes overflowed small phones | fixed earlier for 320px | Kept under test for every revamped scene (360px and 390px) |
| No way to see every state of every game | dev gallery | `?g=<game>&state=right|wrong|host` in `/gaya/subjek`, and a scripted phone browser for screenshots and play-through |

Nothing in the audit found the correct answer leaking before submission. The revamp keeps it so: where a
scene behaves physically (a bulb, a magnet, a balance), it reacts only after the answer is sent.

## 3. Game by game

Priority: **P** pilot, **1** high (concept was misleading or the scene weakest), **2** medium.
Complexity: S small, M medium, L large.

### Sains

| Game (component, type) | Before | Problems | Revamp | Pri / size |
| --- | --- | --- | --- | --- |
| Makmal Ramuan (`sains/Ramuan`, single/multiple) | CSS bottles and beaker, tap to pour, colour mix | Glass and liquid are flat gradients; "reaction" is decorative | Real laboratory glassware photographs, liquid that pours and settles, reaction shown only after checking | 2 / M |
| Teropong Angkasa (`sains/Teropong`, single) | CSS star dots, a ring "lens", emoji or colour glows for answers | Not astronomy; shown for any question; nothing real | Real Milky Way panorama, eyepiece that truly magnifies it, NASA/ESA/ESO images that come into focus, a telescope that follows the aim, lock then check; astronomy-only | P / L |
| Orbit Planet (`sains/Orbit`, order) | Gradient "planets" on dashed half-ellipses | Colours stand in for planets; used for any list | Real Sun (SDO), true circular orbits, real planet images; only planets in order from the Sun; "not to scale" stated | P / M |
| Tubuh Manusia (`sains/Tubuh`, diagram) | LabelBoard with an X-ray tint and scan line | Good base (real anatomical drawings) but little sense of an instrument | Light-box presentation, organ highlight on the place being labelled; body diagrams only | 2 / S |
| Rantai Makanan (`sains/Rantai`, order) | Stickers up a green gradient | Emoji animals; never dealt automatically | Real photographs of each organism, habitat backdrop chosen by the chain (field or sea), energy arrows; dealt when every link is a known organism | 1 / M |
| Litar Elektrik (`sains/Litar`, single) | CSS battery and bulb; bulb lit for the right answer | Physics wrong: any right answer "lit" the bulb | Photographed battery, bulb and materials on a bench mat, knife switch, crocodile clips, current animation; bulb follows conductivity; conductivity questions only | P / L |
| Magnet Ajaib (`sains/Magnet`, sort) | CSS horseshoe with SVG arcs | First group always "sticks" | Real field-line diagram and object photographs; after checking, magnetic things cling and others fall away, by material | 1 / M |
| Balang Jirim (`sains/Jirim`, sort) | CSS jars with blocks, waves, bubbles | Used for any groups | Real glass jars and photographs of each substance; states of matter only | 1 / M |
| Roda Kitaran (`sains/Kitaran`, order) | SVG arrows round a ring, stickers | Any list became a "cycle" | Real photographs of each stage (frog, butterfly, water, Moon phases from the LRO image); known cycles only | 1 / M |
| Mikroskop (`sains/Mikroskop`, diagram) | A round frame round a cell drawing | No instrument, no focusing, no real cell | Photographed microscope, a focus knob that must be turned before labelling, a real onion-cell micrograph added to the diagram library | P / M |
| Jadual Berkala (`sains/Unsur`, match) | Gradient tiles with a made-up number | Numbers were positions in the list, not atomic numbers; used for any pairs | Real atomic numbers, families and a mini table showing where each element sits; elements only | 1 / M |
| Alat Pengukur (`sains/Alat`, number) | CSS thermometer, cylinder, ruler, balance | Scales correct but flat | Precisely drawn instruments with glass and metal, a meniscus, engraved scales; units and ranges unchanged | 2 / M |

### Sejarah

| Game (component, type) | Before | Problems | Revamp | Pri / size |
| --- | --- | --- | --- | --- |
| Gali Artifak (`sejarah/Gali`, single) | Gradient soil squares, stickers | No real site or finds | Photographed excavation ground and tools; finds shown as real artefacts where the answer names one, else as an inscribed find-tag | 1 / M |
| Bina Empayar (`sejarah/Empayar`, order) | CSS palace floors | Invented architecture | Timber and stone from photographs, the Malacca Sultanate Palace museum as the finished building | 2 / M |
| Garis Masa (`sejarah/GarisMasa`, order) | Gradient ledger and rope | Dates buried in text | Archive paper, dates lifted from each event onto a stamped tag | 2 / S |
| Peta Nusantara (`sejarah/Peta`, diagram) | LabelBoard with a parchment tint | Thin | Old-map presentation with a real compass rose; maps and places only | 2 / S |
| Kurator Muzium (`sejarah/Muzium`, sort) | CSS cases | Emoji artefacts | Museum gallery photograph, glass cases, real artefact photographs where known | 1 / M |
| Skrol Purba (`sejarah/Skrol`, blank) | CSS parchment and wax blobs | Flat | Real parchment, wax seals, ink that soaks in | 2 / S |
| Pelabuhan Melaka (`sejarah/Pelabuhan`, match) | CSS sea and hulls | No history in it | A historical view of Malacca's harbour, period ships | 1 / M |
| Siapakah Aku? (`sejarah/Siapa`, single) | Curtained frames with name plates | Fine in principle (no invented faces) | Real gilt frames and gallery wall; still no portraits unless verified | 2 / S |
| Hierarki Istana (`sejarah/Istana`, order) | CSS pyramid | Generic | Tiered dais of a balairung, rank by height | 2 / S |
| Arkib Negara (`sejarah/Arkib`, truefalse) | CSS card and stamps | Flat | Aged paper, real rubber stamps and ink | 2 / S |
| Mesin Masa (`sejarah/MesinMasa`, number) | CSS brass and a conic "vortex" | No history shown | Clockwork from photographs; the window shows the era the wheels are set to (never the answer) | 2 / M |
| Mesin Taip Merdeka (`sejarah/MesinTaip`, text) | CSS typewriter | Flat | A photographed typewriter, type that strikes the paper | 2 / M |

### Pendidikan Islam

| Game (component, type) | Before | Problems | Revamp | Pri / size |
| --- | --- | --- | --- | --- |
| Warna Tajwid (`islam/Tajwid`, sort) | CSS page, Amiri type | Sound; plain | Mushaf-style page and border; text handling untouched | 2 / S |
| Huruf Hijaiyah (`islam/Hijaiyah`, single) | Gradient "wood" | Flat | Real timber board, carved letters | 2 / S |
| Langkah Wuduk (`islam/Wuduk`, order) | Body-part stickers | Emoji body parts | Clear step illustrations and running water | 1 / M |
| Gerakan Solat (`islam/Solat`, order) | Faceless SVG figures | Sound; plain | Prayer mat and mosque floor from photographs; figures kept faceless | 2 / S |
| Kompas Kiblat (`islam/Kiblat`, single) | CSS compass | Could be read as a real Qibla finder | Brass compass; states plainly that it is a dial of answers unless the choices are directions | 1 / M |
| Langit Waktu Solat (`islam/Waktu`, match) | Gradient skies | Not real skies | Photographs of the sky at dawn, morning, noon, afternoon, sunset and night | 1 / M |
| Tiang Rukun (`islam/Rukun`, multiple) | CSS pillars | Flat | Stone columns and arch | 2 / S |
| Neraca Amal (`islam/Timbangan`, sort) | CSS balance | Could be read literally | Brass balance; labelled as a way of sorting, not a measure of deeds | 2 / S |
| Peta Hijrah (`islam/Hijrah`, order) | Coloured map, emoji camel | Thin | Relief map of the Hejaz and the route | 1 / M |
| Lentera Tugas (`islam/Malaikat`, match) | CSS lanterns | Flat | Photographed lanterns that light; no figures | 2 / S |
| Tabung Zakat (`islam/Zakat`, money) | Shared money UI | Money is drawn | Ringgit kept as clear illustrations (see the manifest: banknote scans are not used) | 2 / S |
| Kafilah Sirah (`islam/Kafilah`, single/truefalse) | Gradient dunes, emoji camels | Emoji | Photographed desert and a caravan | 1 / M |

## 4. Game-to-question assignment

`deal_games` gave each question the least-used game of its type. Only nine games had a content check.
After the revamp every game that shows something particular has one, read from the shared lexicon
(`live/server/didik_live/lexicon.py`, copied for the web by `python -m didik_live.lexicon`):

- a question the author gave a game (`question.game`) keeps it only if it suits it (`games.game_for`,
  applied when the question is presented, so old quizzes are never refused);
- a question no game suits is played the plain way, which already has its own hands-on components.

The status of each game is tracked in the final report (`REPORT.md`).
