# ============================================================
# ui/pages/landing.py
# Public landing page.
# ============================================================
from nicegui import ui

from ui.theme import PRIMARY


def render() -> None:
    with ui.column().classes("w-full items-center justify-center min-h-screen gap-8 p-6"):
        # ---------- Hero ----------
        with ui.column().classes("items-center gap-3"):
            ui.label("📄 ResumeFilter").classes("text-5xl font-bold").style(f"color: {PRIMARY}")
            ui.label("AI-powered resume screening and ATS scoring").classes("text-lg rf-muted")

        # ---------- Feature cards ----------
        with ui.row().classes("gap-6 mt-4 flex-wrap justify-center"):
            _feature_card(
                icon="🎯",
                title="For Individuals",
                description=(
                    "Score your resume against any job and get "
                    "actionable, prioritized suggestions."
                ),
                target="/register?type=b2c",
                cta="Get Started Free",
            )
            _feature_card(
                icon="🏢",
                title="For Organizations",
                description=(
                    "Screen hundreds of resumes in minutes. "
                    "Bring your own AI provider or use ours."
                ),
                target="/register?type=b2b",
                cta="Create Organization",
            )

        # ---------- Login link ----------
        with ui.row().classes("items-center gap-2 mt-6"):
            ui.label("Already have an account?").classes("rf-muted")
            ui.link("Sign in", "/login").classes("font-semibold no-underline").style(
                f"color: {PRIMARY}"
            )

        # ---------- Footer ----------
        with ui.row().classes("items-center gap-4 mt-12"):
            ui.label("MIT Licensed").classes("text-xs rf-muted")
            ui.label("•").classes("text-xs rf-muted")
            ui.link("API Docs", "/docs").classes("text-xs rf-muted no-underline")


def _feature_card(
    icon: str,
    title: str,
    description: str,
    target: str,
    cta: str,
) -> None:
    with ui.card().classes("rf-card w-80 items-center gap-3 p-6"):
        ui.label(icon).classes("text-4xl")
        ui.label(title).classes("text-xl font-bold")
        ui.label(description).classes("text-center text-sm rf-muted")
        ui.button(cta, on_click=lambda: ui.navigate.to(target)).props(
            "color=primary unelevated"
        ).classes("w-full mt-2")
