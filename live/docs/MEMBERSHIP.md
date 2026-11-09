# Keahlian DIDIK Live

## Pelan dan bayaran

Harga rasmi disimpan dalam `server/didik_live/membership.py` dalam sen: Free RM0, Premium RM14.90/RM149.00 dan Family RM24.90/RM249.00. Halaman awam dan halaman ibu bapa membaca harga melalui API yang sama. Tiada caj automatik.

Pembayaran QR ialah proses manual. Pemilik memuat naik PNG QR dan nama penerima di **Bilik kawalan → Keahlian → Tetapan QR**. Selagi QR belum disediakan, butang memilih pelan berbayar dilumpuhkan. Ibu bapa memilih pelan dan tempoh, mendapat rujukan unik, membayar jumlah tepat, lalu menghantar bukti ke WhatsApp `+60139558132`. Permintaan kekal `pending` sehingga pemilik menyemak bukti dan menekan **Sahkan bayaran**. Hanya semakan itu mencipta tempoh langganan berbayar. Permintaan yang telah disemak tidak boleh disahkan kali kedua.

QR disimpan di `DIDIK_DATA_DIR/billing/` dan disertakan dalam sandaran. Sandaran pangkalan data mesti dibuat sebelum deploy. Jangan letak QR atau bukti bayaran dalam repo.

## Keahlian dan akses

Langganan berbayar, grant admin, akses khas dan permintaan bayaran ialah rekod berasingan. Grant tidak mencipta transaksi palsu atau hasil jualan. Keputusan grant admin yang paling baharu mengatasi grant terdahulu; langganan berbayar yang sah terus memberi hak yang telah dibeli. Selepas grant tamat, pelan berbayar yang masih sah atau Free dipulihkan. Proses berkala menanda rekod tamat tempoh; pemeriksaan akses sendiri turut menyemak waktu semasa.

Hanya pemilik yang masuk melalui alamat rahsia dan OTP admin boleh mengubah grant, akses khas, tetapan QR atau menyemak bayaran. Setiap perubahan keahlian direkod dalam `membership_audit`. Akses ke permainan premium diperiksa di endpoint penciptaan bilik. Tetamu masih boleh masuk bilik melalui kod atau QR tanpa akaun dan tanpa langganan.

Profil anak dimiliki akaun ibu bapa. Free/Premium membenarkan satu profil baharu; Family tiga. Ketika turun pelan, profil tambahan kekal dalam pangkalan data, dan ibu bapa atau admin memilih satu profil aktif.

## Had pelaksanaan semasa

Projek produksi DIDIK Live menggunakan FastAPI dan SvelteKit; aplikasi Laravel dalam repo ini ialah laman kuiz berasingan dan tidak berkongsi sesi atau pengguna dengan DIDIK Live. Keahlian ini berkuat kuasa pada DIDIK Live. Pengesahan emel, laporan kemajuan pembelajaran terperinci setiap anak, dan pengelasan kandungan Tahun 4/5/6 belum disambungkan kepada sumber data permainan sedia ada. Jangan mengiklankan ciri tersebut sebagai tersedia sehingga aliran data dan ujian lengkap. Tiada integrasi gateway atau caj automatik.
