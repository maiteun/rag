from collections import deque
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.models.source_document import SourceDocument
from app.models.user import User
from app.repositories.source_document_repository import SourceDocumentRepository
from app.schemas.notion import (
    NotionImportedDocumentSummary,
    NotionWorkspaceImportRequest,
    NotionWorkspaceImportResponse,
)
from app.services.document_processing_service import DocumentProcessingService
from app.services.notion_client import NotionClient, NotionPageContent


class NotionImportService:
    def __init__(
        self,
        db: Session,
        notion_client: NotionClient | None = None,
        processor: DocumentProcessingService | None = None,
    ):
        self.db = db
        self.documents = SourceDocumentRepository(db)
        self.notion_client = notion_client
        self.processor = processor

    def import_workspace(self, request: NotionWorkspaceImportRequest) -> NotionWorkspaceImportResponse:
        client = self.notion_client or self._build_client(request.notion_token)
        self._ensure_user(request.user_id)

        pages = self._collect_pages(client, request.root_page_id, request.max_pages)
        documents: list[NotionImportedDocumentSummary] = []
        total_experiences = 0
        total_questions = 0
        processed_documents = 0

        for page in pages:
            if not page.text.strip():
                continue
            document = self._create_document(request, page)
            experience_count = 0
            question_count = 0
            experiences = []
            if request.process_documents:
                status, experience_count, question_count = self._processor().process(document.id)
                document.status = status
                experiences = self._processor().summaries_for_document(document.id)
                processed_documents += 1
            total_experiences += experience_count
            total_questions += question_count
            documents.append(
                NotionImportedDocumentSummary(
                    document_id=document.id,
                    notion_page_id=page.page_id,
                    title=document.title,
                    url=document.external_url,
                    status=document.status,
                    experience_count=experience_count,
                    question_count=question_count,
                    experiences=experiences,
                )
            )

        return NotionWorkspaceImportResponse(
            imported_page_count=len(documents),
            processed_document_count=processed_documents,
            experience_count=total_experiences,
            question_count=total_questions,
            documents=documents,
        )

    def _collect_pages(
        self,
        client: NotionClient,
        root_page_id: str | None,
        max_pages: int,
    ) -> list[NotionPageContent]:
        queue = deque([root_page_id] if root_page_id else client.iter_accessible_page_ids(max_pages))
        visited: set[str] = set()
        pages: list[NotionPageContent] = []

        while queue and len(visited) < max_pages:
            page_id = queue.popleft()
            if page_id in visited:
                continue
            visited.add(page_id)
            page = client.retrieve_page_content(page_id)
            pages.append(page)
            for child_page_id in page.child_page_ids:
                if child_page_id not in visited:
                    queue.append(child_page_id)

        return pages

    def _create_document(self, request: NotionWorkspaceImportRequest, page: NotionPageContent) -> SourceDocument:
        document = SourceDocument(
            id=str(uuid4()),
            user_id=request.user_id,
            source_type="notion",
            title=page.title,
            external_url=page.url,
            raw_text=page.text,
            status="uploaded",
            doc_metadata={
                "notion_page_id": page.page_id,
                "notion_parent_page_id": page.parent_page_id,
                "workspace_name": request.workspace_name,
            },
        )
        self.documents.create(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def _ensure_user(self, user_id: str) -> None:
        if self.db.get(User, user_id) is not None:
            return
        self.db.add(User(id=user_id))
        self.db.flush()

    def _build_client(self, token: str | None) -> NotionClient:
        settings = get_settings()
        resolved_token = token or settings.notion_api_token
        if not resolved_token:
            raise AppError(400, "missing_notion_token", "notion_token or NOTION_API_TOKEN is required.")
        return NotionClient(resolved_token, settings.notion_api_version)

    def _processor(self) -> DocumentProcessingService:
        if self.processor is None:
            self.processor = DocumentProcessingService(self.db)
        return self.processor
