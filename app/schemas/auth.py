# ============================================================
# app/schemas/auth.py
# Pydantic schemas for authentication.
# ============================================================
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRead(BaseModel):
    """Public user representation."""

    id: UUID
    email: EmailStr
    is_active: bool
    is_verified: bool
    role: str
    account_type: str
    tenant_id: UUID | None = None

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """Payload for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    account_type: str = Field(default="b2c", pattern="^(b2b|b2c)$")


class TenantRegister(BaseModel):
    """Payload for registering a new B2B tenant + owner."""

    organization_name: str = Field(..., min_length=2, max_length=255)
    organization_slug: str = Field(..., min_length=2, max_length=100, pattern="^[a-z0-9-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class Token(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"
