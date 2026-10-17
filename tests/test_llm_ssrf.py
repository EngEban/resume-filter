from types import SimpleNamespace

import pytest

from app import providers as providers_module
from app.core.config import settings as app_settings
from app.providers import resolve_llm_config
from app.providers import unified_provider as provider_module
from app.providers.unified_provider import ResolvedLLMConfig, validate_platform_llm_endpoint


def _public_dns(_hostname, port, **_kwargs):
    return [(2, 1, 6, "", ("93.184.216.34", port))]


def _private_dns(_hostname, port, **_kwargs):
    return [(2, 1, 6, "", ("10.0.0.8", port))]


def test_resolve_llm_config_always_uses_platform_settings(monkeypatch):
    monkeypatch.setattr(app_settings, "PLATFORM_LLM_PROVIDER", "groq")
    monkeypatch.setattr(app_settings, "PLATFORM_LLM_MODEL", "groq/test-model")
    monkeypatch.setattr(app_settings, "PLATFORM_LLM_API_KEY", "platform-key")
    monkeypatch.setattr(app_settings, "PLATFORM_LLM_BASE_URL", None)

    tenant = SimpleNamespace()

    config = resolve_llm_config(tenant)

    assert config.provider == "groq"
    assert config.model == "groq/test-model"
    assert config.api_key == "platform-key"
    assert config.base_url is None
    assert config.source == "platform"


def test_provider_factory_does_not_use_tenant_connection_settings(monkeypatch):
    config = ResolvedLLMConfig(
        provider="groq",
        model="groq/test-model",
        api_key="platform-key",
        source="platform",
    )
    tenant = SimpleNamespace()

    monkeypatch.setattr(providers_module, "resolve_llm_config", lambda: config)
    monkeypatch.setattr(providers_module, "UnifiedLLMProvider", lambda received: received)

    assert providers_module.get_provider(tenant) is config


def test_official_platform_endpoint_is_allowed_without_real_request(monkeypatch):
    calls = []

    def resolver(hostname, port, **kwargs):
        calls.append((hostname, port, kwargs))
        return _public_dns(hostname, port, **kwargs)

    monkeypatch.setattr(provider_module.socket, "getaddrinfo", resolver)

    validate_platform_llm_endpoint("openai", "https://api.openai.com/v1")

    assert calls == [("api.openai.com", 443, {"type": provider_module.socket.SOCK_STREAM})]


@pytest.mark.parametrize(
    "base_url",
    [
        "http://127.0.0.1:8000/v1",
        "https://169.254.169.254/latest/meta-data",
        "https://api.openai.com:8443/v1",
        "https://api.openai.com@evil.example/v1",
        "https://evil.example/v1",
    ],
)
def test_unsafe_platform_endpoint_is_rejected(base_url):
    with pytest.raises(ValueError):
        validate_platform_llm_endpoint("openai", base_url)


def test_dns_rebinding_to_private_address_is_rejected(monkeypatch):
    monkeypatch.setattr(provider_module.socket, "getaddrinfo", _private_dns)

    with pytest.raises(ValueError, match="public IP"):
        validate_platform_llm_endpoint("openai", "https://api.openai.com/v1")


def test_default_docker_ollama_endpoint_is_explicitly_trusted(monkeypatch):
    monkeypatch.setattr(app_settings, "OLLAMA_URL", "http://ollama:11434")

    validate_platform_llm_endpoint("ollama", None)
    validate_platform_llm_endpoint("ollama", "http://ollama:11434/")