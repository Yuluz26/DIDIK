#!/usr/bin/env sh
# A backup of the database and the uploaded pictures, taken while the server runs: written inside the
# data volume, then copied to ./backups on the VPS. The newest DIDIK_BACKUP_KEEP (14) are kept.
# Run from this folder: ./backup.sh
# Every night at 3am, from `crontab -e`:
#   0 3 * * * /opt/didik/live/deploy/backup.sh >> /var/log/didik-backup.log 2>&1
set -eu
cd "$(dirname "$0")"
docker compose exec -T app python -m didik_live.backup /data/backups
mkdir -p backups
docker compose cp app:/data/backups/. backups/
# the copies here are kept to the same number
keep=$(grep '^DIDIK_BACKUP_KEEP=' .env 2>/dev/null | cut -d= -f2)
keep=${keep:-14}
for pattern in 'didik-live-*.db' 'didik-uploads-*.tar.gz'; do
	ls -1t backups/$pattern 2>/dev/null | tail -n +$((keep + 1)) | xargs -r rm -f
done
