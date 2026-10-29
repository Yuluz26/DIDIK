# CLAUDE CODE — DIDIK Legenda: Perubahan Visual Senjata Lima Elemen

## Tujuan

Saya telah meletakkan pakej `didik_element_weapons_pack/` di akar projek DIDIK. **Baca dan patuhi dokumen ini**. Pakej mengandungi sepuluh sprite 2D konsep: dua hero (Hang Tuah / `tuah`, Mahsuri / `mahsuri`) memegang senjata unik bagi lima elemen (`fire`, `water`, `wind`, `earth`, `lightning`). **Jangan gunakan logo/teks dari gambar pratonton sebagai aset permainan.** PNG sebenar ada dalam `assets/heroes/`.

**Matlamat:** apabila hero menerima / mempunyai elemen yang telah disahkan oleh server, paparkan hero yang benar-benar memegang senjata berkaitan, bukan hanya tukar warna projectile atau visual FX. Pastikan kedua-dua hero berfungsi dalam Solo dan Party, pada desktop dan telefon.

## Syarat kejuruteraan utama

1. **Semak repo dan kod terlebih dahulu.** Pastikan branch projek yang mempunyai permainan ialah `feat/legenda-story-mode` atau perubahan relevan terkini. Kenal pasti sumber sebenar elemen hero dari server, jangan reka property atau event palsu. Teliti `live/web/src/lib/games/legenda/Stage.svelte`, `data.ts`, `LegendaPlayer.svelte`, manifest aset, logik `live/server/didik_live/game/modes/legenda.py` dan ujian berkaitan. Jika fail telah berpindah, cari alternatif semasa.
2. **Semak kualiti dan keserasian identiti.** Bandingkan `preview/all_10_hero_elements.png` dan semua 10 sprite dengan `live/web/static/story/heroes/tuah/` serta `.../mahsuri/`. Aset ini ialah **konsep AI dan BUKAN rupa rasmi yang dipetik dari repo**. Jika rupa, outfit, proporsi, orientasi atau sudut kamera tak sepadan, JANGAN silently replace aset rasmi. Pilih antara: (a) pakai sebagai preview bersyarat/feature flag dan catat jurang seni, atau (b) bina implementasi yang menyokong sprite unik sambil mengekalkan rupa lama sehingga aset yang betul disediakan. Terangkan keputusan dalam ringkasan.
3. **Salin fail sumber tanpa musnahkan asset lama** ke lokasi baharu, misalnya `live/web/static/story/heroes/{hero}/elements/{element}/equipped_ready.png`, atau path menurut manifest sedia ada. Jangan overwrite `idle.webp`, `ready.webp`, `attack.webp`, `cast.webp`, `hurt.webp`, `victory.webp` asal.
4. **Tambah pemetaan selamat** `hero + element -> sprite URL` dan fallback kepada sprite hero sedia ada. Gunakan ID elemen yang benar-benar digunakan server; jika nama berbeza (`fire`/`api`, dll.), buat mapping eksplisit di TypeScript. Tangani elemen belum unlocked, undefined/null, unload, gagal imej, reconnect dan perpindahan dunia.
5. **Implementasi visual berasaskan state server.** Bila elemen di-unlock dan kini aktif, gunakan sprite hero bersenjata yang berkaitan sekurang-kurangnya pada pose `ready`, dan jika kualiti sesuai pada `attack`/`cast`. Untuk pose lain, jika tidak ada sprite yang serasi, pakai pose asas (bukan menyamar sebagai animasi penuh). **Elakkan hero flicker** semasa pose/transition. Jangan visual equip sebelum server mengesahkan.
6. **Jangan ubah mekanik permainan**, khususnya: jawapan betul/salah, pengiraan 6 hati = 12 setengah hati, damage, unlock selepas 5 soalan betul, pemarkahan, tahap kesukaran, bos 5 HP bar, kelemahan elemen, urutan soalan, Party sync dan server-side authority. Visual sahaja.
7. **UX transformasi.** Jika event unlock sudah ada, sediakan efek visual ringkas (flash/sparkle) **hanya selepas server-confirmed unlock**, paparkan nama elemen dalam bahasa BM, hormati `prefers-reduced-motion`. Jangan menambah overlay yang menutup soalan. Gunakan FX sedia ada jika sesuai.
8. **QA teknikal**: jalankan ujian Python backend berkaitan (cth. `pytest` di `live/server` mengikut setup repo), semakan TS (`npm run check` jika tersedia), `npm run build` dan ujian manual senario. Gunakan arahan sebenar dari package.json/README, jangan andaikan semuanya wujud.
9. **Ujian senario wajib**: Tuah/Mahsuri dengan kelima-lima elemen, belum unlock, unlock selepas 5 betul, jawapan salah, pertempuran bos, Solo/Party, reconnect, resize mobile portrait & landscape, missing-asset fallback, reduced motion dan image load error. Jangan claim browser test jika tidak benar-benar dilaksanakan.
10. **Berikan ringkasan dif**: fail baharu/diubah, bagaimana asset mapping dipasang, mana art yang masih perlu diluluskan, arahan ujian dan keputusan sebenar. Jangan push/merge/deploy tanpa arahan saya.

## Struktur pakej yang perlu dibaca

```text
didik_element_weapons_pack/
  README.md
  CLAUDE_CODE_PROMPT.md              <-- fail arahan ini
  ASSET_REVIEW_CHECKLIST.md
  manifest.json
  assets/heroes/tuah/{fire,water,wind,earth,lightning}/equipped_ready.png
  assets/heroes/mahsuri/{fire,water,wind,earth,lightning}/equipped_ready.png
  preview/all_10_hero_elements.png
  source/concept_atlas_magenta.png
```

## Takrif siap (Definition of Done)

- Kod boleh mengendalikan 2 hero × 5 elemen menggunakan mapping yang disahkan, fallback pada asset asal apabila perlu.
- Paparan senjata benar-benar berbeza; animasi/FX lama dan gameplay server tidak rosak.
- Keserasian visual dengan hero asal dinilai secara jelas, bukan dianggap automatik.
- Build dan ujian yang boleh dijalankan lulus; sebarang kekangan dilaporkan dengan tepat.
- Semua perubahan hanya pada working tree/branch tempatan sehingga saya beri kebenaran push/deploy.

Mulakan dengan audit ringkas sumber hero/element state di Stage.svelte + data.ts sebelum menyentuh kod. Jika aset konsep tak cukup serasi untuk production, bina sistem mapping/fallback dahulu dan senaraikan aset seni yang perlu dipinda — **jangan meneka**.
