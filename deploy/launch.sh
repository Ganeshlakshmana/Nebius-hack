#!/usr/bin/env bash
set -euo pipefail
cd /opt/railwise
test -s .env || { echo 'Missing /opt/railwise/.env'; exit 1; }
set -a
. ./.env
set +a
: "${JURY_PASSWORD:?Missing JURY_PASSWORD}"
export JURY_PASSWORD_HASH="$(docker run --rm caddy:2-alpine caddy hash-password --algorithm bcrypt --plaintext "$JURY_PASSWORD")"
docker compose --env-file .env -f deploy/compose.yaml up -d --build --remove-orphans
