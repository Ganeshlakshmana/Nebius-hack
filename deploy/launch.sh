#!/usr/bin/env bash
set -euo pipefail
cd /opt/railwise
test -s .env || { echo 'Missing /opt/railwise/.env'; exit 1; }
set -a
. ./.env
set +a
docker compose --env-file .env -f deploy/compose.yaml up -d --build --remove-orphans
