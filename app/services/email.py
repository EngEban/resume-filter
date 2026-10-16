# ============================================================
# app/services/email.py
# Email sending via Resend.
# ============================================================
import logging

import resend

from app.core.config import settings

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


async def send_verification_email(
    to_email: str,
    verification_token: str,
) -> bool:
    """
    Send an email verification link.

    Returns True if sent, False if failed.
    Never raises - caller must not fail if email fails.
    """
    if not settings.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set - skipping email to %s", to_email)
        return False

    verify_url = (
        f"{settings.APP_BASE_URL}/verify-email?token={verification_token}"
    )
    
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px;">
      <h2 style="color: #4F46E5;">Welcome to Talentscope</h2>
      <p>Please verify your email address to activate your account.</p>
      <p style="margin: 30px 0;">
        <a href="{verify_url}"
           style="background:#4F46E5;color:white;padding:12px 24px;
                  border-radius:8px;text-decoration:none;font-weight:bold;">
          Verify Email
        </a>
      </p>
      <p style="color:#666;font-size:12px;">
        Or copy this link: <br>
        <code>{verify_url}</code>
      </p>
      <p style="color:#999;font-size:11px;">
        This link expires in 24 hours. If you didn't sign up, ignore this email.
      </p>
    </div>
    """

    try:
        await resend.Emails.send_async({
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [to_email],
            "subject": "Verify your Talentscope account",
            "html": html,
        })
        logger.info("Verification email sent to %s", to_email)
        return True
    except Exception as exc:
        logger.exception("Failed to send verification email to %s: %s", to_email, exc)
        return False