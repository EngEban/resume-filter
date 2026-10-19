# ============================================================
# app/api/v1/b2c/history.py
# B2C user analysis history + cleanup.
# ============================================================
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_b2c_user
from app.db.models.analysis import Analysis
from app.db.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/b2c", tags=["B2C - Individuals"])


# ------------------------------------------------------------
# List history
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Delete a single analysis
# ------------------------------------------------------------
@router.delete("/history/{analysis_id}", status_code=status.HTTP_200_OK)
async def delete_analysis(
    analysis_id: UUID,
    user: Annotated[User, Depends(get_current_b2c_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Delete a single analysis from the current user's history.

    Returns 404 if the analysis does not exist or belongs to another user.
    """
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == user.id,
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    await db.delete(analysis)
    await db.commit()

    return {
        "message": "Analysis deleted.",
        "id": str(analysis_id),
    }


# ------------------------------------------------------------
# Delete all analyses
# ------------------------------------------------------------
@router.delete("/history", status_code=status.HTTP_200_OK)
async def clear_history(
    user: Annotated[User, Depends(get_current_b2c_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Delete ALL analyses for the current user.

    Only affects the authenticated user — other users' data is untouched.
    """
    # Count first for the response
    count_result = await db.execute(
        select(func.count(Analysis.id)).where(Analysis.user_id == user.id)
    )
    deleted_count = count_result.scalar_one() or 0

    # Delete
    await db.execute(delete(Analysis).where(Analysis.user_id == user.id))
    await db.commit()

    return {
        "message": "History cleared.",
        "deleted_count": deleted_count,
    }
