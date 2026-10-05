# ============================================================
# ui/components/header.py
# Top navigation bar shared across authenticated pages.
# ============================================================

from nicegui import app, ui

from ui.state import SessionState


def render_header(state: SessionState) -> None:
    """Render the top navigation bar."""
    with ui.row().classes("w-full items-center justify-between rf-header"):
        # ---------- Brand ----------
        with ui.row().classes("items-center gap-2"):
            ui.link("📄 ResumeFilter", "/dashboard").classes(
                "text-white text-lg font-bold no-underline"
            )

        # ---------- Center links ----------
        with ui.row().classes("items-center gap-6"):
            if state.account_type == "b2c":
                _nav_link("Analyze", "/b2c/analyze")
                _nav_link("History", "/b2c/history")
            elif state.account_type == "b2b":
                _nav_link("Batches", "/b2b/batches")
                _nav_link("Settings", "/b2b/settings")

        # ---------- User menu ----------
        with ui.row().classes("items-center gap-3"):
            ui.label(state.user.get("email", "") if state.user else "").classes(
                "text-white text-sm"
            )
            ui.button(
                "Sign out",
                on_click=lambda: _sign_out(state),
            ).props("flat color=white dense")


def _nav_link(label: str, target: str) -> None:
    ui.link(label, target).classes("text-white text-sm no-underline hover:underline")


def _sign_out(state: SessionState) -> None:
    state.clear()
    app.storage.user.pop("state", None)
    ui.navigate.to("/")
