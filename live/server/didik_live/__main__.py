"""`didik-live` (or `python -m didik_live`): runs the whole app on one port.

    didik-live                          http://localhost:8080 on this computer only
    didik-live --lan                    also reachable from phones on the same Wi-Fi
    didik-live --reset-link EMEL        prints a link to choose a new password, then exits
"""

from __future__ import annotations

import argparse
import logging
import os
import socket
import sys

import uvicorn


def lan_address() -> str | None:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("10.255.255.255", 1))
        return probe.getsockname()[0]
    except OSError:
        return None
    finally:
        probe.close()


def print_reset_link(email: str, port: int) -> int:
    """For a server without email: whoever runs it can hand a parent a reset link."""
    from sqlalchemy import func, select

    from . import passwords
    from .config import load_settings
    from .db import Database
    from .models import User

    settings = load_settings()
    database = Database(settings.database_url)
    database.create_all()
    with database.sessions() as db:
        user = db.scalar(select(User).where(func.lower(User.email) == email.strip().lower()))
        if user is None:
            print(f"Tiada akaun dengan emel {email}.", file=sys.stderr)
            return 1
        base = settings.public_url or f"http://localhost:{port}"
        print(f"Pautan untuk {user.email} (sah {passwords.RESET_MINUTES} minit, sekali guna):")
        print(passwords.link(base, passwords.issue(db, user)))
    return 0


def raise_open_files(want: int = 65536) -> None:
    """Every child's phone is one open socket. Many Linux servers allow a process 1024 open files by
    default, which a school of a thousand children would use up; raise it as far as the system lets."""
    try:
        import resource
    except ImportError:  # Windows has no such limit
        return
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    target = want if hard == resource.RLIM_INFINITY else min(want, hard)
    if soft < target:
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (target, hard))
        except (ValueError, OSError):
            pass


def main() -> None:
    parser = argparse.ArgumentParser(prog="didik-live", description="DIDIK Main Bersama")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--lan", action="store_true", help="dengar pada semua rangkaian (untuk telefon di Wi-Fi yang sama)")
    parser.add_argument("--host", default=None, help="alamat untuk didengar (lalai 127.0.0.1)")
    parser.add_argument("--reload", action="store_true", help="mulakan semula apabila kod Python berubah")
    parser.add_argument("--reset-link", metavar="EMEL", help="cetak pautan untuk memilih kata laluan baharu, kemudian keluar")
    args = parser.parse_args()
    if args.reset_link:
        sys.exit(print_reset_link(args.reset_link, args.port))

    host = args.host or ("0.0.0.0" if args.lan else "127.0.0.1")
    raise_open_files()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print(f"\n  DIDIK Main Bersama\n  Buka:  http://localhost:{args.port}")
    if args.lan and (address := lan_address()):
        # Room links and QR codes point here, so a phone can scan them even when the host's own
        # browser opened the site as localhost.
        os.environ.setdefault("DIDIK_PUBLIC_URL", f"http://{address}:{args.port}")
        print(f"  Telefon di Wi-Fi yang sama:  http://{address}:{args.port}")
    print("  Akaun demo: demo@didik.test / main-bersama\n")

    uvicorn.run(
        "didik_live.app:create_app",
        factory=True,
        host=host,
        port=args.port,
        reload=args.reload,
        log_level="warning",
        ws_max_size=16_384,
    )


if __name__ == "__main__":
    main()
