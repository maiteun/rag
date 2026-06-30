import re

from app.schemas.llm import ExperienceDraft


METRIC_PATTERN = re.compile(r"(\d+|%|명|건|초|분|배|회|원|만원|시간)")


def contains_metric(text: str | None) -> bool:
    return bool(text and METRIC_PATTERN.search(text))


def calculate_completeness(exp: ExperienceDraft) -> float:
    score = 0
    if exp.star.situation:
        score += 15
    if exp.star.task:
        score += 10
    if exp.star.action:
        score += 25
    if exp.star.result:
        score += 20
    if exp.role:
        score += 15
    if contains_metric(exp.star.result or ""):
        score += 10
    if exp.star.learned:
        score += 5
    return float(min(score, 100))


def status_for_score(score: float) -> str:
    if score >= 80:
        return "confirmed"
    if score >= 50:
        return "needs_review"
    return "draft"

