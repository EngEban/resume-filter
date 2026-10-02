# ============================================================
# ui/components/score_badge.py
# Colored badge showing an ATS score.
# ============================================================
from nicegui import ui

from ui.theme import LEVEL_LABELS_EN, level_color


def render_score_badge(score: float, level: str) -> None:
    """Render a colored badge with the score and level label."""
    color = level_color(level)
    label = LEVEL_LABELS_EN.get(level, level)

    with ui.row().classes("items-center gap-2"):
        ui.label(f"{score:.1f}").classes("text-2xl font-bold").style(
            f"color: {color}"
        )
        ui.label(label).classes("rf-score-badge").style(
            f"background-color: {color}"
        )