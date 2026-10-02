# ============================================================
# ui/theme.py
# Brand colors, CSS, and shared UI constants.
# ============================================================
from nicegui import ui

# ---------- Brand palette ----------
PRIMARY = "#2563eb"
PRIMARY_DARK = "#1e40af"
SUCCESS = "#16a34a"
WARNING = "#f59e0b"
DANGER = "#dc2626"
NEUTRAL = "#64748b"
BACKGROUND = "#f8fafc"
CARD = "#ffffff"

# ---------- ATS level colors ----------
LEVEL_COLORS: dict[str, str] = {
    "excellent": "#15803d",
    "good": "#16a34a",
    "average": "#f59e0b",
    "below_average": "#ea580c",
    "weak": "#dc2626",
}

LEVEL_LABELS_AR: dict[str, str] = {
    "excellent": "ممتاز",
    "good": "جيد",
    "average": "متوسط",
    "below_average": "دون المتوسط",
    "weak": "ضعيف",
}

LEVEL_LABELS_EN: dict[str, str] = {
    "excellent": "Excellent",
    "good": "Good",
    "average": "Average",
    "below_average": "Below Average",
    "weak": "Weak",
}

# ---------- ATS factor labels ----------
FACTOR_LABELS: dict[str, str] = {
    "keyword_match": "Keyword Match",
    "action_verbs": "Action Verbs",
    "quantified_achievements": "Quantified Achievements",
    "section_completeness": "Section Completeness",
    "contact_info": "Contact Info",
    "length_and_clarity": "Length & Clarity",
}


def apply_global_css() -> None:
    """Inject global CSS into every page."""
    ui.add_head_html(
        f"""
        <style>
            body {{
                background-color: {BACKGROUND};
                font-family: 'Inter', -apple-system, BlinkMacSystemFont,
                             'Segoe UI', Roboto, sans-serif;
            }}
            .rf-card {{
                background: {CARD};
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06),
                            0 1px 2px rgba(0,0,0,0.04);
            }}
            .rf-header {{
                background: {PRIMARY};
                color: white;
                padding: 12px 24px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .rf-score-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 9999px;
                font-weight: 600;
                color: white;
                font-size: 13px;
            }}
            .rf-muted {{ color: {NEUTRAL}; }}
            .rf-divider {{
                height: 1px;
                background: #e2e8f0;
                margin: 16px 0;
            }}
            .rf-stat {{
                font-size: 32px;
                font-weight: 700;
                line-height: 1;
            }}
            .rf-stat-label {{
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: {NEUTRAL};
                margin-top: 4px;
            }}
        </style>
        """
    )


def level_color(level: str) -> str:
    return LEVEL_COLORS.get(level, NEUTRAL)