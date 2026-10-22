# DIDIK Main Bersama

Permainan kuiz secara langsung untuk kanak-kanak. Ibu bapa atau guru menulis soalan sendiri, buka satu
bilik, dan kanak-kanak masuk dengan pautan, kod QR atau kod 6 digit. Tiada akaun untuk kanak-kanak, hanya
nama samaran.

- **`server/`**: Python (FastAPI). API, bilik masa nyata melalui WebSocket, dua belas permainan,
  pangkalan data SQLite.
- **`web/`**: SvelteKit (TypeScript). Skrin ibu bapa, skrin hos dan skrin kanak-kanak. Selepas dibina,
  pelayan Python yang menghidangkannya, jadi semuanya berjalan pada satu port.

## Dua belas permainan

Semua permainan boleh dimainkan dengan mana-mana kuiz, oleh mana-mana kelas; guru atau ibu bapa pilih
ikut citarasa. Empat yang terakhir dalam 3D (three.js, dimuat hanya bila permainan itu dibuka; tanpa
WebGL ia tetap boleh dimainkan sebagai kuiz), dan biliknya memakai warna yang lebih gelap, sepadan
dengan dunianya pada waktu senja dan malam.

| Permainan | Cara main |
| --- | --- |
| Lumba Sampan | Semua jawab soalan yang sama. Betul dan laju, sampan maju lebih jauh. |
| Lompat! | Lompat ke pulau jawapan; pulau yang salah tenggelam. Habis hati jadi ikan, dua jawapan betul berturut-turut kembali ke darat. |
| Pulau Harta Karun | Jawapan betul memberi penyodok untuk menggali harta di pulau sendiri. |
| Hutan Misteri | Berjalan dalam hutan, buka peti soalan, kumpul 5 kunci, cari pintu keluar. |
| Pasukan Warna | Dua pasukan menawan petak pulau dengan bendera daripada jawapan betul. |
| Kampung Kita | Semua bina satu kampung bersama dan hias padangnya. Tiada yang kalah. |
| Teka Gambar | Jawapan betul membuka petak gambar rahsia. Teka awal, mata lebih banyak. |
| Kebun Ajaib | Jawapan betul memberi air. Tanam, siram dan tuai untuk dapat syiling. |
| Litar Kart (3D) | Lumba tiga pusingan. Betul dan laju, kart memecut; tiga betul berturut-turut menyalakan nitro. |
| Sepakan Penalti (3D) | Harimau lawan Penyu, satu sepakan setiap pasukan bagi setiap soalan. Peratus jawapan betul yang lebih tinggi menjaringkan gol. |
| Peti Lanun (3D) | Jawapan betul membuka satu daripada tiga peti: emas, ganda dua, rampas atau tukar emas dengan kapal lain. Kapal yang dirompak dapat perisai seketika. |
| Menara 118 (3D) | Seisi kelas membina satu menara setinggi Merdeka 118 (679 m). Blok yang diletakkan tepat di tengah menaikkan menara lebih tinggi. |

Jenis soalan: pilihan tunggal, pilih semua yang betul, betul atau salah, taip jawapan, nombor, susun
turutan, padankan, dan isi tempat kosong.

## Keperluan

- Python 3.11 atau lebih baharu
- Node.js 20.19+ atau 22.12+ (hanya untuk membina antara muka web)

## Pasang (sekali sahaja)

macOS atau Linux:

```sh
cd live/server
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cd ../web
npm ci
npm run build
```

Windows (PowerShell):

```powershell
cd live\server
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .

cd ..\web
npm ci
npm run build
```

Jika PowerShell menolak skrip `Activate.ps1`, jalankan sekali `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Jalankan

```sh
cd live/server
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
didik-live
```

Buka <http://localhost:8080>, pilih **Ibu bapa**, kemudian **Guna akaun demo**
(`demo@didik.test` / `main-bersama`). Akaun demo dan lapan kuiz contoh (tiga daripadanya bertaraf
Tingkatan) dicipta sendiri pada kali pertama; kuiz contoh baharu ditambah ke akaun demo yang sedia ada
bila pelayan dimulakan.
Akaun ini untuk mencuba di komputer sendiri sahaja.

## Main dengan telefon di Wi-Fi yang sama

```sh
didik-live --lan
```

Terminal akan menunjukkan alamat seperti `http://192.168.1.20:8080`. Pautan bilik dan kod QR pada skrin hos
akan menggunakan alamat ini, jadi telefon boleh terus mengimbas kod QR walaupun skrin hos dibuka sebagai
`localhost`. Jika Windows atau macOS bertanya tentang firewall, benarkan untuk rangkaian peribadi.

## Mencuba seorang diri

1. Log masuk akaun demo, pilih satu kuiz, tekan **Main bersama**, kemudian pilih permainan.
2. Pada skrin hos, tekan **Tambah bot** beberapa kali. Bot latihan menjawab dan bermain seperti kanak-kanak.
3. Buka pautan bilik dalam tetingkap peribadi (incognito) atau di telefon untuk bermain sebagai seorang
   kanak-kanak. Sementara menunggu, semua berada di dataran: ketik dataran (atau tekan anak panah) untuk
   berjalan, dan skrin hos menunjukkan semua orang bergerak. Bot pun berjalan sendiri.
4. Tekan **Mula**.

## Menulis kuiz sendiri

**Kuiz saya → Kuiz baharu.** Setiap soalan boleh ada gambar dan had masa sendiri. Simpan dengan butang
**Simpan** atau Ctrl+S. Jika ada yang perlu dibetulkan, mesejnya muncul di sebelah medan berkenaan. Kuiz contoh
boleh disalin dan diubah.

Setiap permainan memerlukan jenis soalan tertentu. Contohnya Lompat! hanya menggunakan soalan Betul atau salah,
dan Pilihan tunggal dengan 2 hingga 4 jawapan. Halaman pilih permainan menerangkan jika kuiz belum sesuai.

## Tetapan (pilihan)

| Pembolehubah | Lalai | Kegunaan |
| --- | --- | --- |
| `DIDIK_DATA_DIR` | `live/server/data` | Tempat pangkalan data dan gambar yang dimuat naik |
| `DIDIK_DATABASE_URL` | SQLite dalam `DIDIK_DATA_DIR` | Contoh PostgreSQL: `postgresql+psycopg://...` (pasang `pip install -e ".[postgres]"`) |
| `DIDIK_PUBLIC_URL` | kosong | Alamat untuk pautan bilik dan kod QR; `--lan` mengisinya sendiri |
| `DIDIK_SEED_DEMO` | `1` | Cipta akaun demo dan kuiz contoh. Tetapkan `0` pada pelayan sebenar |
| `DIDIK_ALLOW_BOTS` | `1` | Benarkan bot latihan |
| `DIDIK_SECURE_COOKIES` | `0` | Tetapkan `1` apabila laman dihidangkan melalui https |
| `DIDIK_WEB_DIR` | `live/web/build` | Folder antara muka yang telah dibina |

Pilihan arahan: `didik-live --port 8090`, `--host 0.0.0.0`, `--reload` (mula semula apabila kod Python berubah).

## Pembangunan

Antara muka dengan muat semula segera: jalankan `didik-live`, kemudian dalam `live/web` jalankan
`npm run dev` dan buka <http://localhost:5173>. Vite menghantar `/api`, `/ws` dan `/uploads` ke pelayan Python.

Ujian:

```sh
cd live/server && pip install -e ".[dev]" && pytest
cd live/web && npm run check
```

## Privasi dan keselamatan

- Kanak-kanak hanya memilih haiwan, warna dan nama samaran. Tiada sembang bebas; mereka hanya boleh
  menghantar pelekat.
- Jawapan betul tidak pernah dihantar ke peranti kanak-kanak sebelum disemak di pelayan.
- Gambar yang dimuat naik dibaca semula dan disimpan sebagai WebP, jadi metadata seperti lokasi dibuang.
- Hos boleh mengunci bilik, menggunakan bilik menunggu, dan mengeluarkan pemain.
