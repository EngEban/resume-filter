# ============================================================
# app/schemas/settings.py
# Pydantic schemas for tenant LLM settings.
# ============================================================
from pydantic import BaseModel, Field

SUPPORTED_PROVIDERS = [
    "groq",
    "openai",
    "anthropic",
    "gemini",
    "azure",
    "bedrock",
    "ollama",
]

# Suggested models per provider (used by the UI dropdown).
SUGGESTED_MODELS: dict[str, list[str]] = {
    "groq": [
        "groq/openai/gpt-oss-20b",
        "groq/openai/gpt-oss-120b",
        "groq/qwen/qwen3-32b",
    ],
    "openai": [
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "openai/gpt-4-turbo",
    ],
    "anthropic": [
        "anthropic/claude-sonnet-4-20250514",
        "anthropic/claude-3-5-haiku-20241022",
    ],
    "gemini": [
        "gemini/gemini-1.5-pro",
        "gemini/gemini-1.5-flash",
        "gemini/gemini-2.0-flash",
    ],
    "azure": [
        "azure/gpt-4o",
        "azure/gpt-4o-mini",
    ],
    "bedrock": [
        "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
    ],
    "ollama": [
        "ollama/llama3.1:8b",
        "ollama/qwen2.5:7b",
        "ollama/mistral:7b",
    ],
}


class LLMSettingsUpdate(BaseModel):
    """Payload for updating a tenant's LLM configuration."""

    provider: str = Field(..., pattern="^[a-z_]+$")
    model: str = Field(..., min_length=3, max_length=150)
    api_key: str | None = Field(default=None, max_length=500)
    base_url: str | None = Field(default=None, max_length=255)


class LLMSettingsRead(BaseModel):
    """Current tenant LLM settings (never exposes the key)."""

    provider: str
    model: str
    has_custom_key: bool
    base_url: str | None = None
    source: str  # "platform" or "tenant"


class ProviderInfo(BaseModel):
    """Available provider and its suggested models."""

    provider: str
    models: list[str]
    requires_api_key: bool
    supports_base_url: bool


class ProvidersListResponse(BaseModel):
    """List of available providers."""

    providers: list[ProviderInfo]
    platform_default: dict


class ConnectionTestResult(BaseModel):
    """Result of a connection test."""

    success: bool
    message: str
    latency_ms: int | None = None
