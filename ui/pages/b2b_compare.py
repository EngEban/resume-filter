# ============================================================
# ui/pages/b2b_compare.py
# B2B: side-by-side candidate comparison.
# ============================================================
from nicegui import app, ui

from ui.api_client import APIError
from ui.components.header import render_header
from ui.state import SessionState
from ui.theme import DANGER, PRIMARY, SUCCESS


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

    with ui.column().classes("w-full max-w-7xl mx-auto p-6 gap-4"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.row().classes("items-center gap-2"):
                ui.link(
                    "← Back to batch", f"/ui/b2b/batches/{batch_id}"
                ).classes("text-sm no-underline").style(f"color: {PRIMARY}")
                ui.label("Compare Candidates").classes("text-2xl font-bold")

            async def dl_xlsx() -> None:
                try:
                    data = await state.client.export_comparison_xlsx(batch_id)
                    ui.download(
                        data, filename=f"compare_{batch_id[:8]}.xlsx"
                    )
                except APIError as exc:
                    ui.notify(exc.message, color="negative")

            ui.button("📥 Export Excel", on_click=dl_xlsx).props(
                "outline dense color=primary"
            )

        container = ui.column().classes("w-full gap-4")

        async def load() -> None:
            container.clear()
            try:
                data = await state.client.compare_candidates(
                    batch_id, limit=10
                )
            except APIError as exc:
                with container:
                    ui.label(exc.message).style(f"color: {DANGER}")
                return

            with container:
                _render(data)

        ui.timer(0.1, load, once=True)


def _render(data: dict) -> None:
    candidates = data.get("candidates", []) or []
    if not candidates:
        ui.label("No candidates to compare.").classes("rf-muted")
        return

    with ui.row().classes("gap-4 flex-wrap"):
        for idx, c in enumerate(candidates, start=1):
            _candidate_card(idx, c)


def _candidate_card(rank: int, c: dict) -> None:
    score = c.get("ats_score") or 0
    color = (
        SUCCESS if score >= 75 else "#f59e0b" if score >= 60 else DANGER
    )

    with ui.card().classes("rf-card w-72 gap-2"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(f"#{rank}").classes("text-lg font-bold").style(
                f"color: {PRIMARY}"
            )
            ui.label(f"{score:.1f}").classes("text-2xl font-bold").style(
                f"color: {color}"
            )

        ui.label(c.get("name", "—")).classes("font-semibold")
        if c.get("email"):
            ui.label(c["email"]).classes("text-xs rf-muted")
        if c.get("phone"):
            ui.label(c["phone"]).classes("text-xs rf-muted")

        ui.separator()

        # ---------- Breakdown ----------
        breakdown = c.get("score_breakdown") or {}
        if breakdown:
            ui.label("Breakdown").classes("text-xs font-semibold")
            for factor, val in breakdown.items():
                with ui.row().classes("items-center gap-2 w-full"):
                    ui.label(
                        factor.replace("_", " ").title()
                    ).classes("text-xs flex-1")
                    ui.label(f"{float(val):.0f}").classes(
                        "text-xs rf-muted"
                    )

        # ---------- Missing ----------
        missing = c.get("missing_keywords") or []
        if missing:
            ui.label("Missing").classes("text-xs font-semibold mt-1")
            with ui.row().classes("gap-1 flex-wrap"):
                for kw in missing[:8]:
                    ui.label(kw).classes(
                        "px-1.5 py-0.5 rounded text-xs"
                    ).style(
                        f"background-color: {DANGER}15; color: {DANGER};"
                    )