# ============================================================
# app/providers/unified_provider.py
# Unified LLM provider using LiteLLM.
# Supports 100+ providers through a single interface.
# ============================================================
import logging
import socket
from dataclasses import dataclass
from ipaddress import ip_address
from urllib.parse import urlsplit

import litellm

from app.core.config import settings
from app.providers.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)

# Suppress verbose LiteLLM logs.
litellm.set_verbose = False
litellm.suppress_debug_info = True
litellm.drop_params = True


@dataclass
class ResolvedLLMConfig:
    """Resolved LLM configuration for a single request."""
    provider: str
    model: str
    api_key: str
    base_url: str | None = None
    source: str = "platform"


_PLATFORM_HOSTS = {
    "groq": {"api.groq.com"},
    "openai": {"api.openai.com"},
    "anthropic": {"api.anthropic.com"},
    "gemini": {"generativelanguage.googleapis.com", "aiplatform.googleapis.com"},
}
_PLATFORM_HOST_SUFFIXES = {
    "azure": (
        ".openai.azure.com",
        ".cognitiveservices.azure.com",
        ".services.ai.azure.com",
    ),
    "bedrock": (".amazonaws.com", ".amazonaws.com.cn"),
}


def _is_public_ip(value: str) -> bool:
    try:
        address = ip_address(value)
    except ValueError:
        return False

    return bool(
        address.is_global
        and not address.is_private
        and not address.is_loopback
        and not address.is_link_local
        and not address.is_reserved
        and not address.is_multicast
        and not address.is_unspecified
    )


def _resolve_public_host(hostname: str, port: int) -> None:
    try:
        records = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("Platform LLM endpoint hostname could not be resolved") from exc

    addresses = {record[4][0] for record in records if record[4]}
    if not addresses or any(not _is_public_ip(address) for address in addresses):
        raise ValueError("Platform LLM endpoint must resolve only to public IP addresses")


def validate_platform_llm_endpoint(provider: str, base_url: str | None) -> None:
    """Reject unsafe platform endpoints before LiteLLM opens a connection.

    The platform configuration is trusted input, but it still needs a narrow
    safety boundary so a bad deployment value cannot turn the application into
    an internal-network proxy. Official provider hosts are allowed; the local
    Ollama service is limited to the project-owned Docker service.
    """
    candidate = base_url.strip() if base_url else ""
    if provider == "ollama" and not candidate:
        candidate = settings.OLLAMA_URL.strip()
    if not candidate:
        return

    try:
        parsed = urlsplit(candidate)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid platform LLM endpoint URL") from exc

    if (
        not parsed.scheme
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Platform LLM endpoint must not contain credentials, query, or fragment")

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.rstrip(".").lower()

    if provider == "ollama":
        if scheme not in {"http", "https"} or hostname != "ollama" or port not in {None, 11434}:
            raise ValueError("Platform Ollama endpoint must use the project-owned ollama service")
        return

    if scheme != "https" or port not in {None, 443}:
        raise ValueError("Platform LLM endpoints must use HTTPS on port 443")

    allowed_hosts = _PLATFORM_HOSTS.get(provider, set())
    allowed_suffixes = _PLATFORM_HOST_SUFFIXES.get(provider, ())
    if hostname not in allowed_hosts and not any(hostname.endswith(suffix) for suffix in allowed_suffixes):
        raise ValueError("Platform LLM endpoint must use an official provider host")

    _resolve_public_host(hostname, port or 443)


def resolve_llm_config(tenant=None) -> ResolvedLLMConfig:
    """
    Resolve the platform LLM configuration for a request.

    ``tenant`` remains an accepted argument for call-site compatibility and
    future usage metering, but tenant-stored BYOK values are never consulted.
    """
    config = ResolvedLLMConfig(
        provider=settings.PLATFORM_LLM_PROVIDER,
        model=settings.PLATFORM_LLM_MODEL,
        api_key=settings.PLATFORM_LLM_API_KEY,
        base_url=settings.PLATFORM_LLM_BASE_URL,
        source="platform",
    )
    return config


class UnifiedLLMProvider(BaseLLMProvider):
    """
    LLM provider backed by LiteLLM.

    LiteLLM translates a single OpenAI-compatible interface into
    calls to 100+ providers (Groq, OpenAI, Anthropic, Gemini, ...).
    """

    def __init__(self, config: ResolvedLLMConfig) -> None:
        self.config = config
        validate_platform_llm_endpoint(config.provider, config.base_url)

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
        """Verify credentials and model are usable."""
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
