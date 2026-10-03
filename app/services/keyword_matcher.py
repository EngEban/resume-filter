# ============================================================
# app/services/keyword_matcher.py
# Keyword extraction and matching (resume <-> job description).
# ============================================================
import re
from dataclasses import dataclass

STOPWORDS: set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else",
    "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "by", "for", "with", "about",
    "from", "as", "into", "through", "during", "before", "after",
    "above", "below", "up", "down", "out", "off", "over", "under",
    "this", "that", "these", "those", "it", "its",
    "i", "you", "he", "she", "we", "they", "them", "their",
    "need", "needs", "needed", "want", "wants", "wanted",
    "must", "should", "would", "could", "can", "will",
    "have", "has", "had", "do", "does", "did",
    "also", "well", "very", "just", "only", "such",
    "في", "من", "إلى", "على", "عن", "مع", "هذا", "هذه", "ذلك",
    "التي", "الذي", "كان", "كانت", "هو", "هي", "هم", "أن", "إن",
    "لا", "ما", "لم", "لن", "قد", "كل", "بعض", "أي",
}


@dataclass
class KeywordMatchResult:
    job_keywords: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    match_ratio: float


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[\w\u0600-\u06FF]+\b", text.lower())


def extract_keywords(text: str, min_length: int = 2) -> set[str]:
    tokens = tokenize(text)
    return {
        token
        for token in tokens
        if token not in STOPWORDS and len(token) >= min_length
    }


def match_keywords(
    resume_text: str, job_description: str
) -> KeywordMatchResult:
    job_kws = extract_keywords(job_description)
    resume_kws = extract_keywords(resume_text)

    if not job_kws:
        return KeywordMatchResult(
            job_keywords=[],
            matched_keywords=[],
            missing_keywords=[],
            match_ratio=0.0,
        )

    matched = sorted(job_kws & resume_kws)
    missing = sorted(job_kws - resume_kws)
    ratio = len(matched) / len(job_kws)

    return KeywordMatchResult(
        job_keywords=sorted(job_kws),
        matched_keywords=matched,
        missing_keywords=missing,
        match_ratio=ratio,
    )
