"""drop tenant BYOK columns

Revision ID: 0005_drop_byok
Revises: 8760dfd001fe
Create Date: 2026-10-16

Removes the four tenant-level BYOK columns. LLM usage is now entirely
platform-managed via PLATFORM_LLM_* settings. Tenant users can no longer
store their own credentials.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0005_drop_byok"
down_revision: Union[str, None] = "8760dfd001fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the four BYOK columns from tenants table
    op.drop_column("tenants", "llm_api_key_encrypted")
    op.drop_column("tenants", "llm_base_url")
    op.drop_column("tenants", "llm_model")
    op.drop_column("tenants", "llm_provider")


def downgrade() -> None:
    # Restore the columns (nullable) if we ever roll back
    op.add_column(
        "tenants",
        sa.Column("llm_provider", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column("llm_model", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column("llm_api_key_encrypted", sa.Text(), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column("llm_base_url", sa.String(length=255), nullable=True),
    )