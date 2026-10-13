# ============================================================
# app/api/v1/b2b/settings.py
# Central platform LLM settings (tenant read-only view).
# ============================================================
import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.dependencies import get_current_b2b_user, require_tenant_admin
from app.db.models.user import User
from app.providers import resolve_llm_config
from app.providers.unified_provider import UnifiedLLMProvider
from app.schemas.settings import (
    ConnectionTestResult,
    LLMSettingsRead,
    ProviderInfo,
    ProvidersListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/b2b/settings", tags=["B2B - Settings"])

_CENTRAL_SETTINGS_DETAIL = (
    "LLM settings are managed centrally by the platform and cannot be changed per organization."
)


def _central_settings_read() -> LLMSettingsRead:
    """Return safe, non-secret information about the active platform config."""
    config = resolve_llm_config()
    return LLMSettingsRead(
        provider=config.provider,
        model=config.model,
        has_custom_key=False,
        # Do not disclose the platform's network target to tenant users.
        base_url=None,
        source="platform",
    )


@router.get("/llm", response_model=LLMSettingsRead)
async def get_llm_settings(
    user: Annotated[User, Depends(get_current_b2b_user)],
) -> LLMSettingsRead:
    """Return the active platform configuration without credentials."""
    return _central_settings_read()


@router.put("/llm", response_model=LLMSettingsRead)
async def update_llm_settings(
    user: Annotated[User, Depends(require_tenant_admin)],
) -> LLMSettingsRead:
    """Keep the legacy route explicit while preventing tenant BYOK writes."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=_CENTRAL_SETTINGS_DETAIL,
    )


@router.delete("/llm", status_code=status.HTTP_204_NO_CONTENT)
async def delete_llm_settings(
    user: Annotated[User, Depends(require_tenant_admin)],
) -> None:
    """Prevent tenant requests from mutating retained legacy BYOK columns."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=_CENTRAL_SETTINGS_DETAIL,
    )


@router.get("/llm/providers", response_model=ProvidersListResponse)
async def list_providers(
    user: Annotated[User, Depends(get_current_b2b_user)],
) -> ProvidersListResponse:
    """Expose only the currently active platform provider to tenant users."""
    config = resolve_llm_config()
    return ProvidersListResponse(
        providers=[
            ProviderInfo(
                provider=config.provider,
                models=[config.model],
                requires_api_key=config.provider != "ollama",
                supports_base_url=False,
            )
        ],
        platform_default={
            "provider": config.provider,
            "model": config.model,
        },
    )


@router.post("/llm/test", response_model=ConnectionTestResult)
async def test_llm_connection(
    user: Annotated[User, Depends(get_current_b2b_user)],
) -> ConnectionTestResult:
    """Test the platform provider; request data cannot select a target or key."""
    started = time.monotonic()
    provider_name = settings.PLATFORM_LLM_PROVIDER

    try:
        config = resolve_llm_config()
        provider_name = config.provider
        provider = UnifiedLLMProvider(config)
        await provider.complete(
            system_prompt="You are a health check.",
            user_prompt="Reply with the single word: ok",
            max_tokens=10,
            follow_redirects=False,
        )
    except Exception as exc:
        logger.warning(
            "Central LLM connection test failed for provider %s: %s",
            provider_name,
            type(exc).__name__,
        )
        return ConnectionTestResult(
            success=False,
            message="Connection failed.",
        )

    return ConnectionTestResult(
        success=True,
        message="Connection successful.",
        latency_ms=int((time.monotonic() - started) * 1000),
    )
