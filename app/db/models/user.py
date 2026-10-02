# ============================================================
# app/db/models/user.py
# User Model (both B2B and B2C)
# ============================================================
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.tenant import Tenant
    from app.db.models.analysis import Analysis


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model.

    - B2B users belong to a tenant (organization).
    - B2C users have tenant_id = NULL.
    """

    __tablename__ = "users"

    # ---------- Identity ----------
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)

    # ---------- Status ----------
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ---------- Tenant (nullable for B2C) ----------
    tenant_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # ---------- Role & Account Type ----------
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), default="b2c", nullable=False)

    # ---------- Relationships ----------
    tenant: Mapped["Tenant | None"] = relationship("Tenant", back_populates="users")
    analyses: Mapped[list["Analysis"]] = relationship(
        "Analysis",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, type={self.account_type})>"