# ============================================================
# tests/test_ats_engine.py
# Unit tests for the ATS scoring engine.
# ============================================================
import pytest

from app.services.ats_engine import WEIGHTS, calculate_ats_score


class TestWeights:
    def test_weights_sum_to_one(self):
        assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

    def test_keyword_match_is_dominant(self):
        assert WEIGHTS["keyword_match"] == max(WEIGHTS.values())


class TestScoring:
    def test_perfect_resume_scores_high(
        self,
        strong_resume_text,
        sample_job_description,
        parsed_resume_full,
        llm_analysis_perfect,
    ):
        score = calculate_ats_score(
            parsed_resume=parsed_resume_full,
            raw_text=strong_resume_text,
            job_description=sample_job_description,
            llm_analysis=llm_analysis_perfect,
        )
        assert score.total >= 75
        assert score.level in ("good", "excellent")

    def test_weak_resume_scores_low(
        self,
        weak_resume_text,
        sample_job_description,
        llm_analysis_weak,
    ):
        parsed = {
            "email": None,
            "phone": None,
            "location": None,
            "summary": None,
            "experience": None,
            "education": None,
            "skills": None,
        }
        score = calculate_ats_score(
            parsed_resume=parsed,
            raw_text=weak_resume_text,
            job_description=sample_job_description,
            llm_analysis=llm_analysis_weak,
        )
        assert score.total < 50
        assert score.level in ("weak", "below_average")

    def test_score_is_deterministic(
        self,
        strong_resume_text,
        sample_job_description,
        parsed_resume_full,
        llm_analysis_perfect,
    ):
        a = calculate_ats_score(
            parsed_resume_full,
            strong_resume_text,
            sample_job_description,
            llm_analysis_perfect,
        )
        b = calculate_ats_score(
            parsed_resume_full,
            strong_resume_text,
            sample_job_description,
            llm_analysis_perfect,
        )
        assert a.total == b.total

    def test_score_is_bounded(self, sample_job_description):
        score = calculate_ats_score(
            parsed_resume={},
            raw_text="a" * 500,
            job_description=sample_job_description,
        )
        assert 0 <= score.total <= 100

    def test_breakdown_has_all_factors(
        self,
        strong_resume_text,
        sample_job_description,
        parsed_resume_full,
        llm_analysis_perfect,
    ):
        score = calculate_ats_score(
            parsed_resume_full,
            strong_resume_text,
            sample_job_description,
            llm_analysis_perfect,
        )
        breakdown = score.breakdown
        for factor in WEIGHTS:
            assert hasattr(breakdown, factor)
            value = getattr(breakdown, factor)
            assert 0 <= value <= 100

    def test_missing_keywords_are_reported(
        self,
        weak_resume_text,
        sample_job_description,
    ):
        score = calculate_ats_score(
            parsed_resume={},
            raw_text=weak_resume_text,
            job_description=sample_job_description,
        )
        assert len(score.missing_keywords) > 0
        assert "kubernetes" in score.missing_keywords

    def test_to_dict_is_serializable(
        self,
        strong_resume_text,
        sample_job_description,
        parsed_resume_full,
    ):
        import json

        score = calculate_ats_score(
            parsed_resume_full,
            strong_resume_text,
            sample_job_description,
        )
        data = score.to_dict()
        json.dumps(data)
        assert "total" in data
        assert "breakdown" in data


class TestLevels:
    @pytest.mark.parametrize(
        "score,expected_level",
        [
            (95, "excellent"),
            (80, "good"),
            (65, "average"),
            (50, "below_average"),
            (30, "weak"),
            (0, "weak"),
        ],
    )
    def test_level_thresholds(self, score, expected_level):
        from app.services.ats_engine import _get_level

        level, _ = _get_level(score)
        assert level == expected_level
