# ============================================================
# app/core/security.py
# Encryption helpers (Fernet) for storing tenant API keys.
# ============================================================
import logging

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

logger = logging.getLogger(__name__)

# Singleton Fernet instance built from MASTER_KEY.
_fernet = Fernet(settings.MASTER_KEY.encode())


def encrypt_api_key(plain_key: str) -> str:
    """
    Encrypt a plaintext API key.

    Returns a Fernet token (URL-safe base64 string) safe for DB storage.
    """
    if not plain_key:
        raise ValueError("Cannot encrypt an empty key.")
    return _fernet.encrypt(plain_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt a Fernet token back to plaintext.

    Raises ValueError if the token is invalid or tampered with.
    """
    try:
        return _fernet.decrypt(encrypted_key.encode()).decode()
    except InvalidToken as exc:
        logger.error("Failed to decrypt API key - token is invalid.")
        raise ValueError("Invalid or tampered encrypted key.") from exc