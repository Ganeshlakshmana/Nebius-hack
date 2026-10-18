# Nebius demo deployment

Runs the Vinext frontend, FastAPI backend, and Caddy HTTPS reverse proxy on one small CPU VM. The supplier CSV ships in the backend image; SQLite uses a persistent Docker volume. The backend has no public port. Caddy protects the dashboard and its API routes with jury basic authentication and obtains TLS certificates for the configured public hostname.

## Host requirements

Ubuntu 24.04, Docker Engine + Compose plugin, 4 vCPU / 16 GiB RAM recommended for the first frontend build, public IPv4, and inbound TCP 80/443. Use the assigned hackathon project and subnet; CPU platform only. The reserved GPU is not used.

## Deploy

1. Copy `.env` to `/opt/railwise/.env` over SSH with mode `600`. Include `PUBLIC_HOST`, `JURY_PASSWORD`, `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `TAVILY_API_KEY`, `COMMERCIAL_API_KEY`, internal agent keys, and `OFFLINE_MODE=false`. Never commit this file.
2. Place the repository at `/opt/railwise`.
3. Run `sudo /opt/railwise/deploy/launch.sh`.
4. Open `https://PUBLIC_HOST`; sign in as `jury` with `JURY_PASSWORD`.
5. Check `docker compose -f deploy/compose.yaml ps` and logs. Confirm the public app, login gate, supplier data, compare, chat and real research before sharing the URL.

The Caddy container handles HTTPS automatically. A public DNS hostname pointing to the VM is required; `IP.nip.io` can be used for a temporary demo if certificate issuance succeeds. Persistent Caddy and SQLite volumes survive container restarts; preserve the VM disk for the demo.

This single VM is a hackathon deployment, not a production high-availability architecture. The jury password gates all paths. Keep backend port 8000 private, rotate temporary provider credentials after the event, and stop/delete the VM when the demo is no longer needed.
