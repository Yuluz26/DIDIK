# DIDIK Legenda — Batch 14: Transition Text HD

## Apa yang ada?
- **22 banner teks HD** (1920×480), PNG dengan kanvas luar telus.
- **22 teks tanpa panel** (1920×480), PNG telus untuk animasi tersuai.
- **44 SVG vektor**: huruf ditukar kepada outline paths untuk mengekalkan rupa tanpa memerlukan font fail.
- **6 transisi dianimasikan**: setiap satu 12 frame (1280×320), dengan PNG individu, APNG, GIF preview dan sprite sheet 4×3.
- **2 contact sheet**, manifest JSON, CSV dan panduan Claude Code/SvelteKit.

## Ayat contoh
`Boss Akan Menyerang!` ialah fail `01_STATIC_BANNERS_PNG/boss_akan_menyerang.png`. Ejaan telah ditentukan secara eksplisit dan dibina melalui vector font outlines, bukan tulisan hasil image model.

## Penggunaan
Letakkan fail PNG terpilih di `live/web/static/assets/didik/transition_text/` — **bukan** semua sekali jika tidak diperlukan. Gunakan gambar hanya sebagai overlay visual; sistem quiz/HP/boss mesti disahkan oleh server.

## Ketepatan grafik
Aset ini adalah ilustrasi UI asli dibuat dengan vector+programmatic compositing, **bukan** potongan daripada imej AI dan bukan animasi 3D. PNG telus. Fail SVG tidak mengandungi font fail. GIF mempunyai latar navy untuk preview sahaja; gunakan APNG/PNG frame untuk transparensi sebenar.

## Prestasi dan aksesibiliti
- Lazy-load hanya mesej yang diperlukan pada setiap checkpoint.
- Papar teks yang sama secara semantik dalam DOM/aria-live, kerana PNG tidak dibaca screen reader.
- Patuh `prefers-reduced-motion` untuk hentikan animasi flash/slide.
- Peringatan: wrong answer mengurangkan **1.5 hearts** dan correct memulihkan **0.5 hearts**, semua ditentukan backend; banner hanyalah presentation.

## Urutan disyorkan untuk Boss Akan Menyerang
1. Server sahkan jawapan salah dan tetapkan damage.
2. Munculkan banner `boss_akan_menyerang` selama ~1.0–1.3 saat.
3. Mainkan pose/efek counterattack Naga Chini daripada pack terdahulu.
4. Paparkan perubahan nyawa dan checkpoint secara server-authoritative.

## Format
Banners and text only: RGBA PNG 1920x480. Animation frames: RGBA PNG 1280x320 (12), sheets 4 columns x 3 rows.
