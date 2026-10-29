# Prompt ChatGPT: aset Legenda yang masih perlu dijana

Prompt di bawah menutup jurang dalam [`jrpg-asset-gap.md`](jrpg-asset-gap.md): sprite bos dan latar
bersih untuk Dunia 2–5, serta musuh kecil di jalan. Prompt ditulis dalam bahasa Inggeris kerana
penjana gambar lebih tepat begitu.

## Cara guna (penting untuk konsisten)

1. Buka satu perbualan ChatGPT baharu (model gambar). **Lampirkan fail rujukan** yang disenaraikan
   bawah setiap prompt, dan satu gambar gaya: `_asset_input/Batch03/.../01_naga_chini_battle_pose_transparent_1122x1402.png`
   (bos) dan `.../02_tasik_chini_battle_background_FHD_1920x1080.png` (latar). Itulah tahap kualiti sasaran.
2. Tampal blok **GAYA BERSAMA** dahulu, kemudian prompt aset. Jana **satu gambar bagi satu mesej**.
3. Untuk setiap bos: jana **idle dahulu**, pilih yang terbaik, kemudian lampirkan idle itu sebagai
   rujukan untuk pose attack, hurt dan defeat supaya reka bentuk sama (prompt pose sudah menyebut ini).
4. **Latar lutsinar tidak boleh dipercayai** dalam ChatGPT (sering memberi corak papan dam palsu).
   Semua sprite diminta atas **latar magenta rata `#FF00FF`**; saya buang magenta itu dengan skrip
   (`story_assets.py`) dan alpha yang bersih. Jangan terima gambar dengan bayang, tanah atau kabus
   di belakang sprite.
5. Simpan fail dengan nama tepat di bawah dalam folder `_asset_input/Batch13/` dan beritahu saya.
   Saya sambungkan ke permainan dan gantikan aset sementara.

## GAYA BERSAMA (tampal sekali di awal perbualan)

```
You are generating production art for a Malaysian-folklore educational JRPG ("DIDIK Legenda").
Art direction, applied to EVERY image:
- Polished HD 2D game art in a painterly pixel-art-inspired style: crisp clean outlines, rich saturated
  colour, detailed ornament (Malay songket/woodcarving motifs, gold filigree), soft rim light, no photorealism,
  no 3D render look. Match the attached reference images exactly in finish, line weight and level of detail.
- Original designs only. No copyrighted characters. No text, letters, logos, watermarks, UI, health bars,
  frames, captions or signatures anywhere in the image.
- Fantasy inspired by regional folklore; do not claim historical accuracy.
- Battle camera: a slightly raised three-quarter front view, like a classic JRPG battle screen. The hero
  stands on the LEFT of the screen and the boss on the RIGHT, so every boss faces LEFT (toward the hero).
```

## A. Latar pertempuran bersih (4 gambar, saiz 1536×1024)

Rujukan untuk dilampirkan: konsep dunia (`Batch08…Batch11/…/01_REFERENCE_ART/*_source_concept_1536x1024.png`)
dan latar Tasik Chini Batch03 sebagai contoh gaya.

Tampal prompt ini dengan menggantikan bahagian `[WORLD]`:

```
Generate a CLEAN BATTLE BACKGROUND, 1536x1024 landscape, for the world described below. It is the empty
stage of a turn-based JRPG battle: the same raised three-quarter viewpoint as the attached Tasik Chini
background, with a large flat circular or oval arena area in the lower middle where fighters stand.
Rules:
- NO characters, creatures, enemies, bosses or silhouettes of any kind. NO UI, hearts, health bars, minimap,
  icons, text or logos.
- Keep the composition calm and readable: detail concentrated at the edges and in the distance; the centre
  of the image and the arena floor stay uncluttered so sprites read clearly on top.
- Left third: calm ground where a hero will stand. Right third: open space and a lower horizon where a
  giant boss will loom. Nothing tall in the right-middle.
- Rich lighting and depth (foreground framing leaves, background haze), consistent with the attached reference.
[WORLD]
```

| Nama fail | `[WORLD]` |
| --- | --- |
| `world_lupar_battle_bg.png` | `World: Batang Lupar. A Sarawak river at golden sunset: stilt houses and a longhouse jetty in the distance, mangrove roots, wooden walkways and torches, carved stone posts with red banners, lily pads and lotus, calm shallow river water filling the right half, warm orange and teal palette.` |
| `world_larut_battle_bg.png` | `World: Hutan Larut. Deep Malaysian rainforest: giant buttress trees, ferns, hanging vines, shafts of sunlight, mossy ruined shrine walls with carved elephant faces, a waterfall and a clear pool, a worn stone circle arena, green and gold palette.` |
| `world_kancil_battle_bg.png` | `World: Rimba Bayangan. A moonlit enchanted forest at night: a huge purple moon, gnarled twisted trees, glowing violet runes on standing stones, spirit lanterns, glowing mushrooms, a mystic circle arena with faint violet glow, deep indigo and purple palette with warm lantern accents.` |
| `world_ledang_battle_bg.png` | `World: Gunung Ledang. A sacred misty mountain sanctuary: stone steps and rope bridges between cliffs, cascading waterfalls, pink blossoms, distant pagodas on peaks, a golden lotus-pattern stone arena floating in drifting white mist, pale blue, white and soft gold palette.` |

## B. Sprite bos (4 bos × 4 pose = 16 gambar, saiz 1536×1024)

Rujukan untuk dilampirkan: gambar close-up bos (`Batch08…11/…/01_REFERENCE_ART/*_boss_closeup_REFERENCE_NOT_SPRITE.png`)
dan **sprite siap Naga Chini** (`Batch04/…/NAGA_CHINI/naga_chini_idle.png`) untuk tahap kemasan dan saiz.

Prompt asas (ganti `[BOSS]` dan `[POSE]`):

```
Generate ONE game sprite of the boss below, full body, completely visible and not cropped, centred in a
1536x1024 landscape canvas with about 8% empty margin on every side. The boss faces LEFT in a raised
three-quarter view. Background: perfectly FLAT solid magenta #FF00FF everywhere outside the creature,
with NO ground, NO shadow, NO mist, NO water, NO glow spilling onto the background and no gradient, so it
can be cut out cleanly (effects that belong to the creature, such as its own splash or aura, stay attached
to it and must not use magenta). Crisp edges. No text, UI or watermark.
[BOSS]
[POSE]
```

`[BOSS]`:

| Bos | `[BOSS]` |
| --- | --- |
| Bujang Senang (`bujang_senang`) | `Boss: BUJANG SENANG, a giant MYTHICAL CROCODILE (an animal, never a human): moss-green armoured scales, gold ornamental plates along the spine and jaw, a jewelled golden crown with a cyan gem, glowing orange eyes, vines and river weed draped on the body, huge toothed jaws, thick tail. About twice as long as it is tall.` |
| Gajah Rimba (`gajah_rimba`) | `Boss: GAJAH RIMBA, a colossal forest-guardian ELEPHANT: a hide that looks like mossy weathered stone and bark, long cream tusks with red spiral tribal patterns, a carved wooden-and-emerald crown with a green gem, golden bands and small hanging bells on the head and legs, vines and ferns growing on its back, glowing yellow-green eyes.` |
| Sang Kancil Bayangan (`kancil_bayangan`) | `Boss: SANG KANCIL BAYANGAN, a sinister slender HUMANOID illusionist inspired by the mouse-deer (kancil): a tall bipedal figure with a mouse-deer head (small pointed muzzle, very large ears, large dark glowing violet eyes, two small fang-like upper canines), NO large deer antlers, wearing layered tattered purple-black shadow robes with gold ornament, long clawed hands trailing violet smoke, floating golden crescent ornaments around the head. Elegant, mischievous and menacing.` |
| Penunggu Kabus (`penunggu_kabus`) | `Boss: PENUNGGU KABUS, an epic mountain guardian spirit made of sacred mist: a tall humanoid body of swirling white mist and teal-and-gold armour-like robes, a stern calm golden mask-like face with a tall ornate crown, huge mist hands, a gold chest medallion; wisps of white mist form its lower body. NOT a princess or goddess. Pale blue and white with gold accents.` |

`[POSE]` dan nama fail (ganti `<id>` dengan id bos di atas):

| Fail | `[POSE]` |
| --- | --- |
| `boss_<id>_idle.png` | `Pose: IDLE. Calm and imposing standing/floating pose, relaxed but dominant, looking left at the hero. Neutral breathing pose.` |
| `boss_<id>_attack.png` | `Pose: ATTACK. Use the attached idle image as the exact design reference: identical character, colours, ornaments and scale. Lunging forward-left in the middle of a powerful strike toward the hero, mouth or hands open, body leaning, dynamic and aggressive. Effects belonging to its element are allowed but must stay attached to the creature.` |
| `boss_<id>_hurt.png` | `Pose: HURT. Use the attached idle image as the exact design reference: identical character, colours, ornaments and scale. Recoiling backward to the right in pain, eyes shut or squinting, head thrown back, body twisted, small impact sparks on the body.` |
| `boss_<id>_defeat.png` | `Pose: DEFEATED. Use the attached idle image as the exact design reference: identical character, colours, ornaments and scale. Collapsed low to the ground, eyes closed, weakened and dimmed, slumped and still, much lower and wider than the idle pose.` |

Jumlah: `boss_bujang_senang_*`, `boss_gajah_rimba_*`, `boss_kancil_bayangan_*`, `boss_penunggu_kabus_*` (×4 pose).

> Catatan reka bentuk: rujukan Batch10 menunjukkan Sang Kancil Bayangan dengan tanduk emas, tetapi
> spesifikasi projek meminta jelmaan kancil berupa manusia, bukan rusa/elk. Prompt di atas sengaja tiada
> tanduk besar. Jika anda lebih suka tanduk seperti rujukan, buang frasa `NO large deer antlers` dan
> tambah `with a crown of thin golden branch-like antlers`.

## C. Musuh kecil di jalan (5 gambar, saiz 1024×1024)

Satu musuh bagi setiap dunia, kecil dan comel-mengancam (sesuai untuk kanak-kanak), boleh dikalahkan
dengan satu serangan. Gantikan "Bayang" sementara sekarang.

```
Generate ONE small enemy sprite for a children's JRPG, full body, centred in a 1024x1024 canvas with 10%
margin, raised three-quarter view, facing LEFT. Cute-but-mischievous (not scary or gory), chunky readable
silhouette, about the size of a small child. Same finish as the attached references. Background: perfectly
FLAT solid magenta #FF00FF with no ground, shadow or gradient. No text, UI or watermark.
[ENEMY]
```

| Fail | `[ENEMY]` |
| --- | --- |
| `enemy_chini_pengawal_teratai.png` | `Enemy: PENGAWAL TERATAI, a small lotus guardian spirit: a round stone-and-pink-lotus golem with a carved face and tiny arms, teal water glow.` |
| `enemy_lupar_penjaga_bakau.png` | `Enemy: PENJAGA BAKAU, a mangrove-root spirit: a squat creature of tangled mangrove roots with glowing amber eyes and a tiny lantern.` |
| `enemy_larut_roh_paku_pakis.png` | `Enemy: ROH PAKU PAKIS, a fern spirit: a leafy bush-like creature made of curled fern fronds, with bright yellow eyes and a small mossy mask.` |
| `enemy_kancil_pelita_sesat.png` | `Enemy: PELITA SESAT, a lost-lantern wisp: a floating violet paper-lantern ghost with a flickering flame, glowing eyes and a trailing ribbon tail.` |
| `enemy_ledang_bayu_kabus.png` | `Enemy: BAYU KABUS, a mist sprite: a small cloud-spirit of white swirling mist with a gold-trimmed mask face and wispy arms.` |

## D. Pilihan, jika masih ada kuota (kurang mendesak)

- **Pose hero tambahan** (Hang Jebat, Tun Teja, Puteri Saadong, Bendahara): satu set 6 pose (idle, ready,
  attack, cast, hurt, victory) di atas magenta, rujuk potret di `Batch01/…/04_BATCH_01_CHARACTER_REFERENCE`
  dan sprite hero Batch04 untuk gaya dan saiz. Tidak diperlukan untuk dua wira sedia ada.
- **Bingkai animasi**: bagi setiap bos, 2 pose "idle" tambahan (nafas masuk dan keluar) supaya gerakan
  rehat tidak sekadar tween kod.
- **Muzik**: bukan kerja ChatGPT. Gunakan alat muzik berasingan, 5 loop (satu bagi setiap dunia) dan 1 muzik bos.

## Semakan sebelum menerima setiap gambar

- Bos menghadap **kiri**, seluruh badan kelihatan, tiada bahagian terpotong.
- Latar sprite ialah **magenta rata**, tanpa bayang atau tanah.
- Tiada teks, bar nyawa, bingkai atau logo.
- Pose attack, hurt dan defeat jelas **bos yang sama** seperti idle (warna, mahkota, perhiasan).
- Latar pertempuran tiada watak atau bos, ruang kiri dan kanan lapang.
