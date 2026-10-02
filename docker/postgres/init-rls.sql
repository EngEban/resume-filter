-- ============================================================
-- ResumeFilter - PostgreSQL Initialization
-- ============================================================
-- Runs only on first start of an empty PostgreSQL data volume.
-- Only creates extensions. Tables and RLS policies are managed
-- by Alembic migrations.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";