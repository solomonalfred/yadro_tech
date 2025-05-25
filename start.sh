#!/usr/bin/env bash
set -e

#until pg_isready -h db -p "${DB_PORT_INTERNAL}" -U "${DB_USER:-postgres}" -d "${DB_NAME}" > /dev/null 2>&1; do
#  echo "Waiting for postgres at db" >&2
#  sleep 1
#done

alembic upgrade head
exec uvicorn src.application:app --host 0.0.0.0 --port "${PORT:-8080}"
