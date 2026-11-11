#!/usr/bin/env bash
set -euo pipefail
umask 077

# Le variabili devono essere gia esportate, ad esempio caricando .env in Bash.
export PGPASSWORD="${DB_PASSWORD:?Impostare DB_PASSWORD nell ambiente}"
backup_dir="${BACKUP_DIR:-$(dirname "$0")/backups}"
mkdir -p "$backup_dir"
backup_file="$backup_dir/${DB_NAME:-hdn}_$(date +%Y-%m-%d-%H-%M-%S).sql"

pg_dump --dbname="${DB_NAME:-hdn}" --username="${DB_USER:-hdn}" \
    --host="${DB_HOST:-localhost}" --port="${DB_PORT:-5432}" \
    --clean --file="$backup_file"
printf 'Backup creato: %s\n' "$backup_file"
