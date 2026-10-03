# ============================================================
# app/services/limits.py
# Daily / monthly usage limits for B2C and B2B.
# ============================================================
from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import LimitExceededError
from app.db.models.analysis import Analysis


async def check_b2c_daily_limit(
    user_id: UUID,
    db: AsyncSession,
    limit: int = 3,
) -> None:
    """
    Enforce the daily analysis limit for a B2C user.

    Raises LimitExceededError if the user has reached the limit today.
    """
    today = date.today()
    result = await db.execute(
        select(func.count(Analysis.id)).where(
            Analysis.user_id == user_id,
            func.date(Analysis.created_at) == today,
        )
    )
    count = result.scalar_one() or 0

    if count >= limit:
        raise LimitExceededError(
            f"Daily limit reached ({limit} analyses/day). Try again tomorrow."
        )


def check_batch_size(size: int, max_size: int) -> None:
    """Ensure a batch does not exceed the maximum allowed size."""
    if size > max_size:
        raise LimitExceededError(
            f"Batch size {size} exceeds the maximum of {max_size}."
        )
