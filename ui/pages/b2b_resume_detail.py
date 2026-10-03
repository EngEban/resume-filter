# ============================================================
# ui/pages/b2b_resume_detail.py
# B2B: full report for a single resume, with PDF export.
# ============================================================
from nicegui import app, ui

from ui.api_client import APIError
from ui.components.header import render_header
from ui.components.level_chart import render_level_chart
from ui.components.score_badge import render_score_badge
from ui.state import SessionState
from ui.theme import DANGER, PRIMARY


def render(resume_id: str) -> None:
    state: SessionState = app.storage.user.get("state") or SessionState()
    app.storage.user["state"] = state

    if not state.is_authenticated:
        ui.navigate.to("/ui/login")
        return
    if state.account_type != "b2b":
        ui.navigate.to("/ui/dashboard")
        return

    render_header(state)

    with ui.column().classes("w-full max-w-5xl mx-auto p-6 gap-4"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.link("← Back", "javascript:history.back()").classes("text-sm no-underline").style(
                f"color: {PRIMARY}"
            )
            ui.label("Resume Report").classes("text-2xl font-bold")

            async def dl_pdf() -> None:
                try:
                    data = await state.client.export_resume_pdf(resume_id)
                    ui.download(data, filename=f"resume_{resume_id[:8]}.pdf")
                except APIError as exc:
                    ui.notify(exc.message, color="negative")

            ui.button("📄 Download PDF", on_click=dl_pdf).props("outline dense color=primary")

        container = ui.column().classes("w-full gap-4")

        async def load() -> None:
            container.clear()
            try:
                report = await state.client.get_resume_report(resume_id)
            except APIError as exc:
                with container:
                    ui.label(exc.message).style(f"color: {DANGER}")
                return

            with container:
                _render_report(report)

        ui.timer(0.1, load, once=True)


def _render_report(r: dict) -> None:
    with ui.card().classes("rf-card w-full gap-3"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.column().classes("gap-0"):
                ui.label(r.get("candidate_name") or "Unknown Candidate").classes(
                    "text-xl font-bold"
                )
                if r.get("candidate_email"):
                    ui.label(r["candidate_email"]).classes("text-sm rf-muted")
                if r.get("candidate_phone"):
                    ui.label(r["candidate_phone"]).classes("text-sm rf-muted")
            render_score_badge(
                float(r.get("ats_score") or 0),
                _level_from_score(float(r.get("ats_score") or 0)),
            )

        ui.label(f"File: {r.get('file_name', '—')}").classes("text-xs rf-muted")
        if r.get("status") == "failed":
            ui.label(f"Error: {r.get('error_message', '')}").style(f"color: {DANGER}")

    breakdown = r.get("score_breakdown") or {}
    if breakdown:
        with ui.card().classes("rf-card w-full gap-3"):
            ui.label("Score Breakdown").classes("font-semibold")
            render_level_chart(breakdown)

    missing = r.get("missing_keywords") or []
    if missing:
        with ui.card().classes("rf-card w-full gap-2"):
            ui.label("Missing Keywords").classes("font-semibold")
            with ui.row().classes("gap-2 flex-wrap"):
                for kw in missing[:60]:
                    ui.label(kw).classes("px-2 py-1 rounded text-xs").style(
                        f"background-color: {DANGER}15; color: {DANGER};"
                    )

    suggestions = r.get("suggestions") or []
    if suggestions:
        with ui.card().classes("rf-card w-full gap-2"):
            ui.label("Suggestions").classes("font-semibold")
            for s in suggestions:
                with (
                    ui.column()
                    .classes("gap-0 border-l-4 pl-3 mt-2")
                    .style(f"border-color: {PRIMARY}")
                ):
                    ui.label(s.get("type", "")).classes("text-xs rf-muted")
                    ui.label(s.get("description", "")).classes("text-sm")


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
