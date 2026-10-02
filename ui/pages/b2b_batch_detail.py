# ============================================================
# ui/pages/b2b_batch_detail.py
# B2B: view a single batch with its resumes and scores.
# ============================================================
import asyncio

from nicegui import app, ui

from ui.api_client import APIError
from ui.components.header import render_header
from ui.components.stat_card import render_stat_card
from ui.state import SessionState
from ui.theme import DANGER, NEUTRAL, PRIMARY, SUCCESS, WARNING


def render(batch_id: str) -> None:
    state: SessionState = app.storage.user.get("state") or SessionState()
    app.storage.user["state"] = state

    if not state.is_authenticated:
        ui.navigate.to("/ui/login")
        return
    if state.account_type != "b2b":
        ui.navigate.to("/ui/dashboard")
        return

    render_header(state)

    with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-4"):
        with ui.row().classes("items-center gap-2"):
            ui.link("← Back to batches", "/ui/b2b/batches").classes(
                "text-sm no-underline"
            ).style(f"color: {PRIMARY}")
            ui.label(f"Batch: {batch_id[:8]}…").classes(
                "text-xl font-bold"
            )

        # ---------- Summary card ----------
        summary_row = ui.row().classes("gap-4 flex-wrap mt-2")

        # ---------- Resumes container ----------
        ui.label("Resumes").classes("text-lg font-semibold mt-4")
        table_container = ui.column().classes("w-full mt-2")

    async def refresh() -> None:
        try:
            batch = await state.client.get_batch(batch_id)
            resumes = await state.client.list_batch_resumes(batch_id)
        except APIError as exc:
            ui.notify(exc.message, color="negative")
            return

        # ---------- Summary ----------
        summary_row.clear()
        with summary_row:
            render_stat_card(
                "Total",
                batch.get("total_resumes", 0),
                color=PRIMARY,
            )
            render_stat_card(
                "Completed",
                batch.get("completed", 0),
                color=SUCCESS,
            )
            render_stat_card(
                "Failed",
                batch.get("failed", 0),
                color=DANGER,
            )
            render_stat_card(
                "Status",
                batch.get("status", "?"),
                color=_status_color(batch.get("status")),
            )

        # ---------- Resumes table ----------
        table_container.clear()
        with table_container:
            if not resumes:
                ui.label("No resumes yet.").classes("rf-muted")
                return

            with ui.card().classes("rf-card w-full p-0 overflow-hidden"):
                columns = [
                    {"name": "name", "label": "Candidate", "field": "candidate_name", "align": "left"},
                    {"name": "email", "label": "Email", "field": "candidate_email", "align": "left"},
                    {"name": "score", "label": "Score", "field": "ats_score", "align": "left"},
                    {"name": "status", "label": "Status", "field": "status", "align": "left"},
                ]
                rows = []
                for r in sorted(
                    resumes,
                    key=lambda x: (x.get("ats_score") or 0),
                    reverse=True,
                ):
                    rows.append(
                        {
                            "id": r.get("id"),
                            "candidate_name": r.get("candidate_name") or "—",
                            "candidate_email": r.get("candidate_email") or "—",
                            "ats_score": (
                                f"{r['ats_score']:.1f}"
                                if r.get("ats_score") is not None
                                else "—"
                            ),
                            "status": r.get("status", "—"),
                        }
                    )

                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key="id",
                ).classes("w-full")

                table.on(
                    "rowClick",
                    lambda e: ui.navigate.to(
                        f"/ui/b2b/resumes/{e.args[1]['id']}"
                    ),
                )

    ui.timer(0.1, refresh, once=True)

    # Auto-refresh while processing
    async def auto_refresh() -> None:
        while True:
            await asyncio.sleep(5)
            try:
                batch = await state.client.get_batch(batch_id)
                if batch.get("status") not in ("pending", "processing"):
                    break
                await refresh()
            except Exception:
                break

    ui.timer(0.1, auto_refresh, once=True)


def _status_color(status: str | None) -> str:
    if status == "completed":
        return SUCCESS
    if status in ("pending", "processing"):
        return WARNING
    if status == "failed":
        return DANGER
    return NEUTRAL