"""Shared ownership checks for B2B resources."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.batch import Batch
from app.db.models.resume import Resume


async def get_tenant_batch(
    db: AsyncSession,
    tenant_id: UUID | None,
    batch_id: UUID,
) -> Batch:
    """Return a batch only when it belongs to the authenticated tenant."""
    if tenant_id is None:
        raise HTTPException(status_code=403, detail="B2B account required")

    result = await db.execute(
        select(Batch).where(
            Batch.id == batch_id,
            Batch.tenant_id == tenant_id,
        )
    )
    batch = result.scalar_one_or_none()
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


async def get_tenant_resume(
    db: AsyncSession,
    tenant_id: UUID | None,
    resume_id: UUID,
) -> Resume:
    """Return a resume only when both it and its batch belong to the tenant."""
    if tenant_id is None:
        raise HTTPException(status_code=403, detail="B2B account required")

    result = await db.execute(
        select(Resume)
        .join(Batch, Batch.id == Resume.batch_id)
        .where(
            Resume.id == resume_id,
            Resume.tenant_id == tenant_id,
            Batch.tenant_id == tenant_id,
        )
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
