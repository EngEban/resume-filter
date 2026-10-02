# ============================================================
# ui/pages/b2c_analyze.py
# B2C: analyze a single resume against a job description.
# ============================================================
from nicegui import app, ui

from ui.api_client import APIError
from ui.components.header import render_header
from ui.components.level_chart import render_level_chart
from ui.components.score_badge import render_score_badge
from ui.state import SessionState
from ui.theme import DANGER, PRIMARY, SUCCESS

SAMPLE_RESUME = """John Doe
Senior Python Backend Developer
Email: john@example.com | Phone: +970 599 123 456 | Gaza

SUMMARY
Backend engineer with 6 years of experience designing scalable APIs.

EXPERIENCE
- Built microservices with FastAPI handling 10M requests/day
- Optimized PostgreSQL queries reducing latency by 60%
- Led a team of 4 engineers, delivered 3 major releases

EDUCATION
BSc in Computer Science, Islamic University of Gaza

SKILLS
Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, Celery
"""

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
        ui.navigate.to("/ui/login")
        return
    if state.account_type != "b2c":
        ui.navigate.to("/ui/dashboard")
        return

    render_header(state)

    with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-6"):
        ui.label("🎯 Analyze Your Resume").classes("text-2xl font-bold")
        ui.label(
            "Paste your resume and the job description to receive "
            "an ATS score with prioritized suggestions."
        ).classes("rf-muted")

        # ---------- Input row ----------
        with ui.row().classes("w-full gap-4 flex-wrap"):
            with ui.column().classes("flex-1 min-w-[380px] gap-2"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label("Resume Text").classes("font-semibold")
                    ui.button(
                        "Load sample",
                        on_click=lambda: resume_input.set_value(SAMPLE_RESUME),
                    ).props("flat dense color=primary")
                resume_input = (
                    ui.textarea()
                    .classes("w-full")
                    .props('outlined rows=18')
                )

            with ui.column().classes("flex-1 min-w-[380px] gap-2"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label("Job Description").classes("font-semibold")
                    ui.button(
                        "Load sample",
                        on_click=lambda: job_input.set_value(SAMPLE_JOB),
                    ).props("flat dense color=primary")
                job_input = (
                    ui.textarea()
                    .classes("w-full")
                    .props('outlined rows=18')
                )

        # ---------- Actions ----------
        with ui.row().classes("w-full items-center gap-4"):
            analyze_btn = ui.button(
                "Analyze",
                on_click=lambda: _run_analyze(
                    state, resume_input, job_input, status, results
                ),
            ).props("color=primary unelevated")

            status = ui.label().classes("text-sm")

        # ---------- Results container ----------
        results = ui.column().classes("w-full gap-6 mt-4")

        # ---------- Initial state ----------
        analyze_btn.set_enabled(True)


async def _run_analyze(
    state: SessionState,
    resume_input,
    job_input,
    status,
    results,
) -> None:
    status.set_text("")
    results.clear()

    resume_text = (resume_input.value or "").strip()
    job_text = (job_input.value or "").strip()

    if len(resume_text) < 50:
        status.set_text("Resume must be at least 50 characters.")
        status.style(f"color: {DANGER}")
        return
    if len(job_text) < 20:
        status.set_text("Job description must be at least 20 characters.")
        status.style(f"color: {DANGER}")
        return

    status.set_text("⏳ Analyzing... This can take 5–15 seconds.")
    status.style(f"color: {PRIMARY}")

    try:
        result = await state.client.analyze(resume_text, job_text)
    except APIError as exc:
        status.set_text(exc.message)
        status.style(f"color: {DANGER}")
        return

    status.set_text("✅ Analysis complete.")
    status.style(f"color: {SUCCESS}")

    with results:
        _render_results(result)


def _render_results(result: dict) -> None:
    # ---------- Score header ----------
    with ui.card().classes("rf-card w-full gap-4"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label("Overall ATS Score").classes("text-lg font-semibold")
            render_score_badge(
                float(result.get("ats_score", 0)),
                result.get("level", "weak"),
            )

        ui.label(
            f"Level: {result.get('level_label', '')}"
        ).classes("text-sm rf-muted")

        # ---------- Breakdown ----------
        ui.label("Score Breakdown").classes("font-semibold mt-2")
        render_level_chart(result.get("breakdown", {}) or {})

    # ---------- Keywords ----------
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

    # ---------- Suggestions ----------
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
                ui.label(kw).classes(
                    "px-2 py-1 rounded text-xs font-medium"
                ).style(
                    f"background-color: {color}15; color: {color};"
                )


def _suggestion_row(s: dict) -> None:
    priority = s.get("priority", "medium")
    p_color = {
        "high": DANGER,
        "medium": "#f59e0b",
        "low": SUCCESS,
    }.get(priority, PRIMARY)

    with ui.column().classes("w-full gap-1 border-l-4 pl-3").style(
        f"border-color: {p_color}"
    ):
        with ui.row().classes("items-center gap-2"):
            ui.label(priority.upper()).classes("text-xs font-bold").style(
                f"color: {p_color}"
            )
            ui.label(s.get("type", "")).classes("text-xs rf-muted")
        ui.label(s.get("description", "")).classes("text-sm")

        if s.get("original"):
            ui.label(f"Original: {s['original']}").classes(
                "text-xs rf-muted italic mt-1"
            )
        if s.get("suggestion"):
            ui.label(f"Suggested: {s['suggestion']}").classes(
                "text-xs mt-1"
            ).style(f"color: {SUCCESS}")