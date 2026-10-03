# ============================================================
# app/services/pdf_export.py
# Generate PDF reports for batches and single resumes.
# ============================================================
import io
from datetime import UTC, datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------- Palette ----------
PRIMARY = colors.HexColor("#2563EB")
NEUTRAL = colors.HexColor("#64748B")
LIGHT_BG = colors.HexColor("#F1F5F9")
DANGER = colors.HexColor("#DC2626")
SUCCESS = colors.HexColor("#16A34A")

LEVEL_COLORS = {
    "excellent": colors.HexColor("#15803D"),
    "good": colors.HexColor("#16A34A"),
    "average": colors.HexColor("#F59E0B"),
    "below_average": colors.HexColor("#EA580C"),
    "weak": colors.HexColor("#DC2626"),
}

LEVEL_LABELS = {
    "excellent": "Excellent",
    "good": "Good",
    "average": "Average",
    "below_average": "Below Average",
    "weak": "Weak",
}


def _level_from_score(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 60:
        return "average"
    if score >= 40:
        return "below_average"
    return "weak"


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleX",
            parent=base["Title"],
            fontSize=20,
            textColor=PRIMARY,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "H2X",
            parent=base["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "BodyX",
            parent=base["BodyText"],
            fontSize=10,
            leading=14,
        ),
        "muted": ParagraphStyle(
            "MutedX",
            parent=base["BodyText"],
            fontSize=9,
            textColor=NEUTRAL,
        ),
    }


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
    )


# ============================================================
# Batch PDF
# ============================================================
def build_batch_pdf(batch: dict, resumes: list[dict]) -> bytes:
    """Generate a PDF report for a batch, sorted by score."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Batch Report - {batch.get('job_title', '')}",
    )
    s = _styles()
    story: list[Any] = []

    # ---------- Title ----------
    story.append(Paragraph(batch.get("job_title", "Untitled"), s["title"]))
    story.append(
        Paragraph(
            f"Batch ID: {batch.get('id', '—')} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"Status: {batch.get('status', '—')} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"Exported: {datetime.now(UTC):%Y-%m-%d %H:%M UTC}",
            s["muted"],
        )
    )
    story.append(Spacer(1, 0.3 * cm))

    # ---------- Summary stats ----------
    total = batch.get("total_resumes", 0)
    completed = batch.get("completed", 0)
    failed = batch.get("failed", 0)
    story.append(
        Paragraph(
            f"Total: <b>{total}</b> &nbsp;&nbsp; "
            f"Completed: <b>{completed}</b> &nbsp;&nbsp; "
            f"Failed: <b>{failed}</b>",
            s["body"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    # ---------- Candidates table ----------
    story.append(Paragraph("Ranked Candidates", s["h2"]))
    story.append(Spacer(1, 0.2 * cm))

    data = [["#", "Name", "Email", "Score", "Level", "Status"]]
    sorted_resumes = sorted(
        resumes,
        key=lambda r: (r.get("ats_score") is None, -(r.get("ats_score") or 0)),
    )
    for rank, r in enumerate(sorted_resumes, start=1):
        score = r.get("ats_score")
        level = _level_from_score(float(score)) if score is not None else "weak"
        data.append(
            [
                str(rank),
                (r.get("candidate_name") or "—")[:28],
                (r.get("candidate_email") or "—")[:32],
                f"{score:.1f}" if score is not None else "—",
                LEVEL_LABELS[level] if score is not None else "—",
                r.get("status") or "—",
            ]
        )

    table = Table(
        data,
        colWidths=[1.0 * cm, 4.5 * cm, 6.0 * cm, 1.8 * cm, 2.5 * cm, 2.0 * cm],
        repeatRows=1,
    )
    table.setStyle(_table_style())
    story.append(table)

    # ---------- Top 3 details ----------
    top = sorted_resumes[:3]
    if top:
        story.append(PageBreak())
        story.append(Paragraph("Top Candidates", s["h2"]))
        for r in top:
            story.extend(_render_candidate_block(r, s))

    doc.build(story)
    return buf.getvalue()


def _render_candidate_block(r: dict, s: dict[str, ParagraphStyle]) -> list[Any]:
    """Render a compact block for one candidate."""
    score = r.get("ats_score")
    level = _level_from_score(float(score)) if score is not None else "weak"
    color = LEVEL_COLORS[level]

    block: list[Any] = []
    block.append(
        Paragraph(
            f"<b>{r.get('candidate_name') or 'Unknown'}</b> "
            f'<font color="{color.hexval()}">'
            f"({score:.1f} — {LEVEL_LABELS[level]})</font>"
            if score is not None
            else f"<b>{r.get('candidate_name') or 'Unknown'}</b>",
            s["body"],
        )
    )
    if r.get("candidate_email"):
        block.append(Paragraph(f"Email: {r['candidate_email']}", s["muted"]))

    missing = r.get("missing_keywords") or []
    if missing:
        block.append(
            Paragraph(
                f"Missing: {', '.join(str(k) for k in missing[:15])}",
                s["muted"],
            )
        )

    block.append(Spacer(1, 0.4 * cm))
    return block


# ============================================================
# Single-resume PDF
# ============================================================
def build_resume_pdf(report: dict) -> bytes:
    """Generate a single-candidate PDF report."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Resume Report - {report.get('candidate_name', '')}",
    )
    s = _styles()
    story: list[Any] = []

    score = report.get("ats_score")
    level = _level_from_score(float(score)) if score is not None else "weak"
    color = LEVEL_COLORS[level]

    # ---------- Header ----------
    story.append(
        Paragraph(report.get("candidate_name") or "Unknown Candidate", s["title"])
    )
    story.append(
        Paragraph(
            f'<font color="{color.hexval()}"><b>'
            f"{score:.1f} — {LEVEL_LABELS[level]}</b></font>"
            if score is not None
            else "No score available.",
            s["body"],
        )
    )
    if report.get("candidate_email"):
        story.append(Paragraph(f"Email: {report['candidate_email']}", s["muted"]))
    if report.get("candidate_phone"):
        story.append(Paragraph(f"Phone: {report['candidate_phone']}", s["muted"]))
    story.append(Spacer(1, 0.5 * cm))

    # ---------- Breakdown ----------
    breakdown = report.get("score_breakdown") or {}
    if breakdown:
        story.append(Paragraph("Score Breakdown", s["h2"]))
        rows = [["Factor", "Score"]]
        for key, value in breakdown.items():
            rows.append([key.replace("_", " ").title(), f"{float(value):.1f}"])
        table = Table(rows, colWidths=[10.0 * cm, 3.0 * cm], repeatRows=1)
        table.setStyle(_table_style())
        story.append(table)
        story.append(Spacer(1, 0.5 * cm))

    # ---------- Missing keywords ----------
    missing = report.get("missing_keywords") or []
    if missing:
        story.append(Paragraph("Missing Keywords", s["h2"]))
        story.append(
            Paragraph(", ".join(str(k) for k in missing[:60]), s["body"])
        )
        story.append(Spacer(1, 0.5 * cm))

    # ---------- Suggestions ----------
    suggestions = report.get("suggestions") or []
    if suggestions:
        story.append(Paragraph("Suggestions", s["h2"]))
        for sug in suggestions:
            priority = sug.get("priority", "medium")
            p_color = {
                "high": DANGER,
                "medium": colors.HexColor("#F59E0B"),
                "low": SUCCESS,
            }.get(priority, NEUTRAL)
            story.append(
                Paragraph(
                    f'<font color="{p_color.hexval()}"><b>'
                    f"{priority.upper()}</b></font> — "
                    f"{sug.get('description', '')}",
                    s["body"],
                )
            )
            story.append(Spacer(1, 0.15 * cm))

    doc.build(story)
    return buf.getvalue()
