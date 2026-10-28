# DIDIK Legenda — Pakej Senjata Elemen (Konsep Aset)

Pakej ini mengandungi **10 sprite PNG lutsinar (768 × 960)**: dua hero (`tuah` dan `mahsuri`) × lima elemen (`fire`, `water`, `wind`, `earth`, `lightning`). **Setiap hero jelas memegang senjata berlainan bagi setiap elemen.**

Ini ialah **aset konsep untuk semakan visual**, bukan sprite daripada repositori asal dan **bukan animasi lengkap**. Penjanaan visual menggunakan gambaran watak Hang Tuah dan Mahsuri; sebelum diintegrasikan ke produksi, padankan pakaian, proporsi, sisi menghadap, posisi tangan dan gaya grafik dengan sprite sedia ada dalam `live/web/static/story/heroes/` (jika berlainan, jangan terus menggantikannya).

## Isi ZIP

- `assets/heroes/tuah/{fire,water,wind,earth,lightning}/equipped_ready.png` — 5 variasi Hang Tuah.
- `assets/heroes/mahsuri/{fire,water,wind,earth,lightning}/equipped_ready.png` — 5 variasi Mahsuri.
- `preview/all_10_hero_elements.png` — kolaj semua 10 variasi untuk semakan.
- `source/concept_atlas_magenta.png` — helaian asal dengan latar magenta sebelum pengasingan.
- `manifest.json` — lokasi, saiz dan elemen bagi setiap aset.
- `CLAUDE_CODE_PROMPT.md` — **arahan integrasi siap sedia untuk Claude Code**, di akar ZIP.
- `ASSET_REVIEW_CHECKLIST.md` — QA sebelum digunakan dalam permainan.

## Cara guna dengan Claude Code

1. Ekstrak ZIP ini **ke dalam akar repositori DIDIK** (atau salin folder diekstrak ke repositori) dengan nama folder `didik_element_weapons_pack/`.
2. Buka Claude Code di akar repo DIDIK.
3. Suruh Claude Code baca `didik_element_weapons_pack/CLAUDE_CODE_PROMPT.md`, kemudian laksanakan arahannya. **Tidak perlu salin prompt panjang dari chat** — fail Markdown sudah ada di dalam ZIP.
4. Semak perbandingan dengan rupa hero asal, dan jalankan build + ujian sebelum merge/deploy.

> Nota: Hanya menyalin fail ZIP tanpa mengekstrak atau menunjuk fail Markdown tidak semestinya akan membuat Claude Code menjalankan arahan secara automatik. Arahan pembacaan satu baris / penggunaan `@didik_element_weapons_pack/CLAUDE_CODE_PROMPT.md` lazimnya masih diperlukan.

**Penting:** Mekanik lima elemen, pengiraan hati/nyawa, soalan dan damage harus kekal mengikut backend sedia ada. Jangan menjadikan pemilihan elemen client-authoritative.
