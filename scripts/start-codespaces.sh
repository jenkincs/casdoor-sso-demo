#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -z "${CODESPACE_NAME:-}" ]]; then
  echo "Please run this inside GitHub Codespaces."
  exit 1
fi
mkdir -p .demo
exec 9>.demo/startup.lock
flock 9
python3 scripts/codespaces_config.py
for attempt in $(seq 1 60); do
  if docker info >/dev/null 2>&1; then break; fi
  if [[ "$attempt" == "60" ]]; then echo "Docker is not ready. Rebuild the Codespace container."; exit 1; fi
  sleep 2
done
docker compose --env-file .demo/runtime.env -f compose.codespaces.yml up -d --build
# Try the documented CLI operation once. Codespaces may restrict its generated token.
if command -v gh >/dev/null 2>&1 && gh codespace ports visibility 8000:public 8080:public 8081:public --codespace "$CODESPACE_NAME" >/dev/null 2>&1; then
  echo "The three demo ports are public."
else
  echo "Open the PORTS tab, right-click 8000, 8080 and 8081, then choose Port Visibility > Public."
fi
python3 scripts/check-codespaces.py
echo "Test account is in .demo/TEST-ACCOUNT.txt (keep admin and database secrets private)."
