#!/bin/sh
set -eu

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"

export PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" <<'EOSQL'
-- These are the current application CRUD requirements. RLS is intentionally
-- not enabled or changed by this script.
GRANT SELECT, INSERT ON TABLE public.tenants, public.users TO rf_app;
GRANT SELECT, INSERT, UPDATE ON TABLE public.batches, public.resumes TO rf_app;
GRANT SELECT, INSERT ON TABLE public.analyses TO rf_app;

GRANT SELECT ON TABLE public.tenants TO rf_worker;
GRANT SELECT, UPDATE ON TABLE public.batches, public.resumes TO rf_worker;

-- The migration role is kept separate from runtime roles and needs DML access
-- for data migrations. Ownership is intentionally not changed here.
GRANT ALL PRIVILEGES
    ON TABLE public.tenants, public.users, public.batches, public.resumes, public.analyses
    TO rf_migrator;
GRANT SELECT, INSERT, UPDATE, DELETE
    ON TABLE public.alembic_version
    TO rf_migrator;

DO $$
DECLARE
    sequence_name text;
BEGIN
    FOR sequence_name IN
        SELECT quote_ident(n.nspname) || '.' || quote_ident(c.relname)
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'S'
    LOOP
        EXECUTE format('GRANT USAGE, SELECT ON SEQUENCE %s TO rf_app, rf_migrator', sequence_name);
    END LOOP;
END
$$;
EOSQL
