# ============================================================
# ui/pages/b2b_batches.py
# B2B: list batches + create a new batch.
# ============================================================
import base64

from nicegui import app, ui

from ui.api_client import APIError
from ui.components.header import render_header
from ui.state import SessionState
from ui.theme import DANGER, NEUTRAL, PRIMARY, SUCCESS, WARNING


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

    with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-6"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label("📦 Batches").classes("text-2xl font-bold")
            ui.button(
                "New Batch",
                on_click=lambda: _open_new_batch_dialog(state, refresh),
            ).props("color=primary unelevated")

        ui.label(
            "Manage all your resume screening batches."
        ).classes("rf-muted")

        # ---------- Filters ----------
        with ui.row().classes("gap-3 items-center w-full flex-wrap"):
            search = (
                ui.input("Search by job title")
                .classes("flex-1 min-w-[220px]")
                .props("outlined dense")
            )
            status_filter = (
                ui.select(
                    options={
                        "": "All",
                        "pending": "Pending",
                        "processing": "Processing",
                        "completed": "Completed",
                        "failed": "Failed",
                    },
                    value="",
                    label="Status",
                )
                .classes("min-w-[160px]")
                .props("outlined dense")
            )
            ui.button(
                "Refresh",
                on_click=lambda: refresh(),
            ).props("color=primary outline dense")

        # ---------- List container ----------
        container = ui.column().classes("w-full gap-3 mt-2")

    async def refresh() -> None:
        container.clear()
        try:
            batches = await state.client.list_batches(
                status=status_filter.value or None,
                search=search.value or None,
                limit=100,
            )
        except APIError as exc:
            with container:
                ui.label(exc.message).style(f"color: {DANGER}")
            return

        with container:
            if not batches:
                ui.label("No batches yet.").classes("rf-muted")
                return

            for b in batches:
                _batch_row(b)


def _batch_row(b: dict) -> None:
    status = b.get("status", "unknown")
    color = _status_color(status)

    with ui.card().classes(
        "rf-card w-full cursor-pointer"
    ).on(
        "click",
        lambda: ui.navigate.to(f"/ui/b2b/batches/{b['id']}"),
    ):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.column().classes("gap-0 flex-1"):
                ui.label(b.get("job_title", "Untitled")).classes(
                    "text-lg font-semibold"
                )
                with ui.row().classes("items-center gap-3"):
                    ui.label(f"ID: {b['id'][:8]}…").classes(
                        "text-xs rf-muted"
                    )
                    ui.label(
                        f"Created: {(b.get('created_at') or '')[:19].replace('T', ' ')}"
                    ).classes("text-xs rf-muted")

            with ui.row().classes("items-center gap-4"):
                with ui.column().classes("items-end gap-0"):
                    ui.label(
                        f"{b.get('completed', 0)}/{b.get('total_resumes', 0)}"
                    ).classes("text-lg font-bold").style(f"color: {PRIMARY}")
                    ui.label("completed").classes("text-xs rf-muted")
                ui.label(status).classes(
                    "px-3 py-1 rounded text-xs font-semibold"
                ).style(f"background-color: {color}15; color: {color};")


def _status_color(status: str | None) -> str:
    if status == "completed":
        return SUCCESS
    if status in ("pending", "processing"):
        return WARNING
    if status == "failed":
        return DANGER
    return NEUTRAL


def _open_new_batch_dialog(state: SessionState, on_success) -> None:
    with ui.dialog() as dialog, ui.card().classes(
        "rf-card w-[40rem] gap-4 p-6"
    ):
        ui.label("Create New Batch").classes("text-xl font-bold")

        job_title = (
            ui.input("Job Title").classes("w-full").props("outlined dense")
        )
        job_description = (
            ui.textarea("Job Description")
            .classes("w-full")
            .props("outlined rows=6")
        )
        job_requirements = (
            ui.textarea("Job Requirements (optional)")
            .classes("w-full")
            .props("outlined rows=3")
        )

        upload = (
            ui.upload(
                label="Upload resumes (PDF, DOCX)",
                multiple=True,
                auto_upload=False,
                max_file_size=10 * 1024 * 1024,
            )
            .classes("w-full")
            .props("accept=.pdf,.docx")
        )

        status = ui.label().classes("text-sm")

        async def submit() -> None:
            status.set_text("")

            if not job_title.value or not job_description.value:
                status.set_text("Job title and description are required.")
                status.style(f"color: {DANGER}")
                return

            raw_files = getattr(upload, "_files", None) or []
            if not raw_files:
                status.set_text("Please attach at least one resume.")
                status.style(f"color: {DANGER}")
                return

            status.set_text("⏳ Uploading...")
            status.style(f"color: {PRIMARY}")

            try:
                result = await state.client.create_batch(
                    job_title=job_title.value,
                    job_description=job_description.value,
                    job_requirements=job_requirements.value or None,
                    files=_build_files_payload(raw_files),
                )
            except APIError as exc:
                status.set_text(exc.message)
                status.style(f"color: {DANGER}")
                return

            batch_id = result.get("id")
            dialog.close()
            ui.notify(f"Batch created: {batch_id[:8]}…", color="positive")
            ui.navigate.to(f"/ui/b2b/batches/{batch_id}")

        with ui.row().classes("w-full justify-end gap-2 mt-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Create", on_click=submit).props(
                "color=primary unelevated"
            )

    dialog.open()


def _build_files_payload(files: list) -> list:
    """Convert NiceGUI upload entries to httpx (name, bytes, mime) tuples."""
    payload: list = []
    for entry in files:
        name = entry.get("name") or "resume"
        mime = entry.get("type") or "application/octet-stream"
        content_b64 = entry.get("content") or ""
        data = base64.b64decode(content_b64)
        payload.append(("files", (name, data, mime)))
    return payload