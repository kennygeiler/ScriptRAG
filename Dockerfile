# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.title="scriptrag"
LABEL org.opencontainers.image.description="ScriptRAG — self-healing screenplay extraction + Neo4j graph analytics"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependency layer (cache-friendly)
COPY pyproject.toml uv.lock README.md LICENSE ./
RUN uv sync --frozen --no-install-project --no-dev

# Application
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home --shell /bin/bash --uid 1000 app \
    && chown -R app:app /app \
    && apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Render / Fly / Railway set PORT; default 8501 for local docker run
EXPOSE 8501

# Start as root so entrypoint can chown PERSISTENT_DATA_DIR volumes; then drop to app.
USER root
ENTRYPOINT ["/docker-entrypoint.sh"]
