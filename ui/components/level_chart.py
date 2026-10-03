# ============================================================
# ui/components/level_chart.py
# Horizontal bar chart of ATS factor scores.
# ============================================================
from nicegui import ui

from ui.theme import FACTOR_LABELS, PRIMARY


def render_level_chart(breakdown: dict) -> None:
    """
    Render the ATS breakdown as horizontal progress bars.

    breakdown is a dict: {factor_name: score_0_to_100}
    """
    with ui.column().classes("w-full gap-3"):
        for factor, score in breakdown.items():
            if factor not in FACTOR_LABELS:
                continue
            _factor_row(FACTOR_LABELS[factor], float(score))


def _factor_row(label: str, score: float) -> None:
    with ui.column().classes("w-full gap-1"):
        with ui.row().classes("w-full justify-between items-center"):
            ui.label(label).classes("text-sm font-medium")
            ui.label(f"{score:.0f}/100").classes("text-sm rf-muted")

        ui.linear_progress(
            value=score / 100.0,
            show_value=False,
            color=PRIMARY,
        ).classes("w-full")
