"""`python -m didik_live.backup [FOLDER]`: a backup of the database and the uploaded pictures.

The SQLite database is copied with SQLite's own backup API, which is safe while the server runs (it
writes with WAL), and the pictures go into a .tar.gz beside it. Only the newest DIDIK_BACKUP_KEEP
backups (14 by default) are kept. A PostgreSQL database is left to `pg_dump`; the pictures are still
backed up. Restore: stop the server, put didik-live.db and uploads/ back in DIDIK_DATA_DIR, start it.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tarfile
from datetime import UTC, datetime
from pathlib import Path

from .config import load_settings


def backup(folder: Path, keep: int) -> list[Path]:
    settings = load_settings()
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    made: list[Path] = []

    if settings.database_url.startswith("sqlite:///"):
        source = Path(settings.database_url.removeprefix("sqlite:///"))
        if source.is_file():
            target = folder / f"didik-live-{stamp}.db"
            with sqlite3.connect(source) as live, sqlite3.connect(target) as copy:
                live.backup(copy)
            # a copy that will not open is no backup at all
            with sqlite3.connect(target) as copy:
                if copy.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise RuntimeError(f"Salinan {target.name} rosak")
            made.append(target)
    else:
        print("Pangkalan data bukan SQLite: sandarkan dengan pg_dump. Gambar tetap disandarkan.", file=sys.stderr)

    if settings.upload_dir.is_dir():
        target = folder / f"didik-uploads-{stamp}.tar.gz"
        with tarfile.open(target, "w:gz") as archive:
            archive.add(settings.upload_dir, arcname="uploads")
        made.append(target)

    for pattern in ("didik-live-*.db", "didik-uploads-*.tar.gz"):
        for old in sorted(folder.glob(pattern), reverse=True)[keep:]:
            old.unlink()
    return made


def main() -> None:
    settings = load_settings()
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else settings.data_dir / "backups"
    keep = max(1, int(os.environ.get("DIDIK_BACKUP_KEEP") or 14))
    for path in backup(folder, keep):
        print(f"{path} ({path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
