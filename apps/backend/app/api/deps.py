from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db


DbSession = Annotated[Session, Depends(get_db)]


ERROR_RESPONSES = {
    400: {"description": "Bad request"},
    404: {"description": "Not found"},
    422: {"description": "Validation error"},
    500: {"description": "Internal server error"},
}

