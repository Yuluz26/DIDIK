# Research: platform kuiz berbilang pemain untuk kanak-kanak (ala ZEP Quiz)

Disediakan 21 Oktober 2026, sebelum sebarang pembinaan. Tujuan: tentukan permainan apa yang boleh dibina,
jenis soalan, cara bilik berfungsi, arah visual, dan seni bina Python.

**Had research ini.** Polisi rangkaian persekitaran ini menyekat `quiz.zep.us`, `docs.channel.io`,
`quiz-blog-en.zep.us` dan laman blog pihak ketiga, jadi fakta ZEP diambil daripada ringkasan carian web
(halaman rasmi ZEP, dokumen bantuan ZEP, G2, Capterra, Google Workspace Marketplace dan blog guru).
Sebahagian sumber bercanggah (contohnya jumlah peta), dan ia ditanda di bawah. Tiada apa-apa di sini
diuji pada produk ZEP sendiri.

---

## 1. Ringkasan

- **ZEP Quiz** ialah kuiz dalam dunia 2D: setiap murid mengawal avatar di atas peta, nampak kawan bergerak
  secara langsung, dan menjawab soalan yang tersorok atau muncul serentak. Ia kuat pada rasa "bermain
  bersama", tetapi hanya ada tiga jenis soalan (pilihan, jawapan pendek, OX), OX pun berbayar, dan peta
  terbaik berbayar.
- **Peluang kita:** permainan yang lebih kaya (ekonomi, kerjasama, pasukan, peta), **12 jenis soalan**
  yang dibuat sendiri oleh ibu bapa tanpa AI, Bahasa Melayu dahulu dengan dunia dan watak Malaysia,
  **butang "Bacakan soalan"** untuk Prasekolah yang belum lancar membaca, dan semuanya **percuma**.
- **Cadangan teknikal:** pelayan permainan **Python (FastAPI + WebSocket, asyncio)** yang menjadi hakim
  (semua markah dikira di pelayan), PostgreSQL + Redis, dan antara muka **TypeScript (SvelteKit)** dengan
  **Phaser 4** untuk adegan permainan, **GSAP** untuk interaksi kecil dan **Rive** untuk Didi dan avatar.
- **Tiga mod untuk MVP:** *Lumba Sampan* (lumba jawapan serentak), *Betul atau Salah: Lompat!* (versi kita
  bagi kuiz OX ZEP, dengan avatar berlari ke tebing jawapan), *Pulau Harta Karun* (jawab untuk dapat
  penyodok, gali petak, untung atau dicuri burung kakak tua).

---

## 2. Apa yang ZEP Quiz buat

| Perkara | Dapatan | Sumber |
|---|---|---|
| Konsep | Avatar bergerak di peta 2D (anak panah di PC, pad di telefon). Murid nampak avatar kawan bergerak serentak. Ada item di peta (contoh: laju bertambah dekat satu objek, ikan yu memperlahankan avatar). | ZEP docs "Avatar Control", blog guru |
| Kategori peta | Pelayar peta rasmi: *Sequencing*, *Freestyle*, *Round match*, *Team match*, *Co-op Mode*. Freestyle: soalan tersorok di seluruh peta, dijawab ikut sebarang urutan (rasa memburu harta). Round match: semua jawab soalan yang sama serentak. Team match: kelas dibahagi dua pasukan. | quiz.zep.us (senarai peta), ZEP docs |
| Jumlah peta | Bercanggah: satu blog kata 25+ peta dalam empat mod; laman rasmi menunjukkan lebih sedikit bagi setiap kategori. | TeacherPH vs quiz.zep.us |
| Jenis soalan | Pilihan jawapan, jawapan pendek, kuiz OX. **OX hanya untuk pelan Pro.** | ZEP docs "Quiz Creation" |
| Kawalan guru | *Start Together*, *Learning Report*, togol *Waiting Room*, papan kedudukan. | ZEP docs |
| Masuk bilik | Pautan atau kod QR. Integrasi Google Classroom dan Canvas. | ZEP, Google Workspace Marketplace |
| Harga | Free USD 0 (peta percuma, ciri asas), Basic sekitar USD 15/guru/bulan, Pro sekitar USD 35/guru/bulan. Satu panduan guru menyebut had 200 pengguna serentak bagi pelan percuma (belum disahkan pada laman harga rasmi). | G2, Capterra |
| Satu kajian | Kajian 2026 di kelas vokasional Indonesia mendapati interaksi murid (bertanya, menjawab, memberi pendapat) purata 18.96% dalam kelas yang diperhati. Ingatan bahawa permainan sahaja tidak menjamin penglibatan. | Jurnal siducat.org |

**Kelemahan ZEP yang kita boleh atasi:** jenis soalan sedikit; ciri utama berbayar; tidak berbahasa Melayu
dan tiada konteks Malaysia; tiada sokongan untuk kanak-kanak yang belum boleh membaca; kreativiti peta
bergantung pada katalog mereka.

## 3. Pesaing lain dan mekanik yang terbukti disukai

| Platform | Mekanik yang disukai | Apa kita ambil |
|---|---|---|
| **Blooket** | *Gold Quest*: jawapan betul membuka satu daripada tiga peti (emas, darab tiga, tukar emas dengan pemain lain, curi 10–25% daripada pendahulu). *Tower Defense*: jawapan betul = duit untuk membina menara. Juga Racing, Cafe, Factory, Battle Royale. | Pisahkan "menjawab" daripada "lapisan permainan". Unsur nasib + mekanik kejar-mengejar supaya murid yang lemah masih ada peluang. |
| **Gimkit** | *Classic*: duit daripada jawapan, beli naik taraf dan kuasa. Mod 2D: *Fishtopia* (memancing dengan umpan daripada jawapan), *Capture the Flag* (pasukan dalam arena), *The Floor is Lava*, *Trust No One* (deduksi sosial ala Among Us). | Ekonomi kecil dengan naik taraf; mod pasukan dalam arena 2D. |
| **Kahoot** | Hos memaparkan soalan di skrin besar, murid menjawab di telefon, podium di hujung; mod kendiri; jawapan bergambar. | Mod "Skrin besar" untuk kelas dan majlis keluarga. |
| **Wayground (dahulu Quizizz)** | Kuasa (*Double Points*, *Immunity*, *Extra Time*), meme, muzik, tema dan animasi yang disebut guru sebagai sebab murid seronok; mod kendiri yang membuang tekanan masa; 20+ jenis soalan (padan, susun, kategori, seret-letak, label, hotspot, lukis). Pelan percuma terhad dan ada iklan. | Kuasa yang adil, maklum balas yang lucu, muzik; jenis soalan yang kaya. **Tanpa iklan.** |

**Lima pengajaran:**
1. Pisahkan pembelajaran (menjawab dengan betul) daripada permainan (membelanjakan ganjaran). Kanak-kanak yang
   kurang laju tetap seronok kerana keputusan permainan bukan semata-mata kelajuan.
2. Sesi pendek (5–10 minit) dan mod yang berbeza-beza mengekalkan minat.
3. Nasib dan mekanik "kejar-mengejar" mengelakkan papan kedudukan yang beku.
4. Mod kerjasama (semua menang bersama) penting untuk kanak-kanak kecil dan kelas bercampur umur.
5. Hos perlu kawalan dan laporan: siapa sudah masuk, jeda, tamatkan, siapa perlukan bantuan.

---

## 4. Permainan yang boleh saya bina

Setiap mod memakai enjin yang sama: pelayan menghantar soalan, menyemak jawapan dan memberi ganjaran;
mod hanya mengubah apa yang ganjaran itu lakukan di skrin. Usaha: S (kecil), M (sederhana), L (besar).

### Tahap A: calon MVP

| Mod | Cara main | Kenapa seronok | Jenis soalan | Usaha |
|---|---|---|---|---|
| **Lumba Sampan** | Semua jawab soalan yang sama serentak. Betul dan laju = sampan maju lebih jauh di sungai. Salah tetap maju sedikit, jadi tiada yang tertinggal jauh. Arus deras sekali-sekala menolak semua ke depan. Garisan penamat, podium. | Tegang, mudah difahami, sesuai untuk skrin besar. Setara *Round match* ZEP. | Semua jenis yang boleh dijawab dalam masa 20 saat | S–M |
| **Betul atau Salah: Lompat!** | Avatar berdiri di tengah sungai. Kenyataan muncul, setiap pemain lari ke tebing **BETUL** atau **SALAH** sebelum masa tamat. Tebing yang salah tenggelam dengan percikan; pemain itu jadi "ikan penonton" yang masih boleh menjawab untuk bonus, jadi tiada yang duduk bosan. | Bergerak secara fizikal di skrin, lucu, semua nampak pilihan kawan. Versi kita bagi kuiz OX ZEP, dan percuma. | Betul/salah, pilihan dua jawapan | M (pergerakan avatar diselaraskan) |
| **Pulau Harta Karun** | Pemain menjawab pada kadar sendiri selama 5–8 minit. Setiap jawapan betul memberi penyodok; gali satu petak di pulau: syiling, permata, peta (darab dua), atau burung kakak tua yang mencuri dari pendahulu. | Nasib, strategi dan kejutan. Setara *Gold Quest* Blooket. | Semua jenis | M |

### Tahap B: selepas MVP

| Mod | Cara main | Usaha |
|---|---|---|
| **Kampung Kita** (kerjasama) | Seluruh bilik menjawab untuk mengumpul bahan dan membina kampung bersama (rumah, sekolah, masjid, rumah panjang). Satu bar kemajuan untuk semua; bilik menang atau belajar bersama. Tiada yang kalah. | M |
| **Pasukan Warna** (pasukan) | Dua pasukan (Harimau dan Penyu) merebut petak di peta Malaysia. Jawapan betul = tawan petak. | M–L |
| **Teka Gambar** | Gambar tersembunyi terbuka sepetak demi sepetak setiap kali ada jawapan betul; sesiapa yang meneka gambar (ditaip) dapat bonus. | S–M |
| **Hutan Misteri** (peta jelajah) | Ala *Freestyle* ZEP: avatar menjelajah hutan, peti soalan tersorok, kumpul kunci, buka pintu keluar. | L |
| **Telur Penyu** (pertahanan) | Jawapan betul = cangkerang untuk meletak pengawal yang melindungi telur penyu daripada ketam. Ala *Tower Defense*. | L |
| **Kebun Ajaib** (ekonomi) | Jawapan = air dan benih; tanam, tuai, jual di pasar, naik taraf. Ala *Farmchain*. | L |
| **Ejaan Lebah** | Eja perkataan dengan jubin huruf; pusingan kalah-mati yang ringan. Untuk BM dan Bahasa Inggeris. | S–M |

**Kuasa yang adil:** *Gandaan* (mata x2 untuk satu soalan), *Perisai* (salah sekali tanpa kehilangan),
*Masa Lebih*. Kuasa yang menyusahkan orang lain (bekukan skrin kawan) dimatikan secara lalai dan hos boleh
menghidupkannya, kerana kanak-kanak kecil cepat kecewa.

---

## 5. Jenis soalan (dibuat sendiri oleh ibu bapa, tanpa AI)

Semua jenis mesti boleh dijawab dengan ibu jari di telefon dalam masa singkat, dan disemak di pelayan.

| # | Jenis | Cara kanak-kanak menjawab | Semakan automatik | MVP |
|---|---|---|---|---|
| 1 | Pilihan tunggal | Ketik satu daripada 2–6 jubin (teks atau gambar) | Tepat | Ya |
| 2 | Pilihan berganda | Ketik semua yang betul, kemudian Hantar | Penuh, atau separa jika hos benarkan | Ya |
| 3 | Betul / Salah | Dua butang besar, atau lari ke tebing (mod Lompat!) | Tepat | Ya |
| 4 | Taip jawapan | Papan kekunci | Senarai jawapan diterima; abai huruf besar, ruang dan tanda baca; pilihan toleransi salah eja 1 huruf | Ya |
| 5 | Nombor | Pad nombor atau gelangsar | Tepat, julat atau toleransi (contoh ±2) | Ya |
| 6 | Susun turutan | Seret atau ketik mengikut urutan | Tepat; markah separa pilihan | Ya |
| 7 | Padankan pasangan | Ketik kiri kemudian kanan (perkataan dan gambar) | Setiap pasangan | Ya |
| 8 | Isi tempat kosong | Pilih daripada bank perkataan atau taip | Setiap ruang | Ya |
| 9 | Kumpulkan | Masukkan item ke dalam 2–4 bakul | Setiap item | Fasa 2 |
| 10 | Ketik pada gambar | Ketik kawasan betul pada gambar atau peta | Kawasan yang ditanda ibu bapa | Fasa 2 |
| 11 | Eja dengan huruf | Susun jubin huruf | Tepat | Fasa 2 |
| 12 | Dengar dan jawab | Main rakaman suara ibu bapa, kemudian jawab dengan mana-mana jenis di atas | Ikut jenis | Fasa 2 |
| – | Undian | Pilih pendapat (tiada jawapan betul) | Tiada markah | Fasa 2 |

**Editor ibu bapa:** satu halaman, templat setiap jenis, pratonton seperti yang dilihat anak, muat naik gambar
(diproses semula di pelayan), pustaka kuiz sendiri, salin kuiz, dan kongsi kuiz dengan ibu bapa lain melalui
pautan (baca sahaja, boleh disalin). **Tiada penjana soalan AI**, seperti diminta.

---

## 6. Bilik permainan: masuk dengan satu pautan

1. Ibu bapa pilih kuiz, tekan **Main bersama**, pilih mod dan tetapan (masa, kuasa, masuk lewat).
2. Bilik dicipta dengan **pautan pendek yang mudah disebut** (contoh `didik.my/m/harimau-ungu-42`), **kod QR**
   dan **kod 6 digit** untuk ditaip.
3. Kanak-kanak buka pautan, pilih **nama samaran yang dicadangkan** (contoh "Kancil Biru"; nama sebenar
   tidak digalakkan) dan **avatar** (kancil, harimau, penyu, enggang, gajah), terus masuk **lobi**: avatar
   berlegar, boleh hantar stiker, menunggu hos.
4. Hos tekan **Mula**. Selepas tamat: podium, ganjaran, dan **Main lagi** dalam bilik yang sama.

**Tiada akaun untuk kanak-kanak.** Jika tab ditutup atau internet terputus, peranti yang sama masuk semula
ke tempatnya (token peranti, bukan akaun).

**Dua cara main:** setiap pemain dengan peranti sendiri (seperti ZEP), atau **Skrin besar** di mana soalan dan
dunia permainan dipaparkan di TV atau laptop dan telefon menjadi alat kawalan (seperti Kahoot). MVP: peranti
sendiri dahulu, Skrin besar dalam Fasa 2.

**Keselamatan kanak-kanak (wajib dari hari pertama):**
- Tiada sembang teks bebas. Hanya stiker dan reaksi yang ditetapkan.
- Nama samaran ditapis (senarai perkataan kasar BM dan Inggeris); hos boleh menukar nama atau mengeluarkan pemain.
- Togol **bilik menunggu** (hos meluluskan setiap pemain), kunci bilik selepas mula, had pemain.
- Bilik tamat selepas sesi; pautan tidak boleh diteka; cubaan masuk dihadkan kadarnya.
- Tiada iklan, tiada penjejak, tiada data peribadi kanak-kanak.
- **Undang-undang:** Akta Keselamatan Dalam Talian 2025 berkuat kuasa 1 Januari 2026, dan Kod Perlindungan
  Kanak-kanak MCMC berkuat kuasa 1 Jun 2026 (keselamatan sejak reka bentuk, had akaun bawah 16 tahun, had
  komunikasi orang dewasa dengan kanak-kanak, tiada pendedahan maklumat peribadi kanak-kanak). Reka bentuk
  di atas selari dengannya, tetapi sama ada akta itu terpakai kepada platform kecil perlu disahkan oleh peguam.

---

## 7. Arah visual dan animasi

Permintaan: animasi setanding Quizizz, latar yang menarik dan kesan hover yang comel.

**Gaya:** *Claymorphism*, padanan ui-ux-pro-max untuk aplikasi pendidikan kanak-kanak dan permainan
kasual: rupa 3D lembut, tebal dan seperti mainan, sudut bulat, bayang dalam dan luar, lantunan lembut
(`cubic-bezier(0.34, 1.56, …)`). Ia sambungan semula jadi daripada gaya DIDIK sekarang (neumorfisme pastel),
dengan warna yang lebih tepu untuk setiap dunia permainan dan teks yang tetap kontras tinggi.

**Latar:** adegan bergambar berlapis (parallax) mengikut dunia: sungai, hutan, kampung, pantai, dengan
gerakan ambien perlahan (awan, kilauan air, kelip-kelip, daun gugur). Bukan bentuk rawak terapung: setiap
elemen datang daripada dunia itu. Animasi dihentikan apabila tab tersembunyi dan menjadi statik bagi
pengguna "kurangkan gerakan".

**Hover dan tekan yang comel:**
- Jubin jawapan: *squash and stretch* bila ditekan (0.94 → 1.06 dengan lantunan), goyang kecil bila hover.
- Ikon dan avatar: melambung perlahan ketika rehat, berpusing sedikit bila hover.
- Butang utama: "melompat" sekali bila boleh ditekan; bergetar lembut bila tidak boleh.
- Stiker lobi: muncul dengan *pop* dan terapung ke atas.

**Maklum balas:** betul = letupan konfeti, Didi bersorak, syiling terbang ke markah; salah = goyang lembut,
"Hampir!", jawapan betul ditunjukkan, **tiada X merah yang menghukum**. Kedudukan bertukar dengan animasi
FLIP; podium dengan bunyi gendang; api *streak*; kad kuasa yang terbalik.

**Bunyi:** kesan bunyi dan muzik setiap mod, dengan butang senyap yang jelas. Permainan mesti tetap boleh
dimainkan tanpa bunyi.

**Alat:** Phaser 4 untuk adegan permainan (rangka kerja penuh dengan adegan, input dan audio; satu sumber
menyebut ia dikeluarkan April 2026), **GSAP** untuk animasi antara muka (preset hover dan sambutan daripada
ui-ux-pro-max), **Rive** untuk Didi dan avatar kerana mesin keadaannya sesuai untuk watak yang bertindak
balas (satu ujian lama mendapati Rive kira-kira 60 FPS berbanding 17 FPS bagi Lottie pada React Native;
data lama, perlu diuji semula pada telefon murah), Howler untuk audio.

**Kebolehcapaian kanak-kanak:** sasaran ketik sekurang-kurangnya 48px; fon bulat yang mudah dibaca;
**butang Bacakan soalan** (suara Bahasa Melayu pelayar jika ada, atau rakaman ibu bapa); masa boleh
dilaraskan atau dimatikan oleh hos (WCAG 2.2.1 *Timing Adjustable*; ini panduan umum kerana carian
pangkalan data ui-ux-pro-max tidak menemui padanan khusus untuk pemasa).

**Taste-skill:** peraturannya (tiada bayang, tiada bentuk hiasan, tiada emoji) ditulis untuk laman pemasaran
dan ia sendiri menyatakan "bukan untuk skrin aplikasi". Jadi ia digunakan untuk **halaman utama platform**
sahaja. Tiga hala tuju telah dicabut; yang paling sesuai ialah **colour-chapters**: setiap bahagian halaman
ialah satu "dunia" permainan dengan warna penuhnya sendiri (sungai, hutan, kampung), seperti memilih tahap.

---

## 8. Seni bina teknikal (Python dan bahasa moden)

| Lapisan | Pilihan | Sebab |
|---|---|---|
| Pelayan aplikasi | **Python 3.13, FastAPI** (ASGI), Pydantic v2 | Moden, async, WebSocket asli, skema jelas |
| Masa nyata | **WebSocket FastAPI** dengan pengurus bilik sendiri; **Redis Pub/Sub** apabila ada lebih satu proses | Protokol ringan yang kita kawal. Sumber bersetuju kesesakan biasanya JSON dan broker, bukan rangka kerja. python-socketio ialah alternatif jika mahu bilik dan sambung semula siap sedia. |
| Enjin permainan | Satu tugas asyncio bagi setiap bilik: lobi → soalan → dedah → kedudukan → … Semua markah di pelayan; jawapan tidak pernah dihantar ke pelayar sebelum didedah. Mod avatar: 10–15 kemas kini sesaat, pelayar menginterpolasi. | Adil, tidak boleh ditipu dari pelayar |
| Data | **PostgreSQL** (SQLAlchemy 2, Alembic) untuk kuiz, ibu bapa, keputusan; **Redis** untuk keadaan bilik, had kadar, pub/sub | Standard dan murah |
| Antara muka | **TypeScript + SvelteKit** (editor, lobi, panel hos), **Phaser 4** (adegan), **GSAP**, **Rive** | Pantas di telefon murah, bundel kecil |
| Hosting | Satu VPS kecil (Docker Compose: Caddy untuk HTTPS, aplikasi, PostgreSQL, Redis), anggaran USD 6–12 sebulan | Percuma kepada pengguna, kos hos kecil |

**Apa jadi dengan DIDIK Laravel sekarang?**
- **Pilihan A (disyorkan): bina semula dalam Python** sebagai satu tumpukan. Aset dibawa: watak Didi, token
  warna, salinan Bahasa Melayu, model soalan, dan pelajaran keselamatan (CSP ketat, tiada IP dalam sesi,
  had kadar per pelawat, semakan jawapan di pelayan, penyimpan soalan yang tidak memadam jawapan).
- **Pilihan B:** kekalkan Laravel untuk kandungan dan admin, tambah perkhidmatan masa nyata Python. Dua bahasa
  dan dua deployment untuk satu produk: lebih mahal untuk diselenggara.
- **Pilihan C:** kekal Laravel dan guna Laravel Reverb untuk WebSocket. Paling cepat, tetapi bukan Python
  seperti yang diminta.

---

## 9. Pelan fasa

| Fasa | Isi |
|---|---|
| 0 (sekarang) | Research ini dan keputusan di bawah |
| 1: MVP | Akaun ibu bapa; editor dengan 8 jenis soalan; bilik dengan pautan, QR dan kod; lobi avatar; mod Lumba Sampan, Betul atau Salah: Lompat!, Pulau Harta Karun; kawalan hos; podium dan ringkasan; Bahasa Melayu; ujian automatik dan ujian pelayar sebenar |
| 2 | Kampung Kita, Pasukan Warna, Teka Gambar; jenis soalan 9–12 dan Undian; Skrin besar; perkongsian kuiz antara ibu bapa; laporan |
| 3 | Hutan Misteri, Telur Penyu, Kebun Ajaib; acara bermusim; latihan solo luar talian (PWA) |

## 10. Keputusan yang diperlukan daripada Yul

1. **Tumpukan:** setuju bina semula dalam Python (FastAPI) + TypeScript (SvelteKit + Phaser)?
2. **Tiga mod pertama:** setuju Lumba Sampan, Betul atau Salah: Lompat!, Pulau Harta Karun?
3. **Cara main:** peranti sendiri dahulu (seperti ZEP), Skrin besar kemudian?
4. **Jenama:** kekal DIDIK dan Didi si kancil?
5. **Hosting dan domain:** bajet bulanan dan nama domain.

---

## Sumber

- [ZEP QUIZ](https://quiz.zep.us/en) · [ZEP QUIZ build](https://quiz.zep.us/en/build) · [ZEP](https://zep.us/en) · [ZEP pricing](https://zep.us/en/pricing)
- ZEP docs: [To use in class](https://docs.channel.io/zepquiz/en/categories/To-use-in-class-b3a80e78), [Avatar Control](https://docs.channel.io/zepquiz/en/articles/Avatar-Control-fd40c1f5), [Freestyle Map](https://docs.channel.io/zepquiz/en/articles/Freestyle-Map-d900bc68), [Quiz Creation](https://docs.channel.io/zepquiz/en/articles/Quiz-Creation-76343d1f), [Learn more about the quiz map](https://docs.channel.io/zepquiz/en/articles/709a8010-Learn-more-about-the-quiz-map)
- [ZEP QUIZ Pricing (G2)](https://www.g2.com/products/zep-quiz/pricing) · [ZEP QUIZ (Capterra)](https://www.capterra.com/p/10041457/ZEP-QUIZ/) · [TeacherPH](https://www.teacherph.com/zep-quiz-metaverse-tool-filipino-teachers-need-right-now/) · [ZEP QUIZ blog](https://quiz-blog-en.zep.us/how-to-create-a-metaverse-quiz-map-in-10-minutes-55048) · [Google Workspace Marketplace](https://workspace.google.com/marketplace/app/zep_quiz/766608022007?hl=bn) · [Kajian siducat.org](https://siducat.org/index.php/jpi/article/download/2553/1787)
- Blooket: [Blooket Game Modes](https://shapes.inc/fandom/blooket/game-modes) · [Designbeep guide](https://designbeep.com/2026/06/09/blooket-the-complete-guide-to-the-game-based-learning-platform/)
- Gimkit: [Designbeep guide](https://designbeep.com/2026/06/09/gimkit/) · [Which Gimkit modes have teams](https://blog.blog.wordpress.arktimes.com/which-gimkit-modes-have-teams-a-comprehensive-guide)
- Kahoot: [Ways to play](https://kahoot.com/schools/ways-to-play/) · [How to play](https://kahoot.com/how-to-play/)
- Wayground/Quizizz: [Alice Keeler](https://alicekeeler.com/?p=44672) · [Jotform guide](https://www.jotform.com/ai/how-to-create-a-quiz-on-quizizz/) · [SGU ADC](https://adc.sgu.ac.id/?p=595) · [Capterra reviews](https://www.capterra.com/p/207437/Quizizz/reviews/?page=19) · [Quizizz is now Wayground](https://formswrite.com/blog/quizizz-is-now-wayground)
- Teknikal: [WebSocket with FastAPI](https://websocket.org/guides/frameworks/fastapi/) · [Scaling WebSockets with Redis](https://medium.com/@nandagopal05/scaling-websockets-with-pub-sub-using-python-redis-fastapi-b16392ffe291) · [Flask-SocketIO vs FastAPI](https://dev.to/deepak_mishra_35863517037/modern-alternatives-flask-socketio-vs-fastapi-and-quart-5gh6) · [Phaser vs PixiJS (cortance)](https://cortance.com/answers/phaser-js/phaser-js-vs-pixijs-which-is-better-for-2d-web-games) · [Phaser vs PixiJS vs Kaboom](https://www.pistack.xyz/posts/2026-08-18-phaser-vs-pixijs-vs-kaboom-javascript-game-engine-comparison/) · [Lottie vs Rive (Callstack)](https://callstack.com/blog/lottie-vs-rive-optimizing-mobile-app-animation) · [LottieFiles or Rive](https://lottiefiles.com/blog/lottie-animations/lottiefiles-or-rive)
- Undang-undang: [MCMC codes (Allen & Gledhill)](https://www.allenandgledhill.com/perspectives/publications/bulletins-malaysia/2026/mcmc-issues-risk-mitigation-code-and-child-protection-code-under-the-online-safety-act-2025/) · [Mayer Brown](https://www.mayerbrown.com/zh-hans/insights/publications/2026/07/short-deadlines-significant-penalties-malaysias-online-safety-act-in-focus) · [NST](https://www.nst.com.my/amp/news/nation/2026/05/1451852/online-safety-act-2025-leap-forward-protecting-children)
