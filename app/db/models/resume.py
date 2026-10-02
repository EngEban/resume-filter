# ============================================================
# app/db/models/resume.py
# Resume Model (single CV file)
# ============================================================
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.batch import Batch


class Resume(Base, UUIDMixin, TimestampMixin):
    """
    Resume represents a single candidate's CV within a batch.
    """

    __tablename__ = "resumes"

    # ---------- Tenant & Batch ----------
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ---------- File Info ----------
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ---------- Extracted Data ----------
    candidate_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    candidate_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    candidate_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ---------- Scoring ----------
    ats_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    missing_keywords: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    suggestions: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # ---------- Status ----------
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---------- Relationships ----------
    batch: Mapped["Batch"] = relationship("Batch", back_populates="resumes")

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, status={self.status}, score={self.ats_score})>"