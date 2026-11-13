# DIDIK Interactive Discovery: final report

Branch `claude/interactive-revamp`, cut from `14d4c48`. Not merged, not deployed.

## 1. What changed, in short

- **A real picture library.** 172 pictures (4.0 MB in all), every one from Wikimedia Commons, each with
  its licence and author read from the file's own page by `live/tools/game-assets/build.py`, which
  refuses anything outside public domain, CC0, CC BY and CC BY-SA. Hosted locally, lazily loaded, sized
  for phones. Record: `ASSET-MANIFEST.md`, `live/web/static/game-assets/manifest.json` and `CREDITS.txt`.
- **A lexicon of meaning** (`live/server/didik_live/lexicon.py`, copied for the web): what an answer's
  words are. Planets and their order from the Sun; materials with whether they conduct, are magnetic and
  their state; living things and where they live; stages of six cycles; 32 elements with real atomic
  numbers and places; historical artefacts, places and events; places of the Sirah; the sky through the
  day.
- **Games shown only where they are true.** `games.game_for` (applied when a question is presented) and
  `deal_games` now give a game only to content it can show truthfully: Teropong only for things in the
  sky, Orbit only for planets in their true order, Litar only for a conductor-versus-insulator question,
  Magnet only when every thing's material is known and in the right group, Jirim only for states of
  matter, Kitaran only for a known cycle, Rantai only for living things, Jadual Berkala only for
  elements. Anything else is played the plain way. Nothing is refused: older quizzes keep working.
- **Physics that follows the material, not the answer.** Litar's bulb lights only for a conductor;
  Magnet holds iron and steel and lets the rest fall, after the answer is sent.
- **No new way to give an answer away.** Where some choices would have a photograph and others not
  (Gali, Ramuan), photographs are used only if all of them have one.

## 2. Game by game

**Revamped** means a new scene and interaction; **upgraded** means real pictures and meaning added to
the existing play; **little change** is said plainly.

### Sains

| Game | Status | What changed |
| --- | --- | --- |
| Teropong Angkasa | Revamped (pilot) | Real Milky Way sky; an eyepiece that magnifies it; NASA/ESA/ESO images that come into focus near the cross-hairs; telescope tube that follows the aim; read-out of what is in focus; "Kunci sasaran" then Semak; keyboard arrows; astronomy questions only |
| Orbit Planet | Revamped (pilot) | Real Sun (SDO) and planets, true circular orbits, one place per orbit; planets in order from the Sun only; "not to scale" |
| Litar Elektrik | Revamped (pilot) | Photographed battery, bulb and materials on a bench mat; knife switch that closes; crocodile clips; current that flows only through a conductor; a finding that says why |
| Mikroskop | Revamped (pilot) | Photographed Leitz microscope; a focus knob that must bring the specimen sharp before labelling; a real onion-cell micrograph added to the diagram library and used in the samples |
| Rantai Makanan | Upgraded | Real photograph of each organism; a paddy field or open sea behind the chain; now dealt to living-thing chains |
| Roda Kitaran | Upgraded | Real photograph of each stage; Moon phases drawn on the real Moon; the Earth or the Sun at the hub where it belongs; known cycles only |
| Magnet Ajaib | Upgraded | Real field-line diagram; photographed objects; after checking, magnetic things cling and the rest fall; magnet questions only |
| Balang Jirim | Upgraded | Photographed substances; each jar marked by a real example; states-of-matter groups only |
| Jadual Berkala | Revamped | Real atomic numbers, symbols, families in colour and a small map of the table showing where each element sits; elements only |
| Makmal Ramuan | Little change | Photo labels on the bottles when every bottle's contents are known; otherwise as before |
| Tubuh Manusia | Little change | Already used real anatomical drawings on an X-ray light box |
| Alat Pengukur | Little change | Instruments, units and ranges were already correct; not redrawn |

### Sejarah

| Game | Status | What changed |
| --- | --- | --- |
| Gali Artifak | Upgraded | Real excavation soil, a real trowel, artefact photographs when every find has one |
| Bina Empayar | Upgraded | The reconstructed Malacca Sultanate Palace behind the building site, named |
| Garis Masa | Upgraded | A photograph pinned to each event card (A Famosa, Stadthuys, Stadium Merdeka…) |
| Kurator Muzium | Upgraded | Artefact photographs (keris, tempayan, gendang gangsa, Batu Bersurat…) in the cases and the pile |
| Skrol Purba | Upgraded | Real parchment under the writing |
| Pelabuhan Melaka | Upgraded | Real junk and carrack pictures for Chinese and European traders; spice-route map behind the wharf |
| Siapakah Aku? | Upgraded | Gallery wall; still no portraits of real people |
| Hierarki Istana | Upgraded | A real throne at the top; the palace behind |
| Arkib Negara | Upgraded | Real archive shelves behind the desk |
| Mesin Masa | Upgraded | Real clockwork turning behind the wheels |
| Mesin Taip Merdeka | Revamped | A real Underwood typewriter that jolts with each key |
| Peta Nusantara | Little change | Already labels real maps |

### Pendidikan Islam

| Game | Status | What changed |
| --- | --- | --- |
| Langit Waktu Solat | Revamped | A photograph of the sky at each prayer time (fajar, pagi, tengah hari, petang, senja, malam) |
| Peta Hijrah | Upgraded | Real photographs of Makkah, Gua Thur, Quba and Madinah at each stop; a real camel |
| Lentera Tugas | Upgraded | Real fanous lanterns, dark until a duty is hung, then lit; no figures |
| Kafilah Sirah | Upgraded | The real Rub' al Khali and a real camel caravan |
| Gerakan Solat | Upgraded | A real prayer rug and mihrab; the figures stay faceless outlines |
| Tabung Zakat | Upgraded | A real mosque donation box (from Semporna); ringgit still drawn, not scanned |
| Neraca Amal | Upgraded | A real balance, and a line saying it is a way of sorting, not a measure of deeds |
| Tiang Rukun | Upgraded | Masjid Sultan Salahuddin Abdul Aziz behind the colonnade |
| Kompas Kiblat | Upgraded | A line saying when the dial is only a way of choosing, and that real Qibla direction depends on where one stands |
| Huruf Hijaiyah | Upgraded | Real arabesque carving as the board |
| Warna Tajwid | Little change | Arabic and colouring untouched (a rehal photograph was tried and removed: it read as a blurred hand) |
| Langkah Wuduk | Little change | Kept its body-part stickers; photographs of a person washing were not used |

## 3. Assets and licences

172 pictures: CC BY-SA 84, Public domain 39, CC BY 38, CC0 10, "Attribution" 1.
Full table: `ASSET-MANIFEST.md`. Three files had no author on their page; the uploader is credited
instead, as Commons does. Not used: banknote and coin scans, invented portraits, anything whose licence
could not be read from its page, GFDL-only files (Quba and Masjid Nabawi used CC BY-SA and CC0 photos
instead). Credits are not shown on screen, as asked; they are in the manifest and `CREDITS.txt`.

## 4. Answer contract and safety

- `GameProps` and every answer payload are unchanged; the server still checks every answer.
- Nothing reveals the right answer before it is sent. Physical results (bulb, magnet) appear after.
- Sample changes: one Litar question in Sains Tahap 2 became a conductor question (it was about which
  part supplies energy, which a bulb cannot show); the Sains Menengah Mikroskop question now uses the
  onion micrograph; the Sains Tahap 1 Jadual Berkala question now matches elements to their uses.

## 5. Tests and checks

| Check | Result |
| --- | --- |
| Server tests (`pytest`) | 313 passed |
| New tests | lexicon copy identical; games refused for content they would misrepresent (8 games); every sample question keeps its game; picture library complete, licensed, matching the lexicon and size table |
| `svelte-check` | 0 errors, 0 warnings |
| Production build | passes |
| Scripted play (`live/tools/visual-check/playall.mjs`) | all 36 games played by tapping and answered |
| Screenshots, 390 px, play / right / wrong / host | 144 taken; one overflow found (Kitaran's turning ring) and fixed |
| Screenshots, 360 px | no overflow, no broken picture, no page error |

Before-and-after sheets: `screenshots/sains-1.jpg` … `screenshots/islam-2.jpg`.

## 6. Remaining limitations

- Six games changed little (listed above). Alat Pengukur and Wuduk are the most worth a further pass.
- "Upgraded" games keep their existing play; they gained real material and truthful assignment, not
  new mechanics.
- Kompas Kiblat is not a location-based Qibla finder and says so.
- The lexicon knows the words in the samples and common school vocabulary; a quiz written with other
  words is played the plain way rather than wrongly.
- Some photographs are of places outside Malaysia standing for a kind of thing (a balance, a lantern,
  a typewriter); none stands for a specific Malaysian object it is not.
- Not verified in a live multiplayer room after the last changes; the room tests pass and the gallery
  plays every game.
