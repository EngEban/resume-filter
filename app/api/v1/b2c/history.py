# ============================================================
# app/api/v1/b2c/history.py
# B2C user analysis history.
# ============================================================
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_b2c_user
from app.db.models.analysis import Analysis
from app.db.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/b2c", tags=["B2C - Individuals"])


@router.get("/history")
async def list_my_analyses(
    user: Annotated[User, Depends(get_current_b2c_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
) -> list[dict]:
    """Return the authenticated user's analysis history."""
    result = await db.execute(
        select(Analysis)
        .where(Analysis.user_id == user.id)
        .order_by(desc(Analysis.created_at))
        .limit(limit)
    )
    items = result.scalars().all()

    return [
        {
            "id": str(item.id),
            "ats_score": item.ats_score,
            "breakdown": item.breakdown,
            "missing_keywords": item.missing_keywords,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in items
    ]