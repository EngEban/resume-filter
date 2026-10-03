# ============================================================
# app/api/v1/b2b/settings.py
# Tenant LLM settings management (BYOK).
# ============================================================
import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_b2b_user, get_tenant_db
from app.core.security import encrypt_api_key
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.providers import resolve_llm_config
from app.providers.unified_provider import UnifiedLLMProvider
from app.schemas.settings import (
    SUGGESTED_MODELS,
    SUPPORTED_PROVIDERS,
    ConnectionTestResult,
    LLMSettingsRead,
    LLMSettingsUpdate,
    ProviderInfo,
    ProvidersListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/b2b/settings", tags=["B2B - Settings"])


# ------------------------------------------------------------
# Read current settings
# ------------------------------------------------------------
@router.get("/llm", response_model=LLMSettingsRead)
async def get_llm_settings(
    user: Annotated[User, Depends(get_current_b2b_user)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> LLMSettingsRead:
    """Return the tenant's current LLM configuration (without the key)."""
    tenant = await db.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    config = resolve_llm_config(tenant)

    return LLMSettingsRead(
        provider=tenant.llm_provider or config.provider,
        model=tenant.llm_model or config.model,
        has_custom_key=bool(tenant.llm_api_key_encrypted),
        base_url=tenant.llm_base_url,
        source=config.source,
    )


# ------------------------------------------------------------
# Update settings (BYOK)
# ------------------------------------------------------------
@router.put("/llm", response_model=LLMSettingsRead)
async def update_llm_settings(
    payload: LLMSettingsUpdate,
    user: Annotated[User, Depends(get_current_b2b_user)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> LLMSettingsRead:
    """
    Set the tenant's own LLM provider and API key.

    The key is encrypted with Fernet before storage.
    """
    if payload.provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider. Choose from: {SUPPORTED_PROVIDERS}",
        )

    if payload.provider != "ollama" and not payload.api_key:
        raise HTTPException(
            status_code=400,
            detail="api_key is required for this provider",
        )

    tenant = await db.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.llm_provider = payload.provider
    tenant.llm_model = payload.model
    tenant.llm_base_url = payload.base_url

    if payload.api_key:
        tenant.llm_api_key_encrypted = encrypt_api_key(payload.api_key)

    await db.commit()
    await db.refresh(tenant)

    return LLMSettingsRead(
        provider=tenant.llm_provider,
        model=tenant.llm_model,
        has_custom_key=True,
        base_url=tenant.llm_base_url,
        source="tenant",
    )


# ------------------------------------------------------------
# Delete custom key (revert to platform default)
# ------------------------------------------------------------
@router.delete("/llm", status_code=status.HTTP_204_NO_CONTENT)
async def delete_llm_settings(
    user: Annotated[User, Depends(get_current_b2b_user)],
    db: Annotated[AsyncSession, Depends(get_tenant_db)],
) -> None:
    """Remove the tenant's custom key and revert to the platform default."""
    tenant = await db.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.llm_provider = None
    tenant.llm_model = None
    tenant.llm_api_key_encrypted = None
    tenant.llm_base_url = None

    await db.commit()


# ------------------------------------------------------------
# List available providers
# ------------------------------------------------------------
@router.get("/llm/providers", response_model=ProvidersListResponse)
async def list_providers(
    user: Annotated[User, Depends(get_current_b2b_user)],
) -> ProvidersListResponse:
    """Return the list of supported providers and their suggested models."""
    providers = [
        ProviderInfo(
            provider=p,
            models=SUGGESTED_MODELS.get(p, []),
            requires_api_key=(p != "ollama"),
            supports_base_url=(p in {"ollama", "azure", "openai"}),
        )
        for p in SUPPORTED_PROVIDERS
    ]

    return ProvidersListResponse(
        providers=providers,
        platform_default={
            "provider": settings.PLATFORM_LLM_PROVIDER,
            "model": settings.PLATFORM_LLM_MODEL,
        },
    )


# ------------------------------------------------------------
# Test a configuration without saving
# ------------------------------------------------------------
@router.post("/llm/test", response_model=ConnectionTestResult)
async def test_llm_connection(
    payload: LLMSettingsUpdate,
    user: Annotated[User, Depends(get_current_b2b_user)],
) -> ConnectionTestResult:
    """Test a provider configuration without persisting it."""
    from app.providers.unified_provider import ResolvedLLMConfig

    if payload.provider != "ollama" and not payload.api_key:
        raise HTTPException(status_code=400, detail="api_key is required")

    config = ResolvedLLMConfig(
        provider=payload.provider,
        model=payload.model,
        api_key=payload.api_key or "ollama",
        base_url=payload.base_url,
        source="tenant",
    )

    provider = UnifiedLLMProvider(config)
    started = time.monotonic()

    try:
        await provider.complete(
            system_prompt="You are a health check.",
            user_prompt="Reply with the single word: ok",
            max_tokens=10,
        )
    except Exception as exc:
        return ConnectionTestResult(
            success=False,
            message=f"Connection failed: {exc}",
        )

    latency_ms = int((time.monotonic() - started) * 1000)
    return ConnectionTestResult(
        success=True,
        message="Connection successful.",
        latency_ms=latency_ms,
    )
