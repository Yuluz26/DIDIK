#!/usr/bin/env sh
# Updates DIDIK Main Bersama on the VPS: the latest code, a backup first, a new image, and a check that
# the new server answers. Run from this folder: ./deploy.sh
# Open rooms are saved when the old server stops and come back when the new one starts.
set -eu
cd "$(dirname "$0")"

if [ ! -f .env ]; then
	echo "Tiada .env: salin .env.example ke .env dan isi dahulu." >&2
	exit 1
fi

echo "==> Kod terkini"
git pull --ff-only

if docker compose ps --status running --services 2>/dev/null | grep -qx app; then
	echo "==> Sandaran sebelum kemas kini"
	./backup.sh
fi

echo "==> Bina dan mulakan"
docker compose build --pull app
docker compose up -d --remove-orphans

echo "==> Menunggu pelayan sihat"
tries=0
until [ "$(docker inspect --format '{{.State.Health.Status}}' "$(docker compose ps -q app)")" = "healthy" ]; do
	tries=$((tries + 1))
	if [ "$tries" -gt 40 ]; then
		echo "Pelayan tidak sihat selepas 2 minit. Log terakhir:" >&2
		docker compose logs --tail 60 app >&2
		exit 1
	fi
	sleep 3
done

docker image prune -f >/dev/null
echo "==> Siap: $(grep '^DIDIK_PUBLIC_URL=' .env | cut -d= -f2-)"
