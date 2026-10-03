"""Row-Level Security policies for multi-tenant isolation.

Revision ID: 0002_rls
Revises: 0001_initial
Create Date: 2026-10-02
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_rls"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


TENANT_SCOPED_TABLES = ["users", "batches", "resumes"]


def upgrade() -> None:
    # -------- Enable RLS on tenant-scoped tables --------
    for table in TENANT_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
        op.execute(
            f"""
            CREATE POLICY tenant_isolation_{table} ON {table}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid)
                WITH CHECK (tenant_id = current_setting('app.current_tenant', true)::uuid);
            """
        )

    # -------- RLS on analyses (scoped through user_id) --------
    op.execute("ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE analyses FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY user_isolation_analyses ON analyses
            USING (
                user_id IN (
                    SELECT id FROM users
                    WHERE tenant_id = current_setting('app.current_tenant', true)::uuid
                )
            );
        """
    )

    # -------- Bypass policy for admin role --------
    # Grants the DB owner bypass so migrations and admin tools work.
    for table in [*TENANT_SCOPED_TABLES, "analyses"]:
        op.execute(
            f"""
            CREATE POLICY bypass_{table} ON {table}
                TO CURRENT_USER
                USING (true)
                WITH CHECK (true);
            """
        )


def downgrade() -> None:
    for table in [*TENANT_SCOPED_TABLES, "analyses"]:
        op.execute(f"DROP POLICY IF EXISTS bypass_{table} ON {table};")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table};")
        op.execute(f"DROP POLICY IF EXISTS user_isolation_{table} ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
