# DIDIK JRPG — Batch 03 / TASIK CHINI HD

Batch ini menumpukan **World 1: Tasik Chini**, menggunakan aset HD baharu yang berasingan. Ia **tidak** mengandungi video sebenar, rig animasi, sprite sheet gerakan, atau fail sumber berlapis PSD/ASEPRITE.

## Fail utama
- `01_BATTLE_BACKGROUND/01_...original_1672x941.png`: latar asli, tanpa hero/boss/HUD.
- `01_BATTLE_BACKGROUND/02_...FHD_1920x1080.png`: resolusi 1920×1080 daripada upscale Lanczos; **bukan detail asli 1080p**.
- `01_BATTLE_BACKGROUND/03_...webp`: versi web lebih ringan.
- `02_HERO_CHARACTERS/`: full-body ilustrasi Hang Tuah dan Mahsuri ber-alpha; setiap satu **pose statik**, bukan sprite animasi.
- `03_BOSS_NAGA_CHINI/`: ilustrasi naga ber-alpha; **pose statik**.
- `04_UI_REFERENCE/`: konsep HUD dan pertarungan, **bukan UI button yang dipisah**.
- `05_COMPOSITE_PREVIEWS/`: gabungan layer sebenar dalam 1920×1080 (mockup daripada aset; **bukan screenshot game yang berjalan**).
- `06_DOCUMENTATION/`: manifest mesin dan arahan Codex/Claude Code.

## Penting untuk Codex
1. Gunakan latar tanpa watak sebagai back layer (`background-size:cover` atau parallax berasingan bila ada sumber).
2. Gunakan PNG alpha berasingan untuk watak dan naga; jangan crop hero daripada mockup.
3. Posisi hero di kiri, boss di kanan; susunan responsive untuk mobile.
4. Overlay kuiz, HP, bar boss, dan 5 elemen hendaklah **komponen interaktif**, bukan imej yang mempunyai teks statik.
5. Semua validasi jawapan, healing, damage dan boss HP kekal server-authoritative.
6. **Story Mode tiada joystick:** gunakan perjalanan cerita automatik -> JRPG battle scene -> quiz -> animasi serang/balas.
7. Perlukan produksi lanjut untuk gerakan betul: idle/hurt/attack/defeat frames, boss hit/attack, 5 elemen VFX, story cutscenes, audio. Jangan mengaku animasi telah siap jika hanya menggunakan still art.
8. Kekalkan 8 game 2D sedia ada; buang 4 game 3D (`litar`, `penalti`, `lanun`, `menara`).

**Art direction:** 2D illustrated/chibi anime JRPG yang HD, Malay folklore, tidak meminjam aset berhak cipta Zelda/Final Fantasy.
