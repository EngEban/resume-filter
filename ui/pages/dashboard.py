# ============================================================
# ui/pages/dashboard.py
# Post-login dashboard: routes user by account type.
# ============================================================
from nicegui import app, ui

from ui.components.header import render_header
from ui.state import SessionState
from ui.theme import PRIMARY


def render() -> None:
    state: SessionState = app.storage.user.get("state") or SessionState()
    app.storage.user["state"] = state

    if not state.is_authenticated:
        ui.navigate.to("/login")
        return

    render_header(state)

    with ui.column().classes("w-full max-w-5xl mx-auto p-6 gap-6"):
        ui.label(f"👋 Welcome, {state.user.get('email')}").classes("text-2xl font-bold")

        if state.account_type == "b2c":
            _render_b2c_home()
        elif state.account_type == "b2b":
            _render_b2b_home()
        else:
            ui.label("Unknown account type.").classes("rf-muted")


def _render_b2c_home() -> None:
    ui.label("Your personal resume analysis space.").classes("rf-muted")

    with ui.row().classes("gap-4 mt-4 flex-wrap"):
        _action_card(
            icon="🎯",
            title="Analyze a Resume",
            description=(
                "Paste your resume and a job description to get an "
                "instant ATS score with suggestions."
            ),
            target="/b2c/analyze",
        )
        _action_card(
            icon="📜",
            title="History",
            description="View your past analyses and track your progress.",
            target="/b2c/history",
        )


def _render_b2b_home() -> None:
    ui.label("Manage your organization's hiring pipeline.").classes("rf-muted")

    with ui.row().classes("gap-4 mt-4 flex-wrap"):
        _action_card(
            icon="📦",
            title="Batches",
            description=("Upload resumes and screen them against a job description."),
            target="/b2b/batches",
        )
        _action_card(
            icon="⚙️",
            title="AI Settings",
            description=("Connect your own AI provider (OpenAI, Anthropic, Gemini, ...)."),
            target="/b2b/settings",
        )


def _action_card(
    icon: str,
    title: str,
    description: str,
    target: str,
) -> None:
    with (
        ui.card()
        .classes("rf-card w-80 gap-2 p-6 cursor-pointer")
        .on("click", lambda: ui.navigate.to(target))
    ):
        ui.label(icon).classes("text-3xl")
        ui.label(title).classes("text-lg font-bold")
        ui.label(description).classes("text-sm rf-muted")
        ui.label("Open →").classes("text-sm font-semibold mt-2").style(f"color: {PRIMARY}")
