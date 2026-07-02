from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ApiResponse, ErrorMeta


DbSession = Annotated[Session, Depends(get_db)]


ERROR_RESPONSES = {
    400: {"description": "Bad request", "model": ApiResponse[None, ErrorMeta]},
    404: {"description": "Not found", "model": ApiResponse[None, ErrorMeta]},
    500: {"description": "Internal server error", "model": ApiResponse[None, ErrorMeta]},
    502: {"description": "Upstream service error", "model": ApiResponse[None, ErrorMeta]},
}
