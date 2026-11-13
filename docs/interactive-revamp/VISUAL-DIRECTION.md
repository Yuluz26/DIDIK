# DIDIK Interactive Discovery: visual direction

The standard every subject game is brought to. In order of importance:
**educational accuracy, logical gameplay, asset quality, interaction quality, visual polish, performance.**

## 1. Principles

1. **The real thing, where there is one.** A planet is its spacecraft image, a material is a photograph
   of it, a cell is a micrograph. Supporting parts of a scene that must move or change state (a switch
   blade, wires, a telescope tube, an instrument's scale) are drawn, in the materials of the real object.
2. **A game shows only what the question is about.** No planets on a question about plants. If the
   content does not suit a game, the plain way of answering is used.
3. **Cause and effect are true.** A bulb lights for a conductor, a magnet holds iron. A scene never
   rewards "the right answer" with an effect that would not really happen.
4. **Nothing gives the answer away.** Every choice is found and shown the same way. A physical result
   appears only after the answer is sent.
5. **A simulation says it is one.** Where sizes, distances or positions are not to scale, the scene
   says so in one small line.
6. **Each game is its own place.** Thirty-six scenes share parts and behaviour, not one template.
7. **Respect.** No prophet, angel or companion is pictured. Arabic text is shown exactly as written,
   in a face made for it. Historical people are not given invented portraits.

## 2. One flow in every game

**Discover → Interact → Select → Confirm → Feedback → Continue**

| Step | What the child sees |
| --- | --- |
| Discover | The scene, with a one-line instruction under it |
| Interact | Drag or tap; everything movable is also a button for the keyboard |
| Select | The chosen thing is unmistakable (gold ring, in place, locked) |
| Confirm | One button, named for the scene where that reads naturally ("Tutup suis", "Kunci sasaran" then "Semak") |
| Feedback | What really happens, then a tick or cross and the right answer if needed |
| Continue | The room's own flow (stars, next question); unchanged |

## 3. Shared conventions

- **State colours:** chosen `#ffd23f` gold ring; right `var(--good)` green ring and tick; wrong
  `var(--almost)` orange ring and cross, with "→ right answer" beside it. Never red alone: colour is
  always paired with a mark or words.
- **Targets:** at least 44 px to touch; things that sit close together get a larger invisible touch area.
- **Dragging:** `touch-action: none` only on the piece or the scene being manipulated, so the page still
  scrolls everywhere else. Pointer capture on scenes that are dragged across.
- **Keyboard:** arrow keys move a continuous control (the telescope, a knob); Enter or Space does what a
  tap does; focus is always visible.
- **Motion:** 150–350 ms for a response to input, up to 600 ms for a travel; object-specific easing (a
  blade snaps, a tube eases). Looping motion only where it carries meaning (current flowing, a star
  twinkling) and never over an answer. `prefers-reduced-motion` turns travel and loops off.
- **Sound:** the existing `play('tick' | 'pop' | 'tap')` only, so the mute setting is respected.
- **Words:** Bahasa Melayu, short, in the scene's own terms. An instruction says what to do, a finding
  says what happened and why.
- **Typography:** the app's faces (`--font-display` for names and read-outs, `--font-body` for text);
  Amiri for Arabic. No new faces.

## 4. Materials

| Material | How it is made |
| --- | --- |
| Night sky | The ESO Milky Way panorama, darkened; the same picture magnified inside an eyepiece |
| Glass | A photograph where it is the subject; otherwise layered highlights, an inner shadow and a rim |
| Metal (brass, steel) | Three-stop linear gradients across the form, a thin dark outline, a soft drop shadow |
| Bench, mat, paper, wood | Photographic textures from the library, or a mat with its printed grid |
| Photographs of things | Square tiles with rounded corners and a white edge, like specimen cards |
| Cut-outs | Real objects with their background removed (planets, a battery, a microscope) |

## 5. Assets

- Everything is hosted in `live/web/static/game-assets/<group>/<name>.webp`; nothing is loaded from
  another site while a child plays.
- `live/tools/game-assets/sources.json` lists every picture; `build.py` reads each file's licence and
  author from Wikimedia Commons, refuses anything outside public domain, CC0, CC BY and CC BY-SA,
  prepares the picture and writes `manifest.json`, `CREDITS.txt`, the size table the web uses and
  `ASSET-MANIFEST.md`.
- Pictures are sized for their place: tiles 168 px, cut-outs 280–560 px, backdrops up to 1440 px, WebP
  at quality 70–84. The whole library is loaded lazily, one game at a time.
- A game names a picture by key through `GameImage`, which reserves its space, loads lazily and shows
  a fallback (a sticker, a neutral shape) if the picture is missing or fails.
- Credits are kept in the manifest and `CREDITS.txt`, not on the game screens.
- Not used: scans of Malaysian banknotes and coins (reproduction is restricted), invented portraits of
  historical people, anything from image search, Pinterest or stock sites without a clear licence.

## 6. Meaning: the lexicon

`live/server/didik_live/lexicon.py` is the one place that says what an answer's words are: that "Marikh"
is the fourth planet, that an iron key conducts and is pulled by a magnet, that an eraser does neither.
The server uses it to decide which game a question may be played in; the web uses the generated copy to
choose the picture and the behaviour. A test keeps the copy identical.

## 7. Performance and accessibility

- Game components stay lazily loaded; a game's pictures load only when it is on screen.
- Every picture has its width and height, so nothing shifts as it arrives.
- Text over pictures sits on a dark or light plate with at least 4.5:1 contrast.
- Scenes are checked at 360 px and 390 px wide for overflow, broken pictures and page errors by the
  scripted browser used for the screenshots.
