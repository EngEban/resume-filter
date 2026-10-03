# ============================================================
# app/db/session.py
# Async Database Session + RLS Context
# ============================================================
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# ---------- Engine ----------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)


# ---------- Session Factory ----------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ---------- Context Manager (مع RLS) ----------
@asynccontextmanager
async def get_session(
    tenant_id: UUID | str | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Database session with optional Row-Level Security.

    When tenant_id is provided, SET LOCAL is applied at the
    start of the transaction, so every query within this
    session is automatically scoped to that tenant.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Start the transaction explicitly so SET LOCAL persists
            # for the entire session, not just the first statement.
            await session.begin()

            if tenant_id:
                await session.execute(
                    text("SET LOCAL app.current_tenant = :tid"),
                    {"tid": str(tenant_id)},
                )

            yield session
            await session.commit()

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()
