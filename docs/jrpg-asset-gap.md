# Legenda JRPG: asset ledger and gaps

Every shipped file is in `live/web/static/story/manifest.json` (source path, size, alpha, status).
This ledger groups them and lists what an art specialist still needs to make. Licence for every row:
supplied by the DIDIK project owner in `_asset_input/` (AI-assisted art per the pack notes); the
reference images were not treated as licences for third-party characters.

**Status key**: *production* = a supplied game-ready file, converted to WebP without changing the art
(stray extraction slivers removed from poses). *derived* = interim art made here from reference images,
playable but needing replacement. *reference* = used only as a cinematic still, never as gameplay art.
*missing* = not in any pack.

| asset_id | filename | required_state | source | production_status | usage | licensing | needed_before_merge |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hero_tuah | heroes/tuah/{idle,ready,attack,cast,hurt,victory}.webp | 6 battle poses | Batch04 extracted poses | production (still poses, no in-between frames) | battle | project-supplied | no |
| hero_mahsuri | heroes/mahsuri/{…same 6}.webp | 6 battle poses | Batch04 | production (still poses) | battle | project-supplied | no |
| hero_portraits | heroes/{tuah,mahsuri}/portrait.webp | select / HUD portrait | Batch03 full-body poses | production | hero select, HUD face | project-supplied | no |
| boss_chini | bosses/chini/{idle,attack,special,hurt,defeat}.webp | 5 boss states | Batch04/06 poses | production (still poses) | boss and road "Bayang" enemy | project-supplied | no |
| boss_chini_reveal | bosses/chini/reveal.webp | reveal | Batch03 | production | boss reveal | project-supplied | no |
| boss_lupar / larut / kancil / ledang | bosses/{key}/idle.webp | idle, attack, hurt, defeat | Batch08–11 close-up references, SAM cut-out | **derived**: one pose each; attack/hurt/defeat are played in code (lunge, flash, shake, sink). Edges and hidden parts (crocodile's body, elephant's feet) are approximate | boss and road enemy | project-supplied | recommended |
| bg_chini | worlds/chini/battle.webp | clean battle background | Batch03 | production | battle, travel | project-supplied | no |
| bg_lupar / larut / kancil / ledang | worlds/{key}/battle.webp | clean battle background | Batch08–11 1536×1024 concepts | **derived**: painted HUD, small characters and painted boss filled with a soft colour field, cropped 16:9, softened; the boss sprite covers the filled area | battle, travel | project-supplied | recommended |
| reveal_lupar … ledang | worlds/{key}/reveal.webp | reveal still | Batch08–11 close-ups | reference (cinematic still only) | boss reveal | project-supplied | no |
| fx_elements | fx/{api,angin,petir,tanah,air}.webp | burst per element | Batch05 | production (single stills, tweened) | attack burst, projectile | project-supplied | no |
| fx_sheets | fx/{el}_sheet.webp | impact frames | Batch02 12-frame sheets | production (real frame animation) | impact on target | project-supplied | no |
| fx_transition | fx/transition_4x3.webp | world wipe | Batch12 12 alpha frames | production | world intro | project-supplied | no |
| ui_elements | ui/element_{el}.webp | icons | Batch02 | production | element picker, unlock | project-supplied | no |
| ui_hearts | ui/heart_{full,half,empty}.webp | half-heart states | Batch02 | production | HUD | project-supplied | no |
| ui_symbols | ui/symbol_{key}.webp | world emblems | Batch12 | production | intro, clear, host map, game picker | project-supplied | no |
| sfx | audio/*.wav | battle sounds | Batch12 synth demos | demo quality | feedback sounds | project-supplied | before public release |
| road_enemies | — | 5 minion designs (one per world) | missing | **missing**: road enemies are drawn as a tinted "Bayang" (shadow) of the world's boss | road battles | — | recommended |
| hero_roster | — | Hang Jebat, Tun Teja, Puteri Saadong, Bendahara poses | Batch01/02 portraits only | **missing** battle poses (portraits are references) | hero select | — | no (two heroes ship) |
| boss_frames | — | per-state animation frames for all bosses | missing | **missing**: every boss and hero animates by switching still poses plus code tweens | battle | — | no |
| music | — | world music | missing | **missing** | ambience | — | no |

## Not used in the game, on purpose

- Batch07 story frames, Batch08–11 chapter-intro and boss-reveal compositions, Batch03/05/06 composite
  battle previews, the Batch12 five-world board: they have UI text or HUD painted in. The game renders
  those texts and HUDs itself.
- Batch02 tiny scenery/boss crops (≈300×130 px): too small.
- MP4 animatics (Batches 06–12): still-image pans, not gameplay; not shipped.
- Batch02 `bayangan` FX reference: there is no sixth element.
- The Batch08 concept shows Bujang Senang as a crocodile; the Batch02 reference showing a human is not used.
