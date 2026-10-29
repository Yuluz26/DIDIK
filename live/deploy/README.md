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
`DIDIK_DOMAIN`, `ACME_EMAIL` serta `DIDIK_UPSTREAM=127.0.0.1:8080` ke persekitaran Caddy
(`sudo systemctl edit caddy`, bahagian `[Service]`, baris `Environment=...`), kemudian
`sudo systemctl restart caddy`. Sandaran: `sudo -u didik /opt/didik/venv/bin/python -m didik_live.backup /var/lib/didik/backups`
(dengan `EnvironmentFile` yang sama, atau `DIDIK_DATA_DIR=/var/lib/didik`).

## 9. Satu proses sahaja

Bilik permainan hidup dalam memori satu proses pelayan. **Jangan** jalankan lebih daripada satu bekas
`app` atau beberapa pekerja uvicorn: telefon kanak-kanak dalam bilik yang sama mesti sampai ke proses yang sama.
Untuk lebih ramai pemain, gunakan VPS yang lebih laju, bukan lebih banyak proses.
