from app.schemas.experience import ExperienceProcessingSummary
from app.schemas.notion import NotionWorkspaceImportRequest
from app.services.notion_client import NotionClient, NotionPageContent
from app.services.notion_import_service import NotionImportService


class FakeNotionClient:
    def __init__(self):
        self.pages = {
            "root": NotionPageContent(
                page_id="root",
                title="Career workspace",
                url="https://notion.test/root",
                text="# Career workspace\n## Backend project",
                child_page_ids=["project"],
            ),
            "project": NotionPageContent(
                page_id="project",
                title="Backend project",
                url="https://notion.test/project",
                text="# Backend project\nFastAPI and PostgreSQL project improved response time by 30%.",
                parent_page_id="root",
            ),
        }

    def iter_accessible_page_ids(self, max_pages: int):
        yield "root"

    def retrieve_page_content(self, page_id: str) -> NotionPageContent:
        return self.pages[page_id]


class FakeProcessor:
    def __init__(self):
        self.processed_document_ids: list[str] = []

    def process(self, document_id: str):
        self.processed_document_ids.append(document_id)
        return "processed", 1, 2

    def summaries_for_document(self, document_id: str):
        return [
            ExperienceProcessingSummary(
                experience_id=f"exp-{document_id}",
                title="Backend project",
                summary="FastAPI and PostgreSQL project",
                completeness_score=70,
                confidence_score=80,
            )
        ]


def test_notion_workspace_import_collects_child_pages_and_processes_documents(db_session):
    processor = FakeProcessor()
    response = NotionImportService(
        db_session,
        notion_client=FakeNotionClient(),
        processor=processor,
    ).import_workspace(
        NotionWorkspaceImportRequest(
            user_id="00000000-0000-0000-0000-000000000001",
            root_page_id="root",
        )
    )

    assert response.imported_page_count == 2
    assert response.processed_document_count == 2
    assert response.experience_count == 2
    assert response.question_count == 4
    assert {document.notion_page_id for document in response.documents} == {"root", "project"}
    assert len(processor.processed_document_ids) == 2


def test_notion_block_text_renders_common_content():
    paragraph = {
        "type": "paragraph",
        "paragraph": {"rich_text": [{"plain_text": "Implemented a recommendation API."}]},
    }
    heading = {
        "type": "heading_2",
        "heading_2": {"rich_text": [{"plain_text": "Project"}]},
    }
    todo = {
        "type": "to_do",
        "to_do": {"checked": True, "rich_text": [{"plain_text": "Measured latency"}]},
    }

    assert NotionClient._block_text(paragraph) == "Implemented a recommendation API."
    assert NotionClient._block_text(heading) == "## Project"
    assert NotionClient._block_text(todo) == "- [x] Measured latency"
