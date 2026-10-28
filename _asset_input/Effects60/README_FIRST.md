# DIDIK Legenda — Hero Elemental Weapon + Attack FX Pack

Pek ini mempunyai **dua karakter (lelaki/perempuan) × lima pilihan elemen senjata** serta **lima kesan serangan × 12 frame PNG (60 frame)**. Semua sumber PNG asal dikekalkan tanpa penukaran kepada JPEG atau pengurangan resolusi.

## Apa yang betul-betul disertakan
- `01_ORIGINAL_CHARACTER_SHEETS/`: dua sprite sheet asal 1448×1086, RGBA.
- `02_CHARACTER_VARIANTS/`: 10 potongan karakter asli dan 10 versi berpusat pada kanvas RGBA 768×768; 5 variasi setiap hero.
- `03_ORIGINAL_ATTACK_SHEETS/`: lima helaian efek asal 1254×1254, RGBA.
- `04_ATTACK_FRAMES/`: 60 frame individu 314×418 PNG (12 per elemen; turunan pemotongan 4×3).
- `05_ANIMATED_PREVIEWS/`: 5 APNG telus dan 5 GIF preview (sekadar menunjukkan urutan 12 gambar).
- `06_PREVIEW_SHEETS/`: poster kontak ringkas, bukan aset permainan.
- `07_CLAUDE_CODE_HANDOFF/`: arahan integrasi SvelteKit / FastAPI.
- `asset_manifest.json` dan `.csv`: inventori serta fail path.

## PENTING — batasan kualiti
- Karakter mempunyai **lima rupa senjata berlainan**, tetapi setiap rupa ialah satu pose **statik**, bukan lima animasi frame-by-frame hero.
- Sumber efek memang mengandungi dua belas ilustrasi per elemen dalam satu atlas, tetapi imej dijana secara AI; urutan frame bukan animasi rig yang dijamin lancar. Potongan boleh mengandungi artefak tepi/bertindih; kemaskan jika perlu.
- Satu frame FX bersaiz asal 314×418; pakej tidak mendakwa setiap frame individu ialah Full HD.
- Preview GIF mengurangkan warna untuk keserasian. Gunakan PNG individu atau APNG untuk paparan alpha dan warna penuh.
- Pastikan `prefers-reduced-motion` disokong.

## Element mapping
Api = fire blade; Angin = wind sword; Petir = lightning spear/blade; Tanah = earth axe; Air = water blade. Hero lelaki dan perempuan boleh memilih semua lima elemen.
