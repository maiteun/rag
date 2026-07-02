from fastapi import APIRouter, status

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.codes import SuccessCode
from app.schemas.common import ApiResponse
from app.schemas.notion import NotionWorkspaceImportRequest, NotionWorkspaceImportResponse
from app.services.notion_import_service import NotionImportService

router = APIRouter()


@router.post(
    "/notion/workspaces/import",
    response_model=ApiResponse[NotionWorkspaceImportResponse, None],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
    summary="Notion 페이지 가져오기",
    description="integration token으로 접근 가능한 Notion 페이지를 문서로 저장하고, 기본값으로 경험 추출까지 실행합니다.",
)
def import_notion_workspace(
    request: NotionWorkspaceImportRequest,
    db: DbSession,
) -> ApiResponse[NotionWorkspaceImportResponse, None]:
    data = NotionImportService(db).import_workspace(request)
    return ApiResponse.created(SuccessCode.CREATED, data)
