"""R6 선호 신호 학습.

R5가 저장한 selection_events를 읽어 `(user, question_type, block_id)` 단위로
"이 문항유형에서 이 경험을 얼마나 선호하는지"를 계산한다. 이 값이 R3 리랭킹의
preference 신호(w4)로 들어가면서 추천→선택→학습→다음 추천 루프가 닫힌다.

선호 = shrinkage 적용 선택률을 중립(0.5) 기준으로 재센터링한 값 (범위 [-0.5, +0.5]).
- 자주 선택 → 양수(부스트), 자주 비선택 → 음수(페널티)
- 데이터 적으면 중립으로 당기고(shrinkage), 최소 관측 미만이면 학습 안 함(cold start guard).
- CLAUDE.md 하드룰 6: 한두 번 선택으로 쏠리지 않게 보수적으로.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.selection_event import SelectionEvent

# 조정용 상수
ALPHA = 5.0  # shrinkage 강도 — 클수록 중립(0.5)으로 강하게 당김
MIN_OBSERVATIONS = 3  # 이 미만 노출이면 학습 안 함 (cold start guard)
W4_DEFAULT = 0.15  # R3 preference 가중치 — 작게 시작 (relevance/trust 보조)


def _shrunk_preference(exposures: int, selections: int) -> float:
    if exposures < MIN_OBSERVATIONS:
        return 0.0  # 근거 부족 → 중립(영향 없음)
    raw = (selections + ALPHA * 0.5) / (exposures + ALPHA)  # shrinkage 선택률
    return raw - 0.5  # 0.5 기준 재센터링 → [-0.5, +0.5]


def compute_preferences_batch(
    db: Session,
    user_id: str,
    question_type: str | None,
    block_ids: list[str],
) -> dict[str, float]:
    """후보 여러 개를 한 번에. (user, question_type) 이벤트를 한 번 읽어 메모리에서 집계."""
    preferences = {block_id: 0.0 for block_id in block_ids}
    if question_type is None or not block_ids:
        return preferences  # 학습 근거 없음

    wanted = set(block_ids)
    exposures = {block_id: 0 for block_id in block_ids}
    selections = {block_id: 0 for block_id in block_ids}

    stmt = select(SelectionEvent).where(
        SelectionEvent.user_id == user_id,
        SelectionEvent.question_type == question_type,
    )
    for event in db.scalars(stmt):
        for block_id in event.exposed_block_ids or []:
            if block_id in wanted:
                exposures[block_id] += 1
        selected = event.selected_block_id
        if selected in wanted:
            selections[selected] += 1

    for block_id in block_ids:
        preferences[block_id] = _shrunk_preference(exposures[block_id], selections[block_id])
    return preferences


def compute_preference(
    db: Session,
    user_id: str,
    question_type: str | None,
    block_id: str,
) -> float:
    """단일 후보 선호 점수 (batch의 얇은 래퍼 — 둘의 결과는 항상 동일)."""
    return compute_preferences_batch(db, user_id, question_type, [block_id])[block_id]
