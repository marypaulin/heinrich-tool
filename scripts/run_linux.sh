#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_DIR"

PORT=8502
URL="http://localhost:${PORT}"

# Server already running: just open the browser
if curl -fsS "$URL" >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 || true
  exit 0
fi

# Resolve uv explicitly: launched from the desktop entry, ~/.local/bin is not
# guaranteed to be on PATH
UV="$(command -v uv || echo "${HOME}/.local/bin/uv")"

# Start Streamlit detached and silent (no log file)
nohup "$UV" run streamlit run src/heinrich_tool/app.py \
  --server.port "${PORT}" \
  --server.headless true \
  --browser.gatherUsageStats false \
  >/dev/null 2>&1 &

# Wait for the server to accept connections (max ~10 seconds)
for _ in {1..50}; do
  if curl -fsS "$URL" >/dev/null 2>&1; then
    break
  fi
  sleep 0.2
done

# Open the browser
xdg-open "$URL" >/dev/null 2>&1 || true
