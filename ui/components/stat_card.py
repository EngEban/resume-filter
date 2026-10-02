# ============================================================
# ui/components/stat_card.py
# Compact statistic card.
# ============================================================
from nicegui import ui

from ui.theme import NEUTRAL


def render_stat_card(label: str, value: str | int, color: str = NEUTRAL) -> None:
    """Render a compact statistic tile."""
    with ui.column().classes("rf-card items-start gap-1 min-w-[120px]"):
        ui.label(str(value)).classes("rf-stat").style(f"color: {color}")
        ui.label(label).classes("rf-stat-label")