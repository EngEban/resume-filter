# ============================================================
# app/providers/ollama_provider.py
# Ollama Provider (local LLM, OpenAI-compatible endpoint).
# ============================================================
import logging

from openai import AsyncOpenAI

from app.core.config import settings
from app.providers.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    Ollama provider using its OpenAI-compatible endpoint.

    Requires an Ollama server running locally (or in Docker).
    """

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = (base_url or settings.OLLAMA_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

        self.client = AsyncOpenAI(
            api_key="ollama",  # required by the SDK but unused by Ollama
            base_url=f"{self.base_url}/v1",
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
        """Call Ollama chat completions."""
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
            provider="ollama",
            tokens_used=response.usage.total_tokens if response.usage else None,
            finish_reason=choice.finish_reason,
        )

    async def health_check(self) -> bool:
        """Verify Ollama is reachable."""
        try:
            await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            return True
        except Exception as exc:
            logger.error("Ollama health check failed: %s", exc)
            return False
