#!/bin/sh
set -e
# Named volumes are often root-owned; chown when we start as root (docker-compose / Render).
if [ "$(id -u)" = "0" ]; then
  if [ -n "${PERSISTENT_DATA_DIR:-}" ]; then
    mkdir -p "$PERSISTENT_DATA_DIR"
    chown -R app:app "$PERSISTENT_DATA_DIR"
  fi
  exec gosu app streamlit run app.py \
    --server.address=0.0.0.0 \
    --server.port="${PORT:-8501}" \
    --server.headless=true
fi
exec streamlit run app.py \
  --server.address=0.0.0.0 \
  --server.port="${PORT:-8501}" \
  --server.headless=true
