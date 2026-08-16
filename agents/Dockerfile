# syntax=docker/dockerfile:1
# Catalog + Data agents gateway (Python 3.14) with baked workbench.

FROM node:22-alpine AS frontend
WORKDIR /ui
COPY agents/frontend/package.json agents/frontend/package-lock.json ./
RUN npm ci
COPY agents/frontend/ ./
RUN npm run build

FROM python:3.14-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CATALOG_ROOT=/app \
    AGENTS_DATA_DIR=/app/agents/data \
    AGENTS_PORT=8080

RUN pip install --no-cache-dir \
        "fastapi>=0.115.0" \
        "uvicorn>=0.32.0" \
        "httpx>=0.28.0" \
        "pydantic>=2.10.0" \
        "rdflib>=7.1.0" \
        "pyoxigraph>=0.5.9" \
        "networkx>=3.4.0" \
        "pymongo>=4.10.0" \
        "psycopg[binary]>=3.2.0" \
        "sqlparse>=0.5.0"

COPY index.json industries.json /app/
COPY core /app/core
COPY domains /app/domains
COPY industries /app/industries

COPY agents /app/agents
COPY --from=frontend /ui/dist /app/agents/frontend/dist
RUN rm -rf /app/agents/frontend/src /app/agents/frontend/public

RUN python3 -c "from agents.catalog_agent.tools import rebuild_index; print(rebuild_index(incremental=False))"

EXPOSE 8080
CMD ["python3", "-m", "agents", "--host", "0.0.0.0", "--port", "8080"]
