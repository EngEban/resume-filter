# ============================================================
# app/providers/unified_provider.py
# Unified LLM provider using LiteLLM.
# Supports 100+ providers through a single interface.
# ============================================================
import logging
from dataclasses import dataclass

import litellm

from app.core.config import settings
from app.core.security import decrypt_api_key
from app.providers.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)

# Suppress verbose LiteLLM logs unless debugging.
litellm.set_verbose = False
litellm.drop_params = True  # Ignore unsupported params per provider


@dataclass
class ResolvedLLMConfig:
    """Resolved LLM configuration for a single request."""

    provider: str
    model: str  # LiteLLM format: "provider/model"
    api_key: str
    base_url: str | None = None
    source: str = "platform"  # "platform" or "tenant"


def resolve_llm_config(tenant=None) -> ResolvedLLMConfig:
    """
    Resolve the LLM configuration for a request.

    Priority:
        1. Tenant's own key (BYOK)
        2. Platform default key

    The model string must be in LiteLLM format:
        "groq/llama-3.1-8b-instant"
        "anthropic/claude-sonnet-4-20250514"
        "openai/gpt-4o"
        "gemini/gemini-1.5-pro"
        "ollama/llama3.1:8b"
    """
    # --- Tenant's own key ---
    if tenant and tenant.llm_api_key_encrypted:
        try:
            api_key = decrypt_api_key(tenant.llm_api_key_encrypted)
            return ResolvedLLMConfig(
                provider=tenant.llm_provider or "openai",
                model=tenant.llm_model or "openai/gpt-4o-mini",
                api_key=api_key,
                base_url=tenant.llm_base_url,
                source="tenant",
            )
        except Exception as exc:
            logger.error(
                "Failed to decrypt tenant %s key, falling back to platform: %s",
                tenant.id,
                exc,
            )

    # --- Platform default ---
    return ResolvedLLMConfig(
        provider=settings.PLATFORM_LLM_PROVIDER,
        model=settings.PLATFORM_LLM_MODEL,
        api_key=settings.PLATFORM_LLM_API_KEY,
        base_url=settings.PLATFORM_LLM_BASE_URL,
        source="platform",
    )


class UnifiedLLMProvider(BaseLLMProvider):
    """
    LLM provider backed by LiteLLM.

    LiteLLM translates a single OpenAI-compatible interface into
    calls to 100+ providers (Groq, OpenAI, Anthropic, Gemini,
    Azure, Bedrock, Ollama, ...).
    """

    def __init__(self, config: ResolvedLLMConfig) -> None:
        self.config = config

        if not config.api_key and config.provider != "ollama":
            logger.warning(
                "UnifiedLLMProvider initialized without an API key (provider=%s).",
                config.provider,
            )

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Call the configured LLM via LiteLLM."""
        kwargs: dict = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "num_retries": 2,
        }

        # Ollama uses api_base instead of an API key.
        if self.config.provider == "ollama":
            kwargs["api_base"] = self.config.base_url or settings.OLLAMA_URL
        else:
            kwargs["api_key"] = self.config.api_key

        if self.config.base_url and self.config.provider != "ollama":
            kwargs["api_base"] = self.config.base_url

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await litellm.acompletion(**kwargs)

        choice = response.choices[0]
        usage = getattr(response, "usage", None)

        return LLMResponse(
            content=choice.message.content or "",
            model=response.model or self.config.model,
            provider=self.config.provider,
            tokens_used=getattr(usage, "total_tokens", None) if usage else None,
            finish_reason=choice.finish_reason,
        )

    async def health_check(self) -> bool:
        """Verify the credentials and model are usable."""
        try:
            await self.complete(
                system_prompt="You are a health check.",
                user_prompt="ping",
                max_tokens=5,
            )
            return True
        except Exception as exc:
            logger.error("LLM health check failed: %s", exc)
            return False
