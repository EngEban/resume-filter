# ============================================================
# app/providers/groq_provider.py
# Groq LLM Provider (OpenAI-compatible API).
# ============================================================
import logging

from openai import AsyncOpenAI

from app.core.config import settings
from app.providers.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """
    Groq provider using the OpenAI-compatible SDK.

    Uses an AsyncOpenAI client pointed at Groq's base URL.
    """

    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL

        if not self.api_key:
            logger.warning("GroqProvider initialized without an API key.")

        self.client = AsyncOpenAI(
            api_key=self.api_key or "missing",
            base_url=self.BASE_URL,
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
        """Call Groq chat completions."""
        kwargs: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            provider="groq",
            tokens_used=response.usage.total_tokens if response.usage else None,
            finish_reason=choice.finish_reason,
        )

    async def health_check(self) -> bool:
        """Verify the API key and model are usable."""
        try:
            await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            return True
        except Exception as exc:
            logger.error("Groq health check failed: %s", exc)
            return False