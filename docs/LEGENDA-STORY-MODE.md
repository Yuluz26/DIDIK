# Legenda: Story Mode (JRPG)

Five Malaysian folklore worlds as a turn-based JRPG, played with any parent quiz of 10 or more
questions. Parents only write the quiz and choose **Legenda → Solo** (one child) or **Party** (a room
for friends) on the game picker. There is nothing else to set up: no maps, bosses or HP to configure.

Children never walk, steer or dodge. The hero travels on their own; every enemy on the road opens a
battle; the child answers questions, chooses an element at the boss, and watches the attack (right
answer) or the counterattack (wrong answer) the server has decided.

## Flow (one child, `Seat.step` on the server)

```
select → intro → travel → encounter → question → result → clear → travel …   (5 enemies)
       → unlock → gather → reveal → question → result → (wait) → …            (5 boss hits)
       → worldclear → intro (next world) … → victory
fallen (hearts at 0) → Cuba lagi → back to the same checkpoint
```

| World | Boss | Weak to |
| --- | --- | --- |
| 1. Tasik Chini | Naga Chini | Petir |
| 2. Batang Lupar | Bujang Senang (a crocodile) | Api |
| 3. Hutan Larut | Gajah Rimba | Angin |
| 4. Rimba Bayangan | Sang Kancil Bayangan | Tanah |
| 5. Gunung Ledang | Penunggu Kabus | Air |

The worlds and bosses are fantasy inspired by regional folklore, not claims about the legends.

## Rules (all decided in `live/server/didik_live/game/modes/legenda.py`)

- **Hearts**: six, counted in halves (12). Right answer +½ (never above six). Wrong answer: an
  unavoidable attack, −1½.
- **Road**: five enemies per world. A wrong answer does **not** clear the enemy: it attacks, and the
  child gets a different question for the same enemy.
- **Elements**: after the fifth enemy, Api, Angin, Petir, Tanah and Air unlock. The child picks one
  before each boss answer. The element only changes the animation and gives +50 bonus points on the
  boss's weakness; it never changes correctness or damage.
- **Boss**: five bars. Each right answer removes exactly one bar; a wrong answer never does.
- **Falling** keeps the checkpoint: cleared enemies, unlocked elements and the damage the boss has
  already taken. Hearts refill to six.
- **Questions**: each child has their own shuffled deck of the whole quiz, reshuffled when it runs out.
  A question never returns within three turns of itself, and options are reshuffled each time, so ten
  questions carry all fifty battles.
- **Party**: every child keeps their own hearts, hero and element. At the boss gate they wait (up to
  60 s) for friends still on the road in the same world, then fight one shared boss. The fight runs in
  rounds: one question per child per round, and the next round opens when everyone online in the fight
  has answered (or after 45 s). A fast child cannot finish the boss alone. Friends who arrive later join
  the fight in progress; if the boss already fell, they get a fight of their own.
- **Safety**: answer keys never reach the browser before checking. Every step bumps the seat's `ev`; a
  `next`/`answer` naming an older `ev` (double taps, stale messages after a reconnect) is ignored. The
  game is saved with the room and survives a server restart.

Scores: road win 100, boss hit 150 (+50 on the weakness), world cleared 300. The ending is a co-op
celebration (no podium ranks).

## Front end

`live/web/src/lib/games/legenda/`

| File | Role |
| --- | --- |
| `LegendaPlayer.svelte` | Child's screen. After the hero is chosen the whole screen is the game (`.arena`, fixed; the browser's full screen is asked for at the tap that chooses the hero, with a button to toggle it). It chooses the scene for the step, plays cinematics and auto-advances (with Teruskan/skip). **The question is a popup over the scene, shrunk to fit the viewport (no scrolling, the scroll bar is hidden)**, never a panel beside it: it holds the question, the answer controls for all eight types and, at the boss, the five-element picker (Alt+1 to Alt+5; plain digits already answer questions). While the attack or counterattack plays the popup steps aside; a wrong answer brings it back with the right answer shown, a right one shows a small toast. |
| `Stage.svelte` | The battlefield. The supplied painting of the world is the backdrop; the hero, the boss and the two small enemies are layers laid exactly where the painting had them (`layout.ts`), and the live HUD (six half-hearts, boss name and five bars, the five elements) sits where the painting had its own. Attack and counterattack timelines (Web Animations API): the hero gathers, slides in (or casts), the element's **12 effect frames play one by one on the target** (about 12 fps, edges feathered), the target reacts, the hero retreats. A wrong answer plays the enemy's strike on the hero with the same frames, mirrored. **The hero holds the weapon of the element the server has confirmed** (`weapon` prop, from `story.element` once `story.elements` is true): idle, ready, attack and cast show that weapon sprite, hurt and victory show the base pose, and a missing file falls back to the base sprite. Flash, shake, pop-ups. The HUD keeps the old number until the hit lands. |
| `Banner.svelte`, `banners.ts` | The transition text banners ("Jawapan Betul!", "Boss Akan Menyerang!"...), shown over the scene at the server-confirmed moments: world intro, enemy appears, right and wrong answers, the enemy's counterattack and lost heart, element picking and unlock, boss reveal and defeat, retry, victory. Six are 12-frame animations; with reduced motion all are still. The words are also in the page for screen readers. |
| `Particles.svelte` | Canvas motes per world and hit sparks. |
| `HeroSelect.svelte`, `LegendaHost.svelte` | Hero choice; host big screen (five worlds, every child's place and hearts, live boss bars). |
| `data.ts`, `layout.ts`, `sfx.ts` | Art paths and per-world tuning; positions generated from the paintings; supplied battle sounds. |

Reduced motion: no particles, shake or looping sprite motion; cinematics are shortened. Every screen
has the full-screen button (beside the sound button) where the browser supports it.

Art review without a room: open `/gaya/legenda?world=0..4&step=...` (any step, either hero, plus
buttons that play every element's attack and the counterattack).

## Art pipeline

The five battlefields come from the paintings in `_asset_input/Battlefields/`. `live/web/scripts/story_assets.py`
cuts the boss and the two small enemies out of each painting with SAM (masks cached in
`Battlefields/masks/`), fills the places the game now draws live (hearts, boss panel, element row, and
the painted hero and enemies) with the surrounding colours, and writes `layout.ts`. Heroes, effects,
icons, emblems and sounds are converted from the other packs. `static/story/manifest.json` lists every
file with its source and status. What is production-ready and what is interim: see
[`jrpg-asset-gap.md`](jrpg-asset-gap.md).

## Tests

```sh
cd live/server && .venv/Scripts/python -m pytest tests/test_legenda.py   # or: pytest
cd live/web && npm run check && npm run build
```

`tests/test_legenda.py` covers: 10-question minimum and all eight question types; a full solo world
from hero choice to world clear; heart arithmetic and the cap; wrong boss answers never hurting the
boss; falling and the checkpoint; a full five-world campaign on ten questions with the anti-repeat
rule; no answer keys in the phone's view; double-tap protection; the party gate, shared rounds and a
friend disconnecting; late friends joining a fight; save/restore mid-boss; practice bots; solo rooms
holding one child.
