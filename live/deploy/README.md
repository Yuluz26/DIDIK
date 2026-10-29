# Deploy DIDIK Main Bersama ke VPS

Panduan ini memasang DIDIK pada satu VPS Linux dengan **https automatik** (Caddy + Let's Encrypt),
sandaran harian dan kemas kini satu arahan.

| Fail | Kegunaan |
| --- | --- |
| [`../Dockerfile`](../Dockerfile) | Imej aplikasi: antara muka dibina, kemudian dihidangkan oleh pelayan Python sebagai pengguna bukan root |
| [`compose.yaml`](compose.yaml) | Aplikasi + Caddy (https, WebSocket, mampatan), volum data, had fail terbuka, log berputar |
| [`Caddyfile`](Caddyfile) | Proksi https; tiada log akses (privasi kanak-kanak) |
| [`.env.example`](.env.example) | Semua tetapan; salin ke `.env` |
| [`deploy.sh`](deploy.sh) | Kemas kini: sandaran, bina, mula, tunggu sehingga sihat |
| [`backup.sh`](backup.sh) | Sandaran pangkalan data dan gambar semasa pelayan berjalan |
| [`didik-live.service`](didik-live.service) | Unit systemd untuk VPS tanpa Docker |
| [`nginx-didik.conf`](nginx-didik.conf) | Laman nginx untuk VPS yang sudah ada nginx dan laman lain |
| [`update-vps.sh`](update-vps.sh) | Kemas kini VPS tanpa Docker dari komputer anda, dengan pemulihan automatik |

## 1. Sediakan VPS

- **Linux** (Ubuntu 22.04/24.04 atau Debian 12), sekurang-kurangnya **1 vCPU, 1 GB RAM, 10 GB cakera**.
  Satu proses melayan kira-kira 1000 telefon serentak (diuji: ~60% satu teras semasa semua masuk,
  ~240 MB RAM).
- **Domain**: rekod `A` (dan `AAAA` jika ada IPv6) menghala ke IP VPS, contohnya `didik.contoh.my`.
- **Firewall**: buka port 22, 80 dan 443 sahaja.

```sh
sudo apt update && sudo apt install -y git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER     # log keluar dan masuk semula selepas ini
sudo ufw allow OpenSSH && sudo ufw allow 80 && sudo ufw allow 443/tcp && sudo ufw allow 443/udp && sudo ufw enable
```

## 2. Pasang

```sh
sudo mkdir -p /opt/didik && sudo chown $USER /opt/didik
git clone <alamat-repositori> /opt/didik
cd /opt/didik/live/deploy
cp .env.example .env
nano .env                           # DIDIK_DOMAIN, DIDIK_PUBLIC_URL, ACME_EMAIL, SMTP
chmod +x deploy.sh backup.sh
docker compose up -d --build
docker compose ps                   # "app" mesti "healthy"
```

Buka `https://didik.contoh.my`. Sijil https diambil sendiri pada lawatan pertama (beberapa saat).

Pelayan **enggan bermula** jika tetapan tidak selamat, dan menerangkan sebabnya dalam log:

```sh
docker compose logs app
```

Contoh: `DIDIK_PUBLIC_URL` kosong atau bukan `https://`, kuki tanpa Secure, atau akaun demo dihidupkan.

## 3. Apa yang berbeza pada pelayan sebenar

`DIDIK_ENV=production` (ditetapkan oleh `compose.yaml` dan unit systemd):

- **Tiada akaun demo.** Kuiz contoh tetap ada untuk semua ibu bapa, dimiliki akaun "Perpustakaan DIDIK"
  yang tiada kata laluan dan tidak boleh diset semula.
- **Kuki sesi https sahaja**, dan `Strict-Transport-Security` setahun.
- **Bot latihan dimatikan** (hidupkan dengan `DIDIK_ALLOW_BOTS=1`).
- **Log bertarikh** ke stdout (`docker compose logs`), tanpa alamat IP setiap permintaan
  (`DIDIK_ACCESS_LOG=1` untuk menghidupkannya).
- Alamat sebenar setiap pelawat dibaca daripada Caddy, jadi had permintaan dikira bagi setiap pelawat.
- Bilik yang terbuka disimpan semasa pelayan berhenti dan dibuka semula selepas kemas kini; telefon
  menyambung semula sendiri.

## 4. Emel

Tanpa SMTP, pautan set semula kata laluan ditulis dalam log (`docker compose logs app`). Untuk emel sebenar,
isi `DIDIK_SMTP_*` dalam `.env` (contoh: Brevo, Mailgun, Amazon SES, atau SMTP Google Workspace) dan jalankan
`docker compose up -d`. Pentadbir juga boleh mencetak pautan untuk seorang ibu bapa:

```sh
docker compose exec app didik-live --reset-link ibu@contoh.my
```

## 5. Sandaran

```sh
./backup.sh
```

Menyalin pangkalan data (selamat semasa pelayan berjalan, disemak integritinya) dan gambar yang dimuat naik
ke volum data dan ke `deploy/backups/` pada VPS. Hanya 14 terkini disimpan (`DIDIK_BACKUP_KEEP`).

Setiap malam jam 3 pagi (`crontab -e`):

```cron
0 3 * * * /opt/didik/live/deploy/backup.sh >> /var/log/didik-backup.log 2>&1
```

Salin juga `deploy/backups/` ke luar VPS (contohnya `rclone` ke storan awan), kerana sandaran pada mesin yang
sama tidak melindungi daripada kehilangan VPS.

**Pulihkan:**

```sh
docker compose stop app
docker compose cp backups/didik-live-YYYYMMDD-HHMMSS.db app:/data/didik-live.db
docker compose run --rm --entrypoint sh app -c "rm -f /data/didik-live.db-wal /data/didik-live.db-shm"
tar -xzf backups/didik-uploads-YYYYMMDD-HHMMSS.tar.gz -C /tmp && docker compose cp /tmp/uploads/. app:/data/uploads/
docker compose start app
```

## 6. Kemas kini

```sh
cd /opt/didik/live/deploy && ./deploy.sh
```

Menarik kod terkini, membuat sandaran, membina imej baharu, memulakannya dan menunggu sehingga ia sihat.
Jika pelayan baharu tidak sihat dalam 2 minit, log terakhirnya dipaparkan.

## 7. Pemantauan

- `GET /api/health` menjawab `200 {"ok": true, "database": true, "rooms": N}` selagi pelayan dan pangkalan
  datanya menjawab, dan `503` jika pangkalan data gagal. Docker memeriksanya setiap 30 saat; sambungkan juga
  ke pemantau masa hidup luaran (UptimeRobot, Better Stack) dengan `https://didik.contoh.my/api/health`.
- Log: `docker compose logs -f app` (berputar sendiri, 5 × 10 MB).

## 8. Tanpa Docker (systemd + Caddy)

```sh
sudo apt install -y python3.12-venv caddy nodejs npm   # Node 20+ untuk membina antara muka
sudo useradd --system --home /var/lib/didik --shell /usr/sbin/nologin didik
sudo mkdir -p /var/lib/didik /etc/didik && sudo chown didik:didik /var/lib/didik
cd /opt/didik/live
python3.12 -m venv /opt/didik/venv
/opt/didik/venv/bin/pip install -c server/constraints.txt ./server
npm ci --prefix web && npm run build --prefix web
sudo cp deploy/.env.example /etc/didik/didik.env && sudo nano /etc/didik/didik.env
sudo chmod 640 /etc/didik/didik.env && sudo chown root:didik /etc/didik/didik.env
sudo cp deploy/didik-live.service /etc/systemd/system/ && sudo systemctl enable --now didik-live
```

Caddy di mesin yang sama: salin `deploy/Caddyfile` ke `/etc/caddy/Caddyfile`, dan tambah
`DIDIK_DOMAIN`, `ACME_EMAIL` serta `DIDIK_UPSTREAM=127.0.0.1:8090` ke persekitaran Caddy
(`sudo systemctl edit caddy`, bahagian `[Service]`, baris `Environment=...`), kemudian
`sudo systemctl restart caddy`. Sandaran: `sudo -u didik /opt/didik/venv/bin/python -m didik_live.backup /var/lib/didik/backups`
(dengan `EnvironmentFile` yang sama, atau `DIDIK_DATA_DIR=/var/lib/didik`).

## 9. Di sebelah laman lain (nginx sedia ada)

Pada VPS yang nginx-nya sudah menghidangkan laman lain pada port 80/443 (contohnya laman Laravel), **jangan**
jalankan `compose.yaml` (Caddy akan berebut port itu). DIDIK berjalan sebagai perkhidmatan systemd pada
`127.0.0.1:8090` dan nginx sedia ada menghantar satu domain kepadanya. Laman lain tidak disentuh.

Persediaan sekali (seperti di `didik.engineprofit.io`):

1. DNS: rekod **A** untuk subdomain → IP VPS (tanpa AAAA jika nginx tidak mendengar IPv6).
2. Pasang seperti bahagian 8 (pengguna `didik`, `/opt/didik/venv`, `/var/lib/didik`, `/etc/didik/didik.env`),
   dengan `DIDIK_PORT=8090` dan `DIDIK_PUBLIC_URL=https://domain-anda`.
3. nginx: [`nginx-didik.conf`](nginx-didik.conf) (tukar `server_name`), kemudian
   `sudo nginx -t && sudo systemctl reload nginx` dan `sudo certbot --nginx -d domain-anda --redirect`.
   Setiap `location` menetapkan semua pengepalanya sendiri: nginx membuang `proxy_set_header` peringkat
   `server` dalam `location` yang ada pengepala sendiri, dan tanpa `Host` yang betul log masuk dan soket
   permainan ditolak.
4. Sandaran malam: `/etc/cron.d/didik-backup`, jam 3 pagi, sebagai pengguna `didik`, ke `/var/lib/didik/backups`.

Kemas kini, dari komputer anda (akar repositori):

```sh
live/deploy/update-vps.sh mpsonline@184.168.120.33
```

Ia menghantar versi yang di-commit, membuat sandaran, membina di sebelah versi yang berjalan, menukar,
memulakan semula dan menunggu pemeriksaan kesihatan. Jika versi baharu tidak menjawab, versi lama dipulihkan.
Log: `sudo journalctl -u didik-live -f`.

### Kemas kini automatik dari GitHub

Setiap kali cawangan utama (`ccr-5bfecad5-9qrt47`) menerima perubahan dalam `live/` dan semakan CI lulus,
[`didik-live-deploy.yml`](../../.github/workflows/didik-live-deploy.yml) menjalankan `update-vps.sh` yang sama
dari GitHub, kemudian memeriksa `https://didik.engineprofit.io/api/health`. Boleh juga dijalankan sendiri:
**Actions → DIDIK Live · Deploy to the VPS → Run workflow**.

Persediaan sekali, dari komputer anda:

```sh
ssh-keygen -t ed25519 -N "" -C didik-github-deploy -f ~/.ssh/didik_deploy
ssh-copy-id -i ~/.ssh/didik_deploy.pub mpsonline@184.168.120.33
ssh-keyscan 184.168.120.33
```

Kemudian di GitHub, **Settings → Secrets and variables → Actions → New repository secret**:

| Rahsia | Isi |
| --- | --- |
| `DIDIK_VPS_SSH_KEY` | Kandungan `~/.ssh/didik_deploy` (kunci peribadi, bukan `.pub`) |
| `DIDIK_VPS_KNOWN_HOSTS` | Output `ssh-keyscan` di atas, supaya GitHub hanya bercakap dengan pelayan ini |

Kunci ini untuk GitHub sahaja. Untuk menariknya semula, padam barisnya dalam `~/.ssh/authorized_keys` pada
VPS. Pelayan atau domain lain: pembolehubah repositori `DIDIK_VPS` (`pengguna@hos`) dan `DIDIK_URL`.

## 10. Bilik kawalan admin (untuk pemilik laman)

Papan pemuka peribadi: ibu bapa baharu, kuiz, bilik dan murid yang masuk secara langsung, notifikasi, log aktiviti, dan
urus ibu bapa, kuiz serta notifikasi. Ia **tidak wujud** sehingga anda menetapkan emel dan alamat rahsia; alamat lain
menunjukkan laman biasa.

Persediaan sekali (pada VPS, fail yang sama dengan SMTP: `/etc/didik/didik.env` atau `.env` Docker):

```sh
sudo -u didik /opt/didik/venv/bin/didik-live --admin-path       # cetak alamat rahsia baharu
sudo nano /etc/didik/didik.env
#   DIDIK_ADMIN_EMAIL=emel-anda@contoh.my
#   DIDIK_ADMIN_PATH=<alamat yang dicetak>
#   DIDIK_SMTP_HOST=smtp.office365.com   DIDIK_SMTP_PORT=587   DIDIK_SMTP_SECURITY=starttls
#   DIDIK_SMTP_USER=emel-anda@contoh.my  DIDIK_SMTP_PASSWORD=...  DIDIK_MAIL_FROM=emel-anda@contoh.my
sudo -u didik /bin/sh -c 'set -a; . /etc/didik/didik.env; /opt/didik/venv/bin/didik-live --admin-test-mail'
sudo cp live/deploy/nginx-didik.conf /etc/nginx/sites-available/didik && sudo nginx -t && sudo systemctl reload nginx
sudo systemctl restart didik-live
```

Buka `https://domain-anda/<alamat-rahsia>`, masukkan emel, kemudian kod 6 digit yang sampai ke peti masuk anda.

- **Siapa boleh masuk:** hanya emel yang ditetapkan, dan hanya dengan kod. Kod sah 10 minit, 5 percubaan, sekali guna,
  dan hanya hash disimpan. Permintaan kod dan percubaan dihadkan. Sesi 12 jam (4 jam tanpa aktiviti), kuki
  `HttpOnly`, `SameSite=Strict`, hanya dihantar ke alamat rahsia. Setiap log masuk diemel kepada anda.
- **Alamat rahsia ialah lapisan pertama, bukan satu-satunya:** log nginx menyimpan alamat itu, jadi jangan kongsi log.
  Jika bocor, tukar `DIDIK_ADMIN_PATH` dan mulakan semula `didik-live` (semua sesi tamat).
- **Emel Outlook / Microsoft 365:** kata laluan akaun biasa sering ditolak untuk SMTP. Guna "kata laluan aplikasi" atau minta
  pentadbir akaun menghidupkan "Authenticated SMTP" untuk peti ini. `--admin-test-mail` memberitahu sekarang jika ia tidak
  berfungsi, bukan apabila kod pertama tidak sampai. Jika Microsoft menutup SMTP kata laluan sepenuhnya, gunakan
  penyedia SMTP lain (Brevo, Mailgun, SES) untuk emel ini.
- **Privasi kanak-kanak:** murid direkodkan dengan nama samaran sahaja (tanpa alamat IP atau peranti), dan log dipadam
  selepas 90 hari. Tiada apa-apa direkodkan jika bilik kawalan tidak dihidupkan.

## 11. Satu proses sahaja

Bilik permainan hidup dalam memori satu proses pelayan. **Jangan** jalankan lebih daripada satu bekas
`app` atau beberapa pekerja uvicorn: telefon kanak-kanak dalam bilik yang sama mesti sampai ke proses yang sama.
Untuk lebih ramai pemain, gunakan VPS yang lebih laju, bukan lebih banyak proses.
