#!/bin/bash
# Startup script idempotente para PostgreSQL en una VM de GCP.
# Lee la configuración desde los metadatos de la instancia:
#   pg-user, pg-password, pg-db
set -euo pipefail
cd /tmp

# ── Leer parámetros desde el metadata server ───────────────────────────
MD_URL="http://metadata.google.internal/computeMetadata/v1/instance/attributes"
get_md() { curl -sf -H "Metadata-Flavor: Google" "$MD_URL/$1"; }

PG_USER="$(get_md pg-user)"
PG_PASSWORD="$(get_md pg-password)"
PG_DB="$(get_md pg-db)"

if [ -z "$PG_USER" ] || [ -z "$PG_PASSWORD" ] || [ -z "$PG_DB" ]; then
  echo "Faltan metadatos pg-user / pg-password / pg-db" >&2
  exit 1
fi

# ── 1. Instalar PostgreSQL solo si no está instalado ───────────────────
if ! dpkg -s postgresql >/dev/null 2>&1; then
  apt-get update
  apt-get install -y postgresql postgresql-contrib
fi

PG_CONF="$(ls /etc/postgresql/*/main/postgresql.conf | head -n1)"
PG_HBA="$(ls /etc/postgresql/*/main/pg_hba.conf | head -n1)"

# ── 2. Escuchar en todas las interfaces ────────────────────────────────
sed -i -E "s/^#?listen_addresses\s*=.*/listen_addresses = '*'/" "$PG_CONF"

# ── 3. Regla de acceso remoto (el firewall de GCP filtra por IP) ───────
if ! grep -qE "^host\s+all\s+all\s+0\.0\.0\.0/0" "$PG_HBA"; then
  echo "host all all 0.0.0.0/0 scram-sha-256" >> "$PG_HBA"
fi

systemctl restart postgresql

# Helper: ejecuta SQL como postgres con variables psql seguras (sin problemas de comillas)
pg() {
  sudo -u postgres psql -v ON_ERROR_STOP=1 -tA \
    -v u="$PG_USER" -v pw="$PG_PASSWORD" -v db="$PG_DB" "$@"
}

# ── 4. Crear usuario y base solo si no existen ─────────────────────────
if [ -z "$(pg <<< "SELECT 1 FROM pg_roles WHERE rolname = :'u';")" ]; then
  pg <<< "CREATE USER :\"u\" WITH PASSWORD :'pw';"
fi

if [ -z "$(pg <<< "SELECT 1 FROM pg_database WHERE datname = :'db';")" ]; then
  pg <<< "CREATE DATABASE :\"db\" OWNER :\"u\";"
fi

pg <<< "GRANT ALL PRIVILEGES ON DATABASE :\"db\" TO :\"u\";"

echo "PostgreSQL configurado correctamente."