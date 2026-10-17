# ============================================================
# app/db/models/tenant.py
# Tenant Model (Organizations)
# ============================================================
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class Tenant(Base, UUIDMixin, TimestampMixin):
    """
    Tenant represents an organization (B2B customer).

    Each tenant has its own users, batches, and resumes.
    Data isolation is enforced via PostgreSQL Row-Level Security.

    LLM usage is platform-managed — the platform's API key is used
    for every tenant. No per-tenant credentials are stored.
    """

    __tablename__ = "tenants"

    # ---------- Identity ----------
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # ---------- Plan & Limits ----------
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    monthly_limit: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    concurrent_batches_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # ---------- Status ----------
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ---------- Relationships ----------
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, slug={self.slug}, plan={self.plan})>"
