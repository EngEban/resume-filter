# ============================================================
# ui/pages/b2c_history.py
# B2C: past analysis history.
# ============================================================
from nicegui import app, ui

from ui.api_client import APIError
from ui.components.header import render_header
from ui.components.score_badge import render_score_badge
from ui.state import SessionState
from ui.theme import DANGER


def render() -> None:
    state: SessionState = app.storage.user.get("state") or SessionState()
    app.storage.user["state"] = state

    if not state.is_authenticated:
        ui.navigate.to("/login")
        return
    if state.account_type != "b2c":
        ui.navigate.to("/dashboard")
        return

    render_header(state)

    with ui.column().classes("w-full max-w-5xl mx-auto p-6 gap-4"):
        ui.label("📜 Your Analysis History").classes("text-2xl font-bold")

        container = ui.column().classes("w-full gap-3 mt-2")

        async def load() -> None:
            container.clear()
            try:
                items = await state.client.b2c_history(limit=50)
            except APIError as exc:
                with container:
                    ui.label(exc.message).style(f"color: {DANGER}")
                return

            with container:
                if not items:
                    ui.label("No analyses yet.").classes("rf-muted")
                    ui.button(
                        "Analyze your first resume",
                        on_click=lambda: ui.navigate.to("/b2c/analyze"),
                    ).props("color=primary")
                    return

                for item in items:
                    _history_row(item)

        ui.timer(0.1, load, once=True)


def _history_row(item: dict) -> None:
    with ui.card().classes("rf-card w-full gap-2"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(item.get("created_at", "")[:19].replace("T", " ")).classes("rf-muted text-sm")
            render_score_badge(
                float(item.get("ats_score", 0) or 0),
                _level_from_score(float(item.get("ats_score", 0) or 0)),
            )

        missing = item.get("missing_keywords", []) or []
        if missing:
            with ui.row().classes("gap-2 flex-wrap mt-1"):
                ui.label("Missing:").classes("text-xs rf-muted")
                for kw in missing[:12]:
                    ui.label(kw).classes("px-2 py-0.5 rounded text-xs").style(
                        f"background-color: {DANGER}15; color: {DANGER};"
                    )


def _level_from_score(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 60:
        return "average"
    if score >= 40:
        return "below_average"
    return "weak"
