# ============================================================
# app/core/dependencies.py
# Common FastAPI dependencies.
# ============================================================
from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.user import User
from app.db.session import get_db, get_session

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)

ALGORITHM = "HS256"


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Decode the JWT and return the authenticated user."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exc

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exc
        user_id = UUID(user_id_raw)
    except (JWTError, ValueError):
        raise credentials_exc from None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exc
    return user


async def get_current_b2b_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the user is a B2B user belonging to a tenant."""
    if user.account_type != "b2b" or user.tenant_id is None:
        raise HTTPException(status_code=403, detail="B2B account required")
    return user


async def get_current_b2c_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the user is a B2C user."""
    if user.account_type != "b2c":
        raise HTTPException(status_code=403, detail="B2C account required")
    return user


async def get_tenant_db(
    user: Annotated[User, Depends(get_current_b2b_user)],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Database session with Row-Level Security scoped to the
    authenticated user's tenant.
    """
    assert user.tenant_id is not None
    async with get_session(user.tenant_id) as session:
        yield session
