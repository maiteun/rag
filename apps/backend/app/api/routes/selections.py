from fastapi import APIRouter, status

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.codes import SuccessCode
from app.schemas.common import ApiResponse
from app.schemas.selection import SelectionEventCreate, SelectionEventCreateResponse
from app.services.selection_service import SelectionService

router = APIRouter()


@router.post(
    "/selections",
    response_model=ApiResponse[SelectionEventCreateResponse, None],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
    summary="선택 이벤트 기록",
    description="추천 후보 중 사용자가 고른 선택을 저장합니다. 나중에 R6(선호 학습)가 이 이벤트를 읽어 학습합니다.",
)
def create_selection(request: SelectionEventCreate, db: DbSession) -> ApiResponse[SelectionEventCreateResponse, None]:
    event = SelectionService(db).record_selection(request)
    data = SelectionEventCreateResponse(selection_id=event.id)
    return ApiResponse.created(SuccessCode.CREATED, data)
