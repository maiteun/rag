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
    summary="Import accessible Notion workspace pages into experiences",
)
def import_notion_workspace(
    request: NotionWorkspaceImportRequest,
    db: DbSession,
) -> ApiResponse[NotionWorkspaceImportResponse, None]:
    data = NotionImportService(db).import_workspace(request)
    return ApiResponse.created(SuccessCode.CREATED, data)
