"""`didik-live` (or `python -m didik_live`): runs the whole app on one port.

    didik-live                          http://localhost:8080 on this computer only
    didik-live --lan                    also reachable from phones on the same Wi-Fi
    didik-live --reset-link EMEL        prints a link to choose a new password, then exits
    didik-live --admin-path             prints a new secret address for the control room, then exits
    didik-live --admin-test-mail        sends a test email to the owner with the SMTP settings, then exits

On a server (DIDIK_ENV=production) it listens on DIDIK_HOST:DIDIK_PORT behind a reverse proxy, refuses to
start while a setting is unsafe, and logs with times to standard output (journald or Docker keep it).
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


def print_admin_path() -> int:
    """A secret for DIDIK_ADMIN_PATH: 32 random characters, so the control room's address cannot be guessed."""
    import secrets

    print(secrets.token_urlsafe(24))
    return 0


def test_admin_mail() -> int:
    """Sends one email to the owner through the real SMTP settings and says what happened, so a wrong
    password or a blocked server shows up now and not when the first sign-in code never arrives."""
    from .config import load_settings
    from .mailer import Mailer

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = load_settings()
    if settings.admin is None:
        print("DIDIK_ADMIN_EMAIL dan DIDIK_ADMIN_PATH belum ditetapkan.", file=sys.stderr)
        return 1
    if settings.mail is None:
        print("DIDIK_SMTP_HOST belum ditetapkan.", file=sys.stderr)
        return 1
    sent = Mailer(settings.mail).send(settings.admin.email, "Ujian emel DIDIK", "Jika anda membaca ini, emel kod log masuk admin akan sampai.\n")
    print(f"Emel ujian dihantar ke {settings.admin.email}." if sent else "Emel TIDAK dihantar. Lihat ralat di atas.")
    return 0 if sent else 1


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
    parser.add_argument("--port", type=int, default=int(os.environ.get("DIDIK_PORT") or 8080))
    parser.add_argument("--lan", action="store_true", help="dengar pada semua rangkaian (untuk telefon di Wi-Fi yang sama)")
    parser.add_argument("--host", default=os.environ.get("DIDIK_HOST") or None, help="alamat untuk didengar (lalai 127.0.0.1)")
    parser.add_argument("--reload", action="store_true", help="mulakan semula apabila kod Python berubah")
    parser.add_argument("--reset-link", metavar="EMEL", help="cetak pautan untuk memilih kata laluan baharu, kemudian keluar")
    parser.add_argument("--admin-path", action="store_true", help="cetak alamat rahsia baharu untuk bilik kawalan admin, kemudian keluar")
    parser.add_argument("--admin-test-mail", action="store_true", help="hantar emel ujian kepada admin dengan tetapan SMTP, kemudian keluar")
    args = parser.parse_args()
    if args.admin_path:
        sys.exit(print_admin_path())
    if args.admin_test_mail:
        sys.exit(test_admin_mail())
    if args.reset_link:
        sys.exit(print_reset_link(args.reset_link, args.port))

    host = args.host or ("0.0.0.0" if args.lan else "127.0.0.1")
    raise_open_files()

    from .config import load_settings

    settings = load_settings()
    if settings.production:
        serve_production(settings, host, args.port)
        return

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print(f"\n  DIDIK Main Bersama\n  Buka:  http://localhost:{args.port}")
    if args.lan and (address := lan_address()):
        # Room links and QR codes point here, so a phone can scan them even when the host's own
        # browser opened the site as localhost.
        os.environ.setdefault("DIDIK_PUBLIC_URL", f"http://{address}:{args.port}")
        print(f"  Telefon di Wi-Fi yang sama:  http://{address}:{args.port}")
    if settings.seed_demo:
        print("  Akaun demo: demo@didik.test / main-bersama")
    print()

    uvicorn.run(
        "didik_live.app:create_app",
        factory=True,
        host=host,
        port=args.port,
        reload=args.reload,
        log_level="warning",
        ws_max_size=16_384,
    )


def serve_production(settings, host: str, port: int) -> None:
    """A public server: stop with a clear message while a setting is unsafe, then serve behind the proxy."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stdout)
    log = logging.getLogger("didik")
    problems = settings.problems()
    if problems:
        for problem in problems:
            log.error("Tetapan: %s", problem)
        log.error("Pelayan tidak dimulakan. Betulkan tetapan di atas (lihat live/deploy/.env.example).")
        sys.exit(2)
    log.info("DIDIK Main Bersama di %s (mendengar %s:%s)", settings.public_url, host, port)
    uvicorn.run(
        "didik_live.app:create_app",
        factory=True,
        host=host,
        port=port,
        log_level="info",
        # Children's addresses are not written to the log on every request; errors still are.
        access_log=os.environ.get("DIDIK_ACCESS_LOG", "").strip().lower() in {"1", "true", "yes", "on"},
        # The real address comes from the proxy in front (FORWARDED_ALLOW_IPS names who may send it).
        proxy_headers=True,
        server_header=False,
        ws_max_size=16_384,
        # Time for open rooms to be saved and sockets closed when the service stops.
        timeout_graceful_shutdown=20,
    )


if __name__ == "__main__":
    main()
