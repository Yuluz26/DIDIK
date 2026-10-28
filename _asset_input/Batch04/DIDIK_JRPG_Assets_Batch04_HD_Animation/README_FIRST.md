# DIDIK JRPG — Batch 04: HD Character/Boss Poses

**Status: siap ZIP sebagai asset concept / static battle poses, BUKAN complete animation video.**

## Yang tersedia

- 6 pose **Hang Tuah**: idle, ready, attack, cast, hurt, victory.
- 6 pose **Mahsuri**: idle, ready, attack, cast, hurt, victory.
- 5 pose **Naga Chini**: idle, attack, special, hurt, defeat.
- 1 **Tasik Chini quiz-battle concept** (bukan screenshot sebenar daripada game).
- 3 original HD pose sheets PNG telus dan 17 cropped PNG individu telus.
- Manifest JSON dan CSV, plus prompt integrasi.

Semua pose diambil daripada gambar sumber 1448 × 1086 px (RGBA) dan dipecahkan kepada PNG berasingan. Paparan battle concept beresolusi 1672 × 941 px. Kualiti visual adalah HD sumber asal; tiada dakwaan 4K native.

### Asset limitations
- Original pose sheet tidak berupa sprite sheet dengan frame seragam; setiap pose adalah **ilustrasi berbeza**, bukan 12–24 frame animasi.
- Crops automatik boleh ada elemen pinggir yang terpotong atau gangguan di sempadan panel. Semak secara visual sebelum ship production.
- Image generation boleh menghasilkan bentuk yang kurang konsisten antara pose; QA imej sebelum guna sebagai sprite rasmi.
- Pose individu sedia ada boleh ditween / crossfade untuk prototaip JRPG. Untuk gerakan licin: reka frame pengantara, masking / rigging serta layering sebenar.
- Tiada video output dalam batch ini.

### Usage guidance
- Letakkan watak sebagai sprite dengan anchor bottom-center dan UI secara berasingan; guna asset sheet asal sebagai canonical illustration.
- Phase: intro -> question -> answer evaluation -> answer correct attack animation / wrong boss counter -> update hearts/boss bars -> next question.
- UI question & answer mesti generated dari backend; teks dalam composite art adalah dekorasi sahaja.
- Kesihatan: betul +0.5 HP (cap 6); salah -1.5 HP; boss 5 HP, kehilangan 1 HP per correct answer.
- 5 weapons: api, angin, petir, tanah, air. Jangan gantikan mana-mana dengan bayangan.
- Jangan tambah manual joystick atau kawalan gerak player. Pertukaran scene automatik, pertarungan JRPG turn based.
- Semua mod 3D lama dibuang: litar, penalti, lanun, menara. Lapan mod 2D asal kekal.

## Files
- `01_ORIGINAL_HD_POSE_SHEETS` — no-crop pose sheets (reference/master)
- `02_EXTRACTED_POSES` — 17 PNG individu alpha channel
- `03_BATTLE_COMPOSITION_REFERENCE` — one combined concept artwork
- `04_PREVIEW` — visual overview
- `05_DEVELOPER_GUIDE` — manifest & Codex/Claude Code instructions
