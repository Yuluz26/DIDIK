# DIDIK — Batch 05 HD Elemental Attack Assets

Batch ini mengandungi **7 imej HD asal**, tanpa upscale atau pemampatan semula fail asal:

- **5 visual FX serangan elemen PNG telus:** Api, Angin, Petir, Tanah, Air.
- **2 battle-scene concept references:** Hang Tuah vs Naga Chini, Mahsuri vs Naga Chini.
- `03_PREVIEWS/contact_sheet.jpg` untuk rujukan pantas.
- Manifest JSON/CSV dan panduan integrasi.

## Saiz asli
- Setiap FX: **1254 × 1254 px**, PNG RGBA dengan alpha sebenar.
- Setiap battle reference: **1672 × 941 px**, PNG RGB.

## Penting: jujur tentang status aset
Semua FX ialah **imej statik tunggal**, bukannya video, GIF, animated sprite sheet atau 12-frame animation. Boleh dijadikan lapisan VFX dan dianimasikan (opacity/scale/rotate/motion/particles) oleh engine; untuk animasi penuh perlukan frame tambahan atau kerja motion design.

Kedua-dua battle scenes ialah **imej konsep dijana**, bukan tangkapan skrin daripada projek DIDIK yang sedang berjalan. Jangan gunakan ia sebagai bukti implementasi atau jadikan keseluruhan gambar sebagai battle map gameplay.

## Flow gameplay yang dipersetujui
1. Auto-exploration/story progress → enemy encounter.
2. Dedicated JRPG battle scene, tiada joystick, WASD, berjalan manual atau dodge.
3. Question driven by parent-authored quiz; minimum 10 questions.
4. Betul: hero perform cinematic elemental attack +0.5 HP kepada hero, boss −1 bar jika boss battle.
5. Salah: enemy/boss unavoidable counterattack, hero −1.5 HP.
6. Hero max **6 HP** (half-heart precision), boss **5 HP bars**.
7. Lima dunia; Tasik Chini/Naga Chini ialah vertical slice visual utama.
8. Solo + Party; authoritative backend checks answers, HP and victory.
9. Empat game 3D lama perlu dibuang; lapan game 2D sedia ada dikekalkan.

## Susunan fail
`01_ELEMENTAL_FX_TRANSPARENT/` — direct visual FX overlays (not animated).
`02_BATTLE_SCENE_REFERENCES/` — art direction only.
`03_PREVIEWS/` — contact sheet.
`04_DOCS/` — manifest + Codex/Claude Code handoff.

## Batch yang dirancang seterusnya
- **06 — Naga Chini Boss Counterattack & Response FX:** water-breath, tidal wave, body recoil, screen splash, telegraph, impact and boss defeat.
- **07 — Tasik Chini Story/Cutscenes:** auto-journey panels, enemy encounter reveals, elemental unlock, boss reveal, clear/victory/defeat.
- **08 — Batang Lupar/Bujang Senang:** HD clean arena, characters/enemies/boss poses, FX/UI themes.
- **09 — Hutan Larut/Gajah Rimba:** equivalent game assets.
- **10 — Rimba Bayangan/Sang Kancil Bayangan:** equivalent game assets.
- **11 — Gunung Ledang/Penunggu Kabus:** equivalent game assets, finale.
- **12 — Cross-world hero states, sound, animation & QA:** production sprite sheets and motion/audio where practical.

**No further batches are included in this ZIP; they require separate creation.**
