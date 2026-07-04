from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class SelectionEvent(TimestampMixin, Base):
    """R5 선택 이벤트. 사용자가 추천 후보 중 하나를 고른 사건을 저장한다.

    R6(선호 학습)가 나중에 이걸 읽어 학습한다. R5는 저장까지만.
    지금 안 쓰는 필드(job_description/signals_snapshot 등)도 저장은 해둔다 —
    나중에 "문항유형별 → JD별·속성 학습"으로 승급할 때 복구 불가한 맥락을 남기기 위함.
    """

    __tablename__ = "selection_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    question_type: Mapped[str | None] = mapped_column(String(50))  # R1 분류 문항유형 — R6 집계 키
    job_description: Mapped[str | None] = mapped_column(Text)  # JD 원문 — 나중에 JD별 학습용
    question_text: Mapped[str | None] = mapped_column(Text)
    exposed_block_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)  # 노출된 후보
    selected_block_id: Mapped[str | None] = mapped_column(String(36))  # 선택한 것 (스킵 시 None)
    rejected_block_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)  # soft negative
    signals_snapshot: Mapped[dict | None] = mapped_column(JSON)  # 선택 시점 후보별 신호 — 속성 학습용
