# ============================================================
# ui/pages/login.py
# Login page (both B2B and B2C).
# ============================================================
from nicegui import app, ui

from ui.api_client import APIError
from ui.state import SessionState
from ui.theme import PRIMARY


def render() -> None:
    state: SessionState = app.storage.user.get("state") or SessionState()
    app.storage.user["state"] = state

    if state.is_authenticated:
        ui.navigate.to("/ui/dashboard")
        return

    with (
        ui.column().classes(
            "w-full items-center justify-center min-h-screen gap-6 p-6"
        ),
        ui.card().classes("rf-card w-96 gap-4 p-8"),
    ):
        with ui.column().classes("items-center gap-1"):
            ui.label("📄").classes("text-4xl")
            ui.label("Welcome back").classes("text-2xl font-bold")
            ui.label("Sign in to continue").classes("rf-muted text-sm")

        email = ui.input("Email").classes("w-full").props("outlined dense")
        password = (
            ui.input("Password", password=True, password_toggle_button=True)
            .classes("w-full")
            .props("outlined dense")
        )

        status = ui.label().classes("text-sm")

        async def do_login() -> None:
            status.set_text("")
            if not email.value or not password.value:
                status.set_text("Please fill in all fields.")
                status.style("color: #dc2626")
                return

            try:
                result = await state.client.login(email.value, password.value)
                state.client.token = result["access_token"]
                me = await state.client.me()
            except APIError as exc:
                status.set_text(exc.message)
                status.style("color: #dc2626")
                return

            state.set_authenticated(result["access_token"], me)
            ui.navigate.to("/ui/dashboard")

        ui.button("Sign in", on_click=do_login).props(
            "color=primary unelevated"
        ).classes("w-full")

        ui.separator()

        with ui.row().classes("items-center justify-center w-full gap-2"):
            ui.label("New here?").classes("rf-muted text-sm")
            ui.link("Create account", "/ui/register").classes(
                "text-sm font-semibold no-underline"
            ).style(f"color: {PRIMARY}")

        password.on("keydown.enter", do_login)
