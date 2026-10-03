# ============================================================
# tests/conftest.py
# Shared pytest fixtures.
# ============================================================

import pytest


# ------------------------------------------------------------
# Sample data
# ------------------------------------------------------------
@pytest.fixture
def sample_job_description() -> str:
    """A realistic job description for testing."""
    return (
        "We are hiring a Python Backend Developer.\n"
        "Requirements:\n"
        "- 3+ years experience with Python and FastAPI\n"
        "- Strong knowledge of PostgreSQL and Redis\n"
        "- Experience with Docker and Kubernetes\n"
        "- Familiarity with Celery for background tasks\n"
        "- Good communication skills in English and Arabic\n"
    )


@pytest.fixture
def strong_resume_text() -> str:
    """A resume that matches most requirements."""
    return (
        "Senior Python Backend Developer with 6 years of experience. "
        "Expert in FastAPI, PostgreSQL, Redis, Docker, Kubernetes, and Celery. "
        "Built scalable microservices handling 10M requests per day. "
        "Led a team of 4 engineers and improved deployment time by 60%. "
        "Fluent in English and Arabic. "
    ) * 8


@pytest.fixture
def weak_resume_text() -> str:
    """A resume that matches few requirements."""
    return (
        "Junior developer with 1 year of experience. "
        "Knows some Python. Currently learning HTML and CSS. "
        "Looking for opportunities. "
    ) * 8


@pytest.fixture
def parsed_resume_full() -> dict:
    """A fully populated parsed resume."""
    return {
        "email": "jane@example.com",
        "phone": "+970 599 123 456",
        "location": "Gaza",
        "summary": "Experienced backend engineer.",
        "experience": "6 years in Python backend development.",
        "education": "BSc in Computer Science.",
        "skills": "Python, FastAPI, PostgreSQL, Docker",
        "word_count": 500,
    }


@pytest.fixture
def llm_analysis_perfect() -> dict:
    """LLM analysis suggesting top scores."""
    return {
        "action_verbs_score": 95,
        "quantified_score": 90,
        "weak_bullets": [],
    }


@pytest.fixture
def llm_analysis_weak() -> dict:
    """LLM analysis suggesting poor scores."""
    return {
        "action_verbs_score": 20,
        "quantified_score": 10,
        "weak_bullets": [
            {"original": "Did some work", "issue": "vague", "suggestion": "Quantify"},
        ],
    }
