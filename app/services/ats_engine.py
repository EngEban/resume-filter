# ============================================================
# app/services/ats_engine.py
# ATS Scoring Engine - 6-factor transparent scoring.
# ============================================================
from dataclasses import asdict, dataclass, field

from app.services.keyword_matcher import match_keywords

# Weights sum to 1.0
WEIGHTS = {
    "keyword_match": 0.35,
    "action_verbs": 0.15,
    "quantified_achievements": 0.15,
    "section_completeness": 0.15,
    "contact_info": 0.10,
    "length_and_clarity": 0.10,
}

# Score thresholds
LEVELS = [
    (90, "excellent", "Excellent"),
    (75, "good", "Good"),
    (60, "average", "Average"),
    (40, "below_average", "Below Average"),
    (0, "weak", "Weak"),
]


@dataclass
class ATSBreakdown:
    """Detailed per-factor scores (each 0-100)."""

    keyword_match: float = 0.0
    action_verbs: float = 0.0
    quantified_achievements: float = 0.0
    section_completeness: float = 0.0
    contact_info: float = 0.0
    length_and_clarity: float = 0.0


@dataclass
class ATSScore:
    """Final ATS score with breakdown and level."""

    total: float
    level: str
    level_label: str
    breakdown: ATSBreakdown
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["breakdown"] = asdict(self.breakdown)
        return data


def _score_section_completeness(parsed: dict) -> float:
    """Check for presence of required resume sections."""
    required = ["summary", "experience", "education", "skills"]
    found = sum(1 for section in required if parsed.get(section))
    return (found / len(required)) * 100


def _score_contact_info(parsed: dict) -> float:
    """Check for email, phone, and location."""
    required = ["email", "phone", "location"]
    found = sum(1 for field in required if parsed.get(field))
    return (found / len(required)) * 100


def _score_length_and_clarity(raw_text: str) -> float:
    """Reward resumes between 300 and 800 words."""
    word_count = len(raw_text.split())
    if 300 <= word_count <= 800:
        return 100.0
    if word_count < 300:
        return 60.0
    if word_count <= 1200:
        return 80.0
    return 60.0


def _get_level(total: float) -> tuple[str, str]:
    """Map a total score to a level identifier and label."""
    for threshold, identifier, label in LEVELS:
        if total >= threshold:
            return identifier, label
    return "weak", "Weak"


def calculate_ats_score(
    parsed_resume: dict,
    raw_text: str,
    job_description: str,
    llm_analysis: dict | None = None,
) -> ATSScore:
    """
    Compute the final ATS score.

    Args:
        parsed_resume: Structured resume data (sections, contact, etc.).
        raw_text: Full raw resume text.
        job_description: Target job description.
        llm_analysis: Optional LLM-provided scores for subjective factors.

    Returns:
        ATSScore with total, level, breakdown, and keyword info.
    """
    llm_analysis = llm_analysis or {}

    # Keyword matching
    kw_result = match_keywords(raw_text, job_description)

    # Build breakdown
    breakdown = ATSBreakdown(
        keyword_match=kw_result.match_ratio * 100,
        action_verbs=float(llm_analysis.get("action_verbs_score", 50)),
        quantified_achievements=float(llm_analysis.get("quantified_score", 50)),
        section_completeness=_score_section_completeness(parsed_resume),
        contact_info=_score_contact_info(parsed_resume),
        length_and_clarity=_score_length_and_clarity(raw_text),
    )

    # Weighted total
    total = sum(getattr(breakdown, factor) * weight for factor, weight in WEIGHTS.items())
    total = round(total, 2)
    level, label = _get_level(total)

    return ATSScore(
        total=total,
        level=level,
        level_label=label,
        breakdown=breakdown,
        matched_keywords=kw_result.matched_keywords,
        missing_keywords=kw_result.missing_keywords,
    )
