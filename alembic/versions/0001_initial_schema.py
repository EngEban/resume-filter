"""Initial schema: tenants, users, batches, resumes, analyses.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --------------------------------------------------------
    # tenants
    # --------------------------------------------------------
    op.create_table(
        "tenants",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("plan", sa.String(50), nullable=False, server_default="free"),
        sa.Column("groq_api_key_encrypted", sa.Text(), nullable=True),
        sa.Column("monthly_limit", sa.Integer(), nullable=False, server_default="100"),
        sa.Column(
            "concurrent_batches_limit",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "preferred_model",
            sa.String(100),
            nullable=False,
            server_default="llama-3.1-8b-instant",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)

    # --------------------------------------------------------
    # users (extends FastAPI Users base table)
    # --------------------------------------------------------
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("account_type", sa.String(20), nullable=False, server_default="b2c"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "account_type IN ('b2b', 'b2c')",
            name="chk_users_account_type",
        ),
        sa.CheckConstraint(
            "role IN ('owner', 'admin', 'member', 'viewer')",
            name="chk_users_role",
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])

    # --------------------------------------------------------
    # batches
    # --------------------------------------------------------
    op.create_table(
        "batches",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("job_requirements", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("total_resumes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_batches_tenant_id", "batches", ["tenant_id"])
    op.create_index("ix_batches_status", "batches", ["status"])

    # --------------------------------------------------------
    # resumes
    # --------------------------------------------------------
    op.create_table(
        "resumes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "batch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("batches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("candidate_name", sa.String(255), nullable=True),
        sa.Column("candidate_email", sa.String(255), nullable=True),
        sa.Column("candidate_phone", sa.String(50), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("parsed_data", postgresql.JSONB(), nullable=True),
        sa.Column("ats_score", sa.Float(), nullable=True),
        sa.Column("score_breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("missing_keywords", postgresql.JSONB(), nullable=True),
        sa.Column("suggestions", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_resumes_tenant_id", "resumes", ["tenant_id"])
    op.create_index("ix_resumes_batch_id", "resumes", ["batch_id"])
    op.create_index("ix_resumes_status", "resumes", ["status"])

    # --------------------------------------------------------
    # analyses
    # --------------------------------------------------------
    op.create_table(
        "analyses",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("resume_text", sa.Text(), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("ats_score", sa.Float(), nullable=True),
        sa.Column("breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("missing_keywords", postgresql.JSONB(), nullable=True),
        sa.Column("suggestions", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_analyses_user_id", "analyses", ["user_id"])
    op.create_index("ix_analyses_created_at", "analyses", ["created_at"])


def downgrade() -> None:
    op.drop_table("analyses")
    op.drop_table("resumes")
    op.drop_table("batches")
    op.drop_table("users")
    op.drop_table("tenants")