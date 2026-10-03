# ============================================================
# ui/state.py
# Per-session UI state (auth token, current user).
# ============================================================
from dataclasses import dataclass, field

from ui.api_client import APIClient


@dataclass
class SessionState:
    """State attached to each NiceGUI browser session."""

    client: APIClient = field(default_factory=APIClient)
    user: dict | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None and self.client.token is not None

    @property
    def account_type(self) -> str | None:
        return self.user.get("account_type") if self.user else None

    @property
    def tenant_id(self) -> str | None:
        return self.user.get("tenant_id") if self.user else None

    def set_authenticated(self, token: str, user: dict) -> None:
        self.client.token = token
        self.user = user

    def clear(self) -> None:
        self.client.token = None
        self.user = None
