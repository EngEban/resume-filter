# ============================================================
# app/api/v1/auth.py
# Authentication endpoints (register + login + email verification).
# ============================================================
import secrets
from datetime import UTC, datetime, timedelta
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
from app.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

VERIFICATION_TOKEN_TTL_HOURS = 24


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
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        "role": user.role,
        "account_type": user.account_type,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


# ------------------------------------------------------------
# Verification helpers
# ------------------------------------------------------------
def _issue_verification_token(user: User) -> str:
    """Attach a fresh verification token to the user (not committed)."""
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    user.verification_sent_at = datetime.now(UTC)
    return token


# ------------------------------------------------------------
# B2C Registration (individuals)
# ------------------------------------------------------------
@router.post(
    "/register/b2c",
    status_code=status.HTTP_201_CREATED,
)
async def register_b2c(
    payload: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Register a new B2C (individual) user. Sends a verification email."""
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
    token = _issue_verification_token(user)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await send_verification_email(
        to_email=user.email,
        verification_token=token,
    )

    return {
        "message": "Account created. Please check your email to verify.",
        "email": user.email,
    }


# ------------------------------------------------------------
# B2B Registration (organization + owner)
# ------------------------------------------------------------
@router.post(
    "/register/b2b",
    status_code=status.HTTP_201_CREATED,
)
async def register_b2b(
    payload: TenantRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Register a new organization and its owner user. Sends a verification email."""
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
    token = _issue_verification_token(owner)
    db.add(owner)
    await db.commit()
    await db.refresh(owner)

    await send_verification_email(
        to_email=owner.email,
        verification_token=token,
    )

    return {
        "message": "Account created. Please check your email to verify.",
        "email": owner.email,
    }


# ------------------------------------------------------------
# Email verification
# ------------------------------------------------------------
@router.get("/verify-email")
async def verify_email(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Verify an email address using the token from the email link."""
    result = await db.execute(
        select(User).where(User.verification_token == token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )

    # Check expiry
    if user.verification_sent_at:
        age = datetime.now(UTC) - user.verification_sent_at
        if age > timedelta(hours=VERIFICATION_TOKEN_TTL_HOURS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification link expired. Request a new one.",
            )

    user.email_verified_at = datetime.now(UTC)
    user.is_verified = True
    user.verification_token = None
    user.verification_sent_at = None
    await db.commit()

    return {"message": "Email verified successfully. You can now log in."}


@router.post("/resend-verification")
async def resend_verification(
    email: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Resend the verification email for an unverified account."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Never reveal whether the account exists
    generic = {"message": "If the email exists, a verification link was sent."}

    if not user or user.is_verified:
        return generic

    token = _issue_verification_token(user)
    await db.commit()

    await send_verification_email(
        to_email=user.email,
        verification_token=token,
    )

    return generic


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

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
        )

    return Token(access_token=create_access_token(user))


# ------------------------------------------------------------
# Current user profile
# ------------------------------------------------------------
@router.get("/me", response_model=UserRead)
async def read_me(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Return the authenticated user's profile."""
    # Compute display name: tenant name for B2B, username for B2C
    if user.account_type == "b2b" and user.tenant_id:
        tenant = await db.get(Tenant, user.tenant_id)
        display_name = tenant.name if tenant else user.email.split("@")[0]
    else:
        display_name = user.email.split("@")[0]

    return UserRead(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        account_type=user.account_type,
        tenant_id=user.tenant_id,
        display_name=display_name,
    )

