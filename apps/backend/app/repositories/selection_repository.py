from sqlalchemy.orm import Session

from app.models.selection_event import SelectionEvent


class SelectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, event: SelectionEvent) -> SelectionEvent:
        self.db.add(event)
        self.db.flush()
        return event

    def get(self, selection_id: str) -> SelectionEvent | None:
        return self.db.get(SelectionEvent, selection_id)
