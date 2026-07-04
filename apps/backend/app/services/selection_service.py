from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.codes import ErrorCode
from app.core.errors import BusinessError
from app.models.selection_event import SelectionEvent
from app.models.user import User
from app.repositories.selection_repository import SelectionRepository
from app.schemas.selection import SelectionEventCreate


class SelectionService:
    """R5 선택 이벤트 저장. R6(선호 학습)가 나중에 읽어 학습한다. 여기선 저장까지만."""

    def __init__(self, db: Session):
        self.db = db
        self.selections = SelectionRepository(db)

    def record_selection(self, request: SelectionEventCreate) -> SelectionEvent:
        # 선택은 노출된 후보 중 하나여야 함. 스킵(None)은 허용.
        if request.selected_block_id is not None and request.selected_block_id not in request.exposed_block_ids:
            raise BusinessError(ErrorCode.SELECTED_NOT_EXPOSED)

        self._ensure_user(request.user_id)
        event = SelectionEvent(
            id=str(uuid4()),
            user_id=request.user_id,
            question_type=request.question_type,
            job_description=request.job_description,
            question_text=request.question_text,
            exposed_block_ids=request.exposed_block_ids,
            selected_block_id=request.selected_block_id,
            rejected_block_ids=request.rejected_block_ids,
            signals_snapshot=request.signals_snapshot,
        )
        self.selections.create(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def _ensure_user(self, user_id: str) -> None:
        if self.db.get(User, user_id) is None:
            self.db.add(User(id=user_id))
            self.db.flush()
