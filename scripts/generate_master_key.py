# ============================================================
# scripts/generate_master_key.py
# Generate SECRET_KEY and MASTER_KEY without external deps.
# ============================================================
import base64
import secrets


def generate_secret_key() -> str:
    """مفتاح سري عشوائي بطول 64 حرف (URL-safe)."""
    return secrets.token_urlsafe(64)


def generate_fernet_key() -> str:
    """
    مفتاح Fernet صالح = 32 بايت عشوائية، مُرمّزة بـ URL-safe base64.
    (هذا بالضبط ما تفعله Fernet.generate_key() داخلياً).
    """
    raw = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(raw).decode()


def main() -> None:
    print("=" * 60)
    print("  Copy these values into your .env file")
    print("=" * 60)
    print()
    print(f"SECRET_KEY={generate_secret_key()}")
    print(f"MASTER_KEY={generate_fernet_key()}")
    print()


if __name__ == "__main__":
    main()
