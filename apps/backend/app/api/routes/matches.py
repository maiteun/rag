from fastapi import APIRouter, status

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.codes import SuccessCode
from app.schemas.common import ApiResponse
from app.schemas.match import MatchCreateRequest, MatchCreateResponse, MatchDetailResponse
from app.services.match_service import MatchService

router = APIRouter()


@router.post(
    "/matches",
    response_model=ApiResponse[MatchCreateResponse, None],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
    summary="문항-경험 매칭 요청 생성",
    description="JD와 문항 목록으로 매칭 요청을 만들고 문항별 경험 추천을 실행합니다. 결과는 조회 API를 폴링해서 확인합니다.",
)
def create_match(request: MatchCreateRequest, db: DbSession) -> ApiResponse[MatchCreateResponse, None]:
    match_request = MatchService(db).create(request)
    data = MatchCreateResponse(match_id=match_request.id, status=match_request.status)
    return ApiResponse.created(SuccessCode.CREATED, data)


@router.get(
    "/matches/{match_id}",
    response_model=ApiResponse[MatchDetailResponse, None],
    response_model_exclude_none=True,
    responses=ERROR_RESPONSES,
    summary="매칭 결과 조회 (폴링)",
    description="매칭 상태와 문항별 추천 경험을 돌려줍니다. status가 completed가 되면 recommendations가 채워집니다.",
)
def get_match(match_id: str, db: DbSession) -> ApiResponse[MatchDetailResponse, None]:
    data = MatchService(db).get(match_id)
    return ApiResponse.ok(SuccessCode.OK, data)
