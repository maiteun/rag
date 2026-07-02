from fastapi import APIRouter

from app.schemas.common import MessageResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=MessageResponse, summary="서버 상태 확인")
def health() -> MessageResponse:
    return MessageResponse(message="ok")

