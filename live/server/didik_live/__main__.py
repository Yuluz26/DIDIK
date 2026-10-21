"""`didik-live` (or `python -m didik_live`): runs the whole app on one port.

    didik-live                  http://localhost:8080 on this computer only
    didik-live --lan            also reachable from phones on the same Wi-Fi
"""

from __future__ import annotations

import argparse
import logging
import socket

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


def main() -> None:
    parser = argparse.ArgumentParser(prog="didik-live", description="DIDIK Main Bersama")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--lan", action="store_true", help="dengar pada semua rangkaian (untuk telefon di Wi-Fi yang sama)")
    parser.add_argument("--host", default=None, help="alamat untuk didengar (lalai 127.0.0.1)")
    parser.add_argument("--reload", action="store_true", help="mulakan semula apabila kod Python berubah")
    args = parser.parse_args()

    host = args.host or ("0.0.0.0" if args.lan else "127.0.0.1")
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print(f"\n  DIDIK Main Bersama\n  Buka:  http://localhost:{args.port}")
    if args.lan and (address := lan_address()):
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
