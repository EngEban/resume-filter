#!/bin/sh
set -eu

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${RF_APP_PASSWORD:?RF_APP_PASSWORD is required}"
: "${RF_WORKER_PASSWORD:?RF_WORKER_PASSWORD is required}"
: "${RF_MIGRATOR_PASSWORD:?RF_MIGRATOR_PASSWORD is required}"

# The init hook uses local trust authentication; the Compose/Kubernetes Jobs
# use the same variable through libpq without printing it.
export PGPASSWORD="$POSTGRES_PASSWORD"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --variable=rf_app_password="$RF_APP_PASSWORD" \
  --variable=rf_worker_password="$RF_WORKER_PASSWORD" \
  --variable=rf_migrator_password="$RF_MIGRATOR_PASSWORD" \
  --variable=database_name="$POSTGRES_DB" <<'EOSQL'
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rf_owner') THEN
        CREATE ROLE rf_owner NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rf_app') THEN
        CREATE ROLE rf_app LOGIN;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rf_worker') THEN
        CREATE ROLE rf_worker LOGIN;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rf_migrator') THEN
        CREATE ROLE rf_migrator LOGIN;
    END IF;
END
$$;

-- Runtime roles are deliberately not superusers, RLS bypass roles, or role/database creators.
ALTER ROLE rf_app LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE PASSWORD :'rf_app_password';
ALTER ROLE rf_worker LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE PASSWORD :'rf_worker_password';
ALTER ROLE rf_migrator LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE PASSWORD :'rf_migrator_password';
ALTER ROLE rf_owner NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;

-- The migration role is the only role allowed to create objects in the application schema.
GRANT CONNECT ON DATABASE :"database_name" TO rf_app, rf_worker, rf_migrator;
GRANT USAGE ON SCHEMA public TO rf_app, rf_worker, rf_migrator;
GRANT CREATE ON SCHEMA public TO rf_migrator;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM rf_app, rf_worker;

-- Runtime roles must never inherit owner privileges.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_auth_members membership
        JOIN pg_roles granted_role ON granted_role.oid = membership.roleid
        JOIN pg_roles member_role ON member_role.oid = membership.member
        WHERE granted_role.rolname = 'rf_owner' AND member_role.rolname = 'rf_app'
    ) THEN
        REVOKE rf_owner FROM rf_app;
    END IF;
    IF EXISTS (
        SELECT 1
        FROM pg_auth_members membership
        JOIN pg_roles granted_role ON granted_role.oid = membership.roleid
        JOIN pg_roles member_role ON member_role.oid = membership.member
        WHERE granted_role.rolname = 'rf_owner' AND member_role.rolname = 'rf_worker'
    ) THEN
        REVOKE rf_owner FROM rf_worker;
    END IF;
END
$$;
EOSQL
