# ============================================================
# tests/test_keyword_matcher.py
# Unit tests for the keyword matcher.
# ============================================================
from app.services.keyword_matcher import (
    extract_keywords,
    match_keywords,
    normalize,
    tokenize,
)


class TestNormalize:
    def test_lowercases(self):
        assert normalize("Hello WORLD") == "hello world"

    def test_collapses_whitespace(self):
        assert normalize("hello    world\n\nfoo") == "hello world foo"

    def test_strips(self):
        assert normalize("  spaced  ") == "spaced"


class TestTokenize:
    def test_splits_on_punctuation(self):
        tokens = tokenize("Python, FastAPI, and Docker.")
        assert "python" in tokens
        assert "fastapi" in tokens
        assert "docker" in tokens

    def test_supports_arabic(self):
        tokens = tokenize("مهندس برمجيات في غزة")
        assert "مهندس" in tokens
        assert "غزة" in tokens

    def test_returns_lowercase(self):
        assert all(t == t.lower() for t in tokenize("HELLO World"))


class TestExtractKeywords:
    def test_removes_stopwords(self):
        keywords = extract_keywords("the quick brown fox and the dog")
        assert "the" not in keywords
        assert "and" not in keywords

    def test_removes_short_tokens(self):
        keywords = extract_keywords("a b c de fg")
        assert "a" not in keywords
        assert "b" not in keywords
        assert "de" in keywords

    def test_removes_new_stopwords(self):
        keywords = extract_keywords("we need a python developer who will do the work")
        assert "need" not in keywords
        assert "will" not in keywords
        assert "do" not in keywords
        assert "python" in keywords
        assert "developer" in keywords


class TestMatchKeywords:
    def test_perfect_match(self):
        result = match_keywords(
            "Python developer with FastAPI experience",
            "Python FastAPI developer",
        )
        assert result.match_ratio > 0.6
        assert "python" in result.matched_keywords
        assert "fastapi" in result.matched_keywords

    def test_no_match(self):
        result = match_keywords(
            "Java Spring engineer",
            "Python FastAPI developer",
        )
        assert result.match_ratio < 0.3
        assert "python" in result.missing_keywords

    def test_empty_job_description(self):
        result = match_keywords("Python developer", "")
        assert result.match_ratio == 0.0
        assert result.missing_keywords == []

    def test_partial_match(self, sample_job_description, strong_resume_text):
        result = match_keywords(strong_resume_text, sample_job_description)
        assert result.match_ratio > 0.5
        assert "python" in result.matched_keywords
        assert "fastapi" in result.matched_keywords

    def test_weak_resume_has_high_missing(self, sample_job_description, weak_resume_text):
        result = match_keywords(weak_resume_text, sample_job_description)
        assert result.match_ratio < 0.5
        assert "kubernetes" in result.missing_keywords
