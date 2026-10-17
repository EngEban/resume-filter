# ============================================================
# app/api/v1/google_auth.py
# Google OAuth 2.0 authentication endpoints.
# ============================================================
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import create_access_token
from app.core.config import settings
from app.core.logging import get_logger
from app.core.oauth import oauth
from app.db.models.user import User
from app.db.session import get_db

logger = get_logger(__name__)

router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])


@router.get("/login")
async def google_login(request: Request):
    """Redirect the user to Google's OAuth consent screen."""
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def google_callback(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Handle the OAuth callback from Google and issue a JWT."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as exc:
        logger.exception("google_oauth_token_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authentication failed.",
        ) from exc

    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(400, "Could not retrieve user info from Google.")

    google_id = user_info["sub"]
    email = user_info["email"].lower()

    # Find existing user by google_id OR email
    result = await db.execute(
        select(User).where(
            (User.google_id == google_id) | (User.email == email)
        )
    )
    user = result.scalar_one_or_none()

    if user:
        # Link Google account if not linked yet
        if not user.google_id:
            user.google_id = google_id
        # Google already verified the email
        if not user.is_verified:
            user.is_verified = True
            user.email_verified_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(user)
    else:
        # Create new B2C user with no password (Google-only)
        user = User(
            email=email,
            hashed_password="",
            account_type="b2c",
            role="member",
            is_active=True,
            is_verified=True,
            is_superuser=False,
            google_id=google_id,
            email_verified_at=datetime.now(UTC),
            tenant_id=None,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    logger.info("google_login_success", email=email, is_new=user is not None)

    access_token = create_access_token(user)
    return RedirectResponse(
        url=f"{settings.APP_BASE_URL}/auth/callback?token={access_token}"
    )
