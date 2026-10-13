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
    Return the platform-managed LLM provider.

    ``tenant`` is retained for compatibility with worker and request call
    sites, but it is not used to select credentials or a network endpoint.
    """
    config = resolve_llm_config()
    return UnifiedLLMProvider(config)


__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "ResolvedLLMConfig",
    "UnifiedLLMProvider",
    "get_provider",
    "resolve_llm_config",
]
