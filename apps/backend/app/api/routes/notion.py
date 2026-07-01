from fastapi import APIRouter

from app.api.deps import DbSession, ERROR_RESPONSES
from app.schemas.notion import NotionWorkspaceImportRequest, NotionWorkspaceImportResponse
from app.services.notion_import_service import NotionImportService

router = APIRouter()


@router.post(
    "/notion/workspaces/import",
    response_model=NotionWorkspaceImportResponse,
    responses=ERROR_RESPONSES,
    summary="Import accessible Notion workspace pages into experiences",
)
def import_notion_workspace(
    request: NotionWorkspaceImportRequest,
    db: DbSession,
) -> NotionWorkspaceImportResponse:
    return NotionImportService(db).import_workspace(request)
