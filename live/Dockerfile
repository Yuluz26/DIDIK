# syntax=docker/dockerfile:1
# DIDIK Main Bersama: the web app built, then served with the Python server, as one small image.
#
#   docker build -t didik-live live/          (from the repository root)
#
# The server keeps open rooms in its own memory, so run exactly one container of it. Its database and
# the uploaded pictures live in /data (a volume). See live/deploy/README.md.

FROM node:22-bookworm-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build


FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

COPY server/pyproject.toml server/constraints.txt ./server/
COPY server/didik_live ./server/didik_live
RUN pip install -c server/constraints.txt "./server[postgres]" \
    && rm -rf server/build server/*.egg-info

COPY --from=web /web/build ./web/build

RUN useradd --system --uid 10001 --home-dir /app --shell /usr/sbin/nologin didik \
    && mkdir -p /data \
    && chown didik:didik /data

ENV DIDIK_ENV=production \
    DIDIK_HOST=0.0.0.0 \
    DIDIK_PORT=8080 \
    DIDIK_DATA_DIR=/data \
    DIDIK_WEB_DIR=/app/web/build \
    FORWARDED_ALLOW_IPS=*

USER didik
VOLUME ["/data"]
EXPOSE 8080
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/api/health', timeout=4).status == 200 else 1)"]

CMD ["didik-live"]
