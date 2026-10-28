# Legenda JRPG: asset ledger and gaps

Every shipped file is in `live/web/static/story/manifest.json` (source path, size, alpha, status). This
ledger groups them and lists what an art specialist still needs to make. Licence for every row: supplied
by the DIDIK project owner in `_asset_input/` (AI-assisted art per the pack notes); the reference images
were not treated as licences for third-party characters.

The battlefield of each world is the supplied painting itself (`_asset_input/Battlefields/`): the game
keeps its composition (the hero's path on the left, the boss's arena on the right, the title plate and the
minimap) and lays the live HUD over the places where the painting had its own.

**Status key**: *production* = a supplied game-ready file, converted to WebP without changing the art.
*cut from painting* = made from a supplied painting at its native detail, with the surrounding scene filled
in behind it. *missing* = not in any pack.

| asset_id | filename | required_state | source | production_status | usage | needed_before_merge |
| --- | --- | --- | --- | --- | --- | --- |
| battlefield_1..5 | worlds/{chini,lupar,larut,kancil,ledang}/field.webp | clean backdrop | the five supplied battlefield paintings | **cut from painting**: boss, hero, small enemies, hearts, boss panel and element row filled with the colours around them (Telea inpainting for the small characters, soft colour fill for the boss). The path patches are visible if you look closely; the live hero and enemies cover most of them | backdrop for every scene of the world | recommended: a clean repaint without characters |
| boss_1..5 | worlds/{key}/boss.webp | boss, drawn over the field where it stands | the same paintings, SAM cut-out | **cut from painting**: ONE pose each. Idle breathing, hit recoil, lunge and defeat are made in code. Parts hidden behind the painting's foreground are missing, so the boss can only move a little | boss | recommended: attack, hurt and defeat poses |
| minion_a / minion_b (x5) | worlds/{key}/minion_*.webp | two small enemies per world | the same paintings, SAM cut-out | **cut from painting**: small (about 100 px), shown about 1.5 times larger | road enemies, taking turns | recommended: larger redraw |
| hero_tuah | heroes/tuah/{idle,ready,attack,cast,hurt,victory}.webp | 6 battle poses | Batch04 extracted poses | production (still poses, no in-between frames); painted larger and in a different finish than the paintings' small chibi heroes | battle | no |
| hero_mahsuri | heroes/mahsuri/{...same 6}.webp | 6 battle poses | Batch04 | production (still poses) | battle | no |
| hero_portraits | heroes/{tuah,mahsuri}/portrait.webp | select / HUD portrait | Batch03 full-body poses | production | hero select | no |
| fx_elements | fx/{api,angin,petir,tanah,air}.webp | burst per element | Batch05 | production (single stills, tweened) | attack burst, projectile | no |
| fx_slash | fx/{el}_slash.webp | attack effect, 12 frames | Effects60 pack (`_asset_input/Effects60/04_ATTACK_FRAMES`) | production art, AI-generated frames cut from contact sheets (neighbour bleed removed, native 314 x 418 per frame; some frames are cut flush with their cell, so the edges are feathered in code) | attack on the boss or enemy, counterattack on the hero | no |
| fx_transition | fx/transition_4x3.webp | world wipe | Batch12 12 alpha frames | production | world intro | no |
| ui_elements | ui/element_{el}.webp | icons | Batch02 | production | element dock, unlock | no |
| ui_hearts | ui/heart_{full,half,empty}.webp | half-heart states | Batch02 | production | HUD | no |
| ui_symbols | ui/symbol_{key}.webp | world emblems | Batch12 | production | boss panel, intro, clear, host map, game picker | no |
| sfx | audio/*.wav | battle sounds | Batch12 synth demos | demo quality | feedback sounds | before public release |
| hero_roster | none | Hang Jebat, Tun Teja, Puteri Saadong, Bendahara poses | Batch01/02 portraits only | **missing** battle poses (portraits are references) | hero select | no (two heroes ship) |
| boss_poses | none | attack, hurt and defeat drawings for the five bosses | missing | **missing**: only one pose per boss exists | battle | no |
| music | none | world music | missing | **missing** | ambience | no |

## Not used in the game, on purpose

- The earlier Batch 8 to 11 reference close-ups and Batch 13 ChatGPT prototypes (`_asset_input/Batch13*`):
  low native detail (about 380 px upscaled), a boss design that differs from the battlefield paintings, a
  pose that shows a different character (Penunggu Kabus "hurt"), and vector drafts for Sang Kancil Bayangan
  and the enemies. Kept in the repository as reference only.
- Batch07 story frames, chapter-intro and boss-reveal compositions, the Batch03/05/06 composite battle
  previews, the Batch12 five-world board: they have UI text or HUD painted in.
- Batch02 tiny scenery/boss crops (about 300 by 130 px): too small.
- MP4 animatics (Batches 06 to 12): still-image pans, not gameplay.
- Batch02 `bayangan` FX reference: there is no sixth element.
- Sang Kancil Bayangan keeps the antlers of the supplied painting, although the written brief asks for an
  antlerless humanoid; the painting was chosen as the visual target.
