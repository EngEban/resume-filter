# ============================================================
# app/providers/base.py
# Abstract base for LLM providers.
# ============================================================
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Structured response from an LLM provider."""
    content: str
    model: str
    provider: str
    tokens_used: int | None = None
    finish_reason: str | None = None


class BaseLLMProvider(ABC):
    """
    Abstract interface every LLM provider must implement.
    Ensures the rest of the code is decoupled from any specific vendor.
    """

    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """
        Send a chat completion request.

        Args:
            system_prompt: The system role instruction.
            user_prompt: The user message.
            json_mode: If True, request structured JSON output.
            temperature: Sampling temperature (0.0 - 1.0).
            max_tokens: Maximum tokens in the response.

        Returns:
            LLMResponse with the model's content.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable and credentials are valid."""
        ...
