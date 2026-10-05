# ============================================================
# ui/pages/register.py
# Registration page (B2B + B2C).
# ============================================================
import re

from nicegui import app, ui

from ui.api_client import APIError
from ui.state import SessionState
from ui.theme import PRIMARY

_SLUG_RE = re.compile(r"^[a-z0-9-]+$")


def render() -> None:
    state: SessionState = app.storage.user.get("state") or SessionState()
    app.storage.user["state"] = state

    if state.is_authenticated:
        ui.navigate.to("/dashboard")
        return

    is_b2b_default = "b2b" in ui.context.client.page.path

    with (
        ui.column().classes("w-full items-center justify-center min-h-screen gap-6 p-6"),
        ui.card().classes("rf-card w-[28rem] gap-4 p-8"),
    ):
        with ui.column().classes("items-center gap-1"):
            ui.label("📄").classes("text-4xl")
            ui.label("Create your account").classes("text-2xl font-bold")

        account_type = ui.toggle(
            {"b2c": "Individual", "b2b": "Organization"},
            value="b2b" if is_b2b_default else "b2c",
        ).classes("w-full")

        b2b_fields = ui.column().classes("w-full gap-3")
        with b2b_fields:
            org_name = ui.input("Organization Name").classes("w-full").props("outlined dense")
            org_slug = (
                ui.input("Organization Slug (a-z, 0-9, -)")
                .classes("w-full")
                .props("outlined dense")
            )

        def refresh_b2b_visibility() -> None:
            b2b_fields.set_visibility(account_type.value == "b2b")

        account_type.on_value_change(lambda _: refresh_b2b_visibility())
        refresh_b2b_visibility()

        email = ui.input("Email").classes("w-full").props("outlined dense")
        password = (
            ui.input(
                "Password (min 8 chars)",
                password=True,
                password_toggle_button=True,
            )
            .classes("w-full")
            .props("outlined dense")
        )

        status = ui.label().classes("text-sm")

        async def do_register() -> None:
            status.set_text("")
            if not email.value or not password.value:
                status.set_text("Please fill in all required fields.")
                status.style("color: #dc2626")
                return

            if len(password.value) < 8:
                status.set_text("Password must be at least 8 characters.")
                status.style("color: #dc2626")
                return

            if account_type.value == "b2b":
                if not org_name.value or not org_slug.value:
                    status.set_text("Organization name and slug are required.")
                    status.style("color: #dc2626")
                    return
                if not _SLUG_RE.match(org_slug.value):
                    status.set_text(
                        "Slug must contain only lowercase letters, " "digits, and hyphens."
                    )
                    status.style("color: #dc2626")
                    return

            try:
                if account_type.value == "b2c":
                    result = await state.client.register_b2c(email.value, password.value)
                else:
                    result = await state.client.register_b2b(
                        org_name.value,
                        org_slug.value,
                        email.value,
                        password.value,
                    )
                state.client.token = result["access_token"]
                me = await state.client.me()
            except APIError as exc:
                status.set_text(exc.message)
                status.style("color: #dc2626")
                return

            state.set_authenticated(result["access_token"], me)
            ui.navigate.to("/dashboard")

        ui.button("Create account", on_click=do_register).props("color=primary unelevated").classes(
            "w-full"
        )

        with ui.row().classes("items-center justify-center w-full gap-2"):
            ui.label("Already registered?").classes("rf-muted text-sm")
            ui.link("Sign in", "/login").classes("text-sm font-semibold no-underline").style(
                f"color: {PRIMARY}"
            )
