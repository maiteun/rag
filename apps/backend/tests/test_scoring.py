from app.schemas.llm import ExperienceDraft, StarDraft
from app.utils.scoring import calculate_completeness, contains_metric


def test_calculate_completeness_full_fields():
    draft = ExperienceDraft(
        title="project",
        role="backend",
        star=StarDraft(
            situation="s",
            task="t",
            action="a",
            result="latency reduced by 30%",
            learned="l",
        ),
    )
    assert calculate_completeness(draft) == 100


def test_calculate_completeness_drops_without_result():
    draft = ExperienceDraft(title="project", role="backend", star=StarDraft(situation="s", task="t", action="a"))
    assert calculate_completeness(draft) == 65


def test_contains_metric_detects_common_metric_markers():
    assert contains_metric("응답 시간이 0.9초로 감소")
    assert contains_metric("30% improved")
    assert not contains_metric("성과를 개선했습니다")

