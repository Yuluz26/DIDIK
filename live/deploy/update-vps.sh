#!/usr/bin/env sh
# Updates DIDIK on a VPS set up beside other sites (README.md, "Di sebelah laman lain"): systemd runs the app
# from /opt/didik/live, nginx sends the domain to it. Run from the repository root on your own computer:
#
#   live/deploy/update-vps.sh mpsonline@184.168.120.33
#
# It sends the committed live/ folder, takes a backup, installs and builds the new version beside the running
# one, switches to it and restarts the service, then waits for the health check. If the new version does not
# answer, the old one is put back and started again. Open rooms are saved when the service stops and come
# back when it starts. The other sites on the server are not touched.
set -eu

HOST=${1:?usage: live/deploy/update-vps.sh user@host}
REV=$(git rev-parse --short HEAD)
if [ -n "$(git status --porcelain -- live)" ]; then
	echo "Ada perubahan yang belum di-commit dalam live/: hanya versi yang di-commit dihantar ($REV)." >&2
fi

ARCHIVE=$(mktemp)
git archive --format=tar.gz -o "$ARCHIVE" HEAD live
echo "==> Menghantar $REV ke $HOST"
scp -q "$ARCHIVE" "$HOST:didik-release.tar.gz"
rm -f "$ARCHIVE"

ssh "$HOST" REV="$REV" sh -s <<'REMOTE'
set -eu
D=/opt/didik
health() {
	for i in $(seq 1 40); do
		curl -fsS -m 3 http://127.0.0.1:8090/api/health >/dev/null 2>&1 && return 0
		sleep 1
	done
	return 1
}

echo "==> Sandaran"
sudo -u didik /bin/sh -c "set -a; . /etc/didik/didik.env; exec $D/venv/bin/python -m didik_live.backup /var/lib/didik/backups"

echo "==> Memasang dan membina versi baharu (di sebelah versi yang berjalan)"
rm -rf "$D/next" && mkdir -p "$D/next"
tar -xzf ~/didik-release.tar.gz -C "$D/next"
(cd "$D/next/live/web" && npm ci --no-audit --no-fund --loglevel=error && nice -n 10 npm run build >/dev/null)

echo "==> Menukar versi dan memulakan semula"
rm -rf "$D/previous"
mv "$D/live" "$D/previous"
mv "$D/next/live" "$D/live"
rm -rf "$D/next"
"$D/venv/bin/pip" install -q -c "$D/live/server/constraints.txt" "$D/live/server"
sudo systemctl restart didik-live

if health; then
	echo "$REV" > "$D/REVISION"
	echo "==> Siap: $REV berjalan"
else
	echo "!! Versi baharu tidak menjawab. Log terakhir:" >&2
	sudo journalctl -u didik-live --no-pager -n 40 >&2
	echo "!! Memulihkan versi sebelumnya" >&2
	rm -rf "$D/live" && mv "$D/previous" "$D/live"
	"$D/venv/bin/pip" install -q -c "$D/live/server/constraints.txt" "$D/live/server"
	sudo systemctl restart didik-live
	health && echo "!! Versi sebelumnya berjalan semula ($(cat $D/REVISION))" >&2
	exit 1
fi
REMOTE
