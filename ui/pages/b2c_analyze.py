# ============================================================
# ui/pages/b2c_analyze.py
# B2C: upload a resume file and analyze it.
# ============================================================
from nicegui import app, ui

from ui.api_client import APIError
from ui.components.header import render_header
from ui.components.level_chart import render_level_chart
from ui.components.score_badge import render_score_badge
from ui.state import SessionState
from ui.theme import DANGER, PRIMARY, SUCCESS

SAMPLE_JOB = """We are hiring a Senior Python Backend Developer.

Requirements:
- 5+ years of Python experience
- Strong knowledge of FastAPI and PostgreSQL
- Experience with Docker and Kubernetes
- Familiarity with Redis and Celery
- Fluent in English and Arabic
"""


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

    # ---------- Uploaded file buffer ----------
    uploaded: dict = {"name": None, "content": None}

    with ui.column().classes("w-full max-w-5xl mx-auto p-6 gap-6"):
        ui.label("🎯 Analyze Your Resume").classes("text-2xl font-bold")
        ui.label(
            "Upload your resume (PDF or DOCX) and paste the job "
            "description to receive an ATS score with suggestions."
        ).classes("rf-muted")

        # ---------- Resume upload ----------
        with ui.card().classes("rf-card w-full gap-3"):
            ui.label("1. Your Resume").classes("font-semibold")

            def handle_upload(e) -> None:
                try:
                    content = e.content.read()
                    uploaded["name"] = e.name
                    uploaded["content"] = content
                    upload_status.set_text(
                        f"✅ Uploaded: {e.name} " f"({len(content) / 1024:.1f} KB)"
                    )
                    upload_status.style(f"color: {SUCCESS}")
                except Exception as ex:
                    upload_status.set_text(f"❌ Upload failed: {ex}")
                    upload_status.style(f"color: {DANGER}")

            ui.upload(
                label="Upload PDF or DOCX",
                auto_upload=True,
                on_upload=handle_upload,
                max_file_size=10 * 1024 * 1024,
                max_files=1,
            ).classes("w-full").props("accept=.pdf,.docx")

            upload_status = ui.label().classes("text-sm")

            ui.label("Supported formats: PDF, DOCX. Max size: 10 MB.").classes("text-xs rf-muted")

        # ---------- Job description ----------
        with ui.card().classes("rf-card w-full gap-3"):
            with ui.row().classes("items-center justify-between w-full"):
                ui.label("2. Job Description").classes("font-semibold")
                ui.button(
                    "Load sample",
                    on_click=lambda: job_input.set_value(SAMPLE_JOB),
                ).props("flat dense color=primary")

            job_input = ui.textarea().classes("w-full").props("outlined rows=10")

        # ---------- Actions ----------
        with ui.row().classes("w-full items-center gap-4"):
            ui.button(
                "Analyze Resume",
                on_click=lambda: _run_analyze(state, uploaded, job_input, status, results),
            ).props("color=primary unelevated")

            status = ui.label().classes("text-sm")

        # ---------- Results ----------
        results = ui.column().classes("w-full gap-6 mt-4")


async def _run_analyze(
    state: SessionState,
    uploaded: dict,
    job_input,
    status,
    results,
) -> None:
    status.set_text("")
    results.clear()

    # ---------- Validate upload ----------
    if not uploaded.get("content"):
        status.set_text("Please upload a resume file (PDF or DOCX).")
        status.style(f"color: {DANGER}")
        return

    file_name = uploaded["name"]
    file_bytes = uploaded["content"]

    # ---------- Validate job description ----------
    job_text = (job_input.value or "").strip()
    if len(job_text) < 20:
        status.set_text("Job description must be at least 20 characters.")
        status.style(f"color: {DANGER}")
        return

    status.set_text("⏳ Analyzing... This can take 5-20 seconds.")
    status.style(f"color: {PRIMARY}")

    try:
        result = await state.client.analyze(
            file_content=file_bytes,
            file_name=file_name,
            job_description=job_text,
        )
    except APIError as exc:
        status.set_text(exc.message)
        status.style(f"color: {DANGER}")
        return

    status.set_text("✅ Analysis complete.")
    status.style(f"color: {SUCCESS}")

    with results:
        _render_results(result)


def _render_results(result: dict) -> None:
    with ui.card().classes("rf-card w-full gap-4"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label("Overall ATS Score").classes("text-lg font-semibold")
            render_score_badge(
                float(result.get("ats_score", 0)),
                result.get("level", "weak"),
            )

        ui.label(f"Level: {result.get('level_label', '')}").classes("text-sm rf-muted")

        ui.label("Score Breakdown").classes("font-semibold mt-2")
        render_level_chart(result.get("breakdown", {}) or {})

    with ui.row().classes("w-full gap-4 flex-wrap"):
        _keyword_card(
            "Matched Keywords",
            result.get("matched_keywords", []) or [],
            color=SUCCESS,
        )
        _keyword_card(
            "Missing Keywords",
            result.get("missing_keywords", []) or [],
            color=DANGER,
        )

    suggestions = result.get("suggestions", []) or []
    if suggestions:
        with ui.card().classes("rf-card w-full gap-3"):
            ui.label("💡 Suggestions").classes("text-lg font-semibold")
            for s in suggestions:
                _suggestion_row(s)


def _keyword_card(title: str, keywords: list, color: str) -> None:
    with ui.card().classes("rf-card flex-1 min-w-[300px] gap-2"):
        ui.label(title).classes("font-semibold")

        if not keywords:
            ui.label("—").classes("rf-muted text-sm")
            return

        with ui.row().classes("gap-2 flex-wrap"):
            for kw in keywords[:60]:
                ui.label(kw).classes("px-2 py-1 rounded text-xs font-medium").style(
                    f"background-color: {color}15; color: {color};"
                )


def _suggestion_row(s: dict) -> None:
    priority = s.get("priority", "medium")
    p_color = {
        "high": DANGER,
        "medium": "#f59e0b",
        "low": SUCCESS,
    }.get(priority, PRIMARY)

    with ui.column().classes("w-full gap-1 border-l-4 pl-3").style(f"border-color: {p_color}"):
        with ui.row().classes("items-center gap-2"):
            ui.label(priority.upper()).classes("text-xs font-bold").style(f"color: {p_color}")
            ui.label(s.get("type", "")).classes("text-xs rf-muted")
        ui.label(s.get("description", "")).classes("text-sm")

        if s.get("original"):
            ui.label(f"Original: {s['original']}").classes("text-xs rf-muted italic mt-1")
        if s.get("suggestion"):
            ui.label(f"Suggested: {s['suggestion']}").classes("text-xs mt-1").style(
                f"color: {SUCCESS}"
            )
