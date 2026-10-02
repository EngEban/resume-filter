# ============================================================
# app/api/v1/auth.py
# Authentication endpoints (register + login).
# ============================================================
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import TenantRegister, Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


# ------------------------------------------------------------
# Password utilities
# ------------------------------------------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ------------------------------------------------------------
# JWT creation
# ------------------------------------------------------------
def create_access_token(user: User, expires_minutes: int = 60 * 24) -> str:
    """Create a signed JWT for the given user."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        "role": user.role,
        "account_type": user.account_type,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


# ------------------------------------------------------------
# B2C Registration (individuals)
# ------------------------------------------------------------
@router.post(
    "/register/b2c",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
)
async def register_b2c(
    payload: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Register a new B2C (individual) user."""
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        account_type="b2c",
        role="member",
        is_active=True,
        is_verified=False,
        is_superuser=False,
        tenant_id=None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return Token(access_token=create_access_token(user))


# ------------------------------------------------------------
# B2B Registration (organization + owner)
# ------------------------------------------------------------
@router.post(
    "/register/b2b",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
)
async def register_b2b(
    payload: TenantRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Register a new organization and its owner user."""
    existing_user = await db.execute(select(User).where(User.email == payload.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    slug = payload.organization_slug or slugify(payload.organization_name)
    existing_tenant = await db.execute(select(Tenant).where(Tenant.slug == slug))
    if existing_tenant.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Organization slug already taken")

    tenant = Tenant(
        name=payload.organization_name,
        slug=slug,
        plan="free",
    )
    db.add(tenant)
    await db.flush()

    owner = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        account_type="b2b",
        role="owner",
        is_active=True,
        is_verified=False,
        is_superuser=False,
        tenant_id=tenant.id,
    )
    db.add(owner)
    await db.commit()
    await db.refresh(owner)

    return Token(access_token=create_access_token(owner))


# ------------------------------------------------------------
# Login (OAuth2 form-data compatible)
# ------------------------------------------------------------
@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Authenticate a user with form data and return a JWT."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    return Token(access_token=create_access_token(user))


# ------------------------------------------------------------
# Current user profile
# ------------------------------------------------------------
@router.get("/me", response_model=UserRead)
async def read_me(
    user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Return the authenticated user's profile."""
    return UserRead.model_validate(user)