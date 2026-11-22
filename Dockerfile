# ── Etapa 1: Entorno de Python y Dev Containers ────────
FROM python:3.13-slim AS python_server

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY ./requirements.txt /tmp/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --prefer-binary -r /tmp/requirements.txt && \
    python -m ipykernel install --name python3 --display-name "Python 3.13 (Docker)" && \
    rm /tmp/requirements.txt

CMD ["tail", "-f", "/dev/null"]

# ── Etapa 2: Contenedor con Google Cloud SDK CLI + cbt (Bigtable) ────────
FROM python:3.13-slim AS gcp_server

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gnupg \
    curl \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        google-cloud-cli \
        google-cloud-cli-cbt \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && printf '%s\n' \
        '#!/bin/sh' \
        'ERR_FILE=$(mktemp)' \
        'trap '\''rm -f "$ERR_FILE"'\'' EXIT' \
        '/usr/bin/cbt "$@" 2>"$ERR_FILE"' \
        'STATUS=$?' \
        'grep -v "Failed to read manufacturer, vmOnGCE=false" "$ERR_FILE" >&2' \
        'exit "$STATUS"' \
        > /usr/local/bin/cbt \
    && chmod +x /usr/local/bin/cbt

CMD ["tail", "-f", "/dev/null"]