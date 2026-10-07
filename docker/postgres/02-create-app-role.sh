#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --variable=app_db_user="$APP_DB_USER" \
  --variable=app_db_password="$APP_DB_PASSWORD" \
  --variable=app_db_name="$POSTGRES_DB" <<'EOSQL'
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'app_db_user') THEN
        CREATE ROLE :"app_db_user" LOGIN PASSWORD :'app_db_password' NOSUPERUSER NOBYPASSRLS;
    END IF;
END
$$;
ALTER ROLE :"app_db_user" NOSUPERUSER NOBYPASSRLS;
GRANT CONNECT ON DATABASE :"app_db_name" TO :"app_db_user";
GRANT USAGE, CREATE ON SCHEMA public TO :"app_db_user";
EOSQL
