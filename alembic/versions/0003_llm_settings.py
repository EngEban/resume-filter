"""Add multi-provider LLM settings to tenants.

Revision ID: 0003_llm_settings
Revises: 0002_rls
Create Date: 2026-10-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_llm_settings"
down_revision: Union[str, None] = "0002_rls"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------- Add provider-agnostic columns --------
    op.add_column(
        "tenants",
        sa.Column("llm_provider", sa.String(50), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column("llm_model", sa.String(150), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column("llm_api_key_encrypted", sa.Text(), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column("llm_base_url", sa.String(255), nullable=True),
    )

    # -------- Migrate data from the old Groq-specific columns --------
    op.execute(
        """
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='tenants' AND column_name='groq_api_key_encrypted'
            ) THEN
                UPDATE tenants
                SET llm_provider = 'groq',
                    llm_model = COALESCE(preferred_model, 'groq/llama-3.1-8b-instant'),
                    llm_api_key_encrypted = groq_api_key_encrypted
                WHERE groq_api_key_encrypted IS NOT NULL;
            END IF;
        END $$;
        """
    )

    # -------- Drop the old Groq-specific columns --------
    op.execute("ALTER TABLE tenants DROP COLUMN IF EXISTS groq_api_key_encrypted;")
    op.execute("ALTER TABLE tenants DROP COLUMN IF EXISTS preferred_model;")


def downgrade() -> None:
    op.add_column(
        "tenants",
        sa.Column("groq_api_key_encrypted", sa.Text(), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "preferred_model",
            sa.String(100),
            nullable=False,
            server_default="llama-3.1-8b-instant",
        ),
    )

    op.drop_column("tenants", "llm_base_url")
    op.drop_column("tenants", "llm_api_key_encrypted")
    op.drop_column("tenants", "llm_model")
    op.drop_column("tenants", "llm_provider")