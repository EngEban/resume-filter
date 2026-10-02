# ============================================================
# app/providers/__init__.py
# Provider factory.
# ============================================================
from app.providers.base import BaseLLMProvider, LLMResponse
from app.providers.unified_provider import (
    ResolvedLLMConfig,
    UnifiedLLMProvider,
    resolve_llm_config,
)


def get_provider(tenant=None) -> BaseLLMProvider:
    """
    Return an LLM provider for the given tenant.

    If the tenant has configured its own key (BYOK), it is used.
    Otherwise, the platform-wide default is used.
    """
    config = resolve_llm_config(tenant)
    return UnifiedLLMProvider(config)


__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "ResolvedLLMConfig",
    "UnifiedLLMProvider",
    "get_provider",
    "resolve_llm_config",
]