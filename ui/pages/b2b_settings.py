# ============================================================
# ui/pages/b2b_settings.py
# B2B: manage the tenant's LLM provider (BYOK).
# ============================================================
from nicegui import app, ui

from ui.api_client import APIError
from ui.components.header import render_header
from ui.state import SessionState
from ui.theme import DANGER, PRIMARY, SUCCESS


def render() -> None:
    state: SessionState = app.storage.user.get("state") or SessionState()
    app.storage.user["state"] = state

    if not state.is_authenticated:
        ui.navigate.to("/ui/login")
        return
    if state.account_type != "b2b":
        ui.navigate.to("/ui/dashboard")
        return

    render_header(state)

    with ui.column().classes("w-full max-w-3xl mx-auto p-6 gap-6"):
        ui.label("⚙️ AI Provider Settings").classes("text-2xl font-bold")
        ui.label(
            "By default, the platform's AI provider is used. "
            "You can connect your own provider (BYOK) for higher limits "
            "and full control."
        ).classes("rf-muted")

        current_card = ui.card().classes("rf-card w-full gap-2")
        form_card = ui.card().classes("rf-card w-full gap-4")

        async def load_current() -> None:
            current_card.clear()
            try:
                info = await state.client.get_llm_settings()
            except APIError as exc:
                with current_card:
                    ui.label(exc.message).style(f"color: {DANGER}")
                return

            with current_card:
                ui.label("Current configuration").classes("font-semibold")
                with ui.row().classes("items-center gap-3 flex-wrap"):
                    ui.label(f"Provider: {info.get('provider', '—')}").classes(
                        "text-sm"
                    )
                    ui.label(f"Model: {info.get('model', '—')}").classes(
                        "text-sm"
                    )
                    source = info.get("source")
                    badge_text = (
                        "Your Key" if source == "tenant" else "Platform Default"
                    )
                    badge_color = SUCCESS if source == "tenant" else PRIMARY
                    ui.label(badge_text).classes(
                        "px-2 py-0.5 rounded text-xs font-semibold"
                    ).style(
                        f"background-color: {badge_color}15; color: {badge_color};"
                    )

                if info.get("has_custom_key"):
                    ui.button(
                        "Remove my key (revert to platform)",
                        on_click=lambda: _remove_key(state, load_current),
                    ).props("flat dense color=negative")

        ui.timer(0.1, load_current, once=True)

        async def build_form() -> None:
            try:
                data = await state.client.list_providers()
            except APIError as exc:
                with form_card:
                    ui.label(exc.message).style(f"color: {DANGER}")
                return

            providers = data.get("providers", [])
            provider_map = {p["provider"]: p for p in providers}

            with form_card:
                ui.label("Configure a provider").classes("font-semibold")

                provider_select = (
                    ui.select(
                        options=list(provider_map.keys()),
                        value=providers[0]["provider"] if providers else "groq",
                        label="Provider",
                    )
                    .classes("w-full")
                    .props("outlined dense")
                )

                model_select = (
                    ui.select(
                        options=provider_map.get(provider_select.value, {}).get(
                            "models", []
                        ),
                        label="Model",
                    )
                    .classes("w-full")
                    .props("outlined dense")
                )

                def on_provider_change() -> None:
                    meta = provider_map.get(provider_select.value, {})
                    model_select.options = meta.get("models", [])
                    model_select.value = (
                        meta["models"][0] if meta.get("models") else None
                    )
                    model_select.update()

                provider_select.on_value_change(
                    lambda _: on_provider_change()
                )
                if providers:
                    on_provider_change()

                api_key = (
                    ui.input(
                        "API Key",
                        password=True,
                        password_toggle_button=True,
                    )
                    .classes("w-full")
                    .props("outlined dense")
                )

                base_url = (
                    ui.input("Base URL (optional, for Azure / Ollama)")
                    .classes("w-full")
                    .props("outlined dense")
                )

                status = ui.label().classes("text-sm")

                async def test_connection() -> None:
                    status.set_text("⏳ Testing connection...")
                    status.style(f"color: {PRIMARY}")
                    try:
                        result = await state.client.test_llm_connection(
                            provider=provider_select.value,
                            model=model_select.value or "",
                            api_key=api_key.value or None,
                            base_url=base_url.value or None,
                        )
                    except APIError as exc:
                        status.set_text(exc.message)
                        status.style(f"color: {DANGER}")
                        return

                    if result.get("success"):
                        latency = result.get("latency_ms")
                        status.set_text(
                            f"✅ Connection OK ({latency} ms)"
                            if latency
                            else "✅ Connection OK"
                        )
                        status.style(f"color: {SUCCESS}")
                    else:
                        status.set_text(result.get("message", "Failed"))
                        status.style(f"color: {DANGER}")

                async def save() -> None:
                    status.set_text("")
                    if not model_select.value:
                        status.set_text("Please select a model.")
                        status.style(f"color: {DANGER}")
                        return

                    try:
                        await state.client.update_llm_settings(
                            provider=provider_select.value,
                            model=model_select.value,
                            api_key=api_key.value or None,
                            base_url=base_url.value or None,
                        )
                    except APIError as exc:
                        status.set_text(exc.message)
                        status.style(f"color: {DANGER}")
                        return

                    status.set_text("✅ Settings saved.")
                    status.style(f"color: {SUCCESS}")
                    await load_current()

                with ui.row().classes("gap-2 mt-2"):
                    ui.button(
                        "Test Connection",
                        on_click=test_connection,
                    ).props("outline color=primary")
                    ui.button(
                        "Save",
                        on_click=save,
                    ).props("color=primary unelevated")

        ui.timer(0.2, build_form, once=True)


async def _remove_key(state: SessionState, refresh_cb) -> None:
    try:
        await state.client.delete_llm_settings()
    except APIError as exc:
        ui.notify(exc.message, color="negative")
        return
    ui.notify("Reverted to platform default.", color="positive")
    await refresh_cb()
