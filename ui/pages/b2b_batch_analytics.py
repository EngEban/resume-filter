# ============================================================
# ui/pages/b2b_batch_analytics.py
# B2B: analytics for a single batch.
# ============================================================
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

    with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-6"):
        with ui.row().classes("items-center gap-2"):
            ui.link("← Back to batch", f"/ui/b2b/batches/{batch_id}").classes(
                "text-sm no-underline"
            ).style(f"color: {PRIMARY}")
            ui.label("Analytics").classes("text-2xl font-bold")

        container = ui.column().classes("w-full gap-4")

        async def load() -> None:
            container.clear()
            try:
                data = await state.client.batch_analytics(batch_id)
            except APIError as exc:
                with container:
                    ui.label(exc.message).style(f"color: {DANGER}")
                return

            with container:
                _render(data)

        ui.timer(0.1, load, once=True)


def _render(data: dict) -> None:
    ui.label(data.get("job_title", "—")).classes("text-lg font-semibold")

    # ---------- Stats row ----------
    with ui.row().classes("gap-4 flex-wrap"):
        render_stat_card("Total", data.get("total_resumes", 0), PRIMARY)
        render_stat_card("Completed", data.get("completed", 0), SUCCESS)
        render_stat_card("Failed", data.get("failed", 0), DANGER)
        render_stat_card("Pending", data.get("pending", 0), WARNING)

    # ---------- Score stats ----------
    with ui.row().classes("gap-4 flex-wrap mt-2"):
        avg = data.get("avg_score")
        render_stat_card("Avg Score", f"{avg:.1f}" if avg is not None else "—", PRIMARY)
        med = data.get("median_score")
        render_stat_card("Median", f"{med:.1f}" if med is not None else "—", PRIMARY)
        mn = data.get("min_score")
        render_stat_card("Min", f"{mn:.1f}" if mn is not None else "—", NEUTRAL)
        mx = data.get("max_score")
        render_stat_card("Max", f"{mx:.1f}" if mx is not None else "—", NEUTRAL)

    # ---------- Distribution ----------
    dist = data.get("score_distribution", {}) or {}
    with ui.card().classes("rf-card w-full gap-3 mt-4"):
        ui.label("Score Distribution").classes("font-semibold")
        for level, color in [
            ("excellent", SUCCESS),
            ("good", SUCCESS),
            ("average", WARNING),
            ("below_average", "#ea580c"),
            ("weak", DANGER),
        ]:
            count = dist.get(level, 0)
            total = sum(dist.values()) or 1
            with ui.column().classes("w-full gap-1"):
                with ui.row().classes("justify-between w-full"):
                    ui.label(level.replace("_", " ").title()).classes("text-sm")
                    ui.label(f"{count}").classes("text-sm rf-muted")
                ui.linear_progress(value=count / total, show_value=False, color=color).classes(
                    "w-full"
                )

    # ---------- Top missing keywords ----------
    top_missing = data.get("top_missing_keywords", []) or []
    if top_missing:
        with ui.card().classes("rf-card w-full gap-2 mt-4"):
            ui.label("Top Missing Keywords").classes("font-semibold")
            with ui.row().classes("gap-2 flex-wrap"):
                for item in top_missing:
                    kw = item.get("keyword", "")
                    count = item.get("count", 0)
                    ui.label(f"{kw} ({count})").classes("px-2 py-1 rounded text-xs").style(
                        f"background-color: {DANGER}15; color: {DANGER};"
                    )
