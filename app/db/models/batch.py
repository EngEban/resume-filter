# ============================================================
# app/db/models/batch.py
# Batch Model (a group of resumes for one job)
# ============================================================
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.resume import Resume


class Batch(Base, UUIDMixin, TimestampMixin):
    """
    Batch represents a group of resumes uploaded together
    for a specific job description.
    """

    __tablename__ = "batches"

    # ---------- Tenant ----------
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ---------- Job Definition ----------
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    job_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---------- Status ----------
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True,
    )

    # ---------- Progress Counters ----------
    total_resumes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ---------- Timestamps ----------
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ---------- Relationships ----------
    resumes: Mapped[list["Resume"]] = relationship(
        "Resume",
        back_populates="batch",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Batch(id={self.id}, status={self.status}, total={self.total_resumes})>"
