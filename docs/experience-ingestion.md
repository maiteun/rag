# Experience Ingestion Pipeline

This document summarizes how KHU:DArchive imports user records and turns them into structured experiences.

## Supported Input Channels

All input channels eventually store a `source_documents` row and run the same `DocumentProcessingService` pipeline.

| Channel | API | Behavior |
| --- | --- | --- |
| Text | `POST /api/documents/text` then `POST /api/documents/{document_id}/process` | Stores raw text, then processes it into experiences. |
| PDF | `POST /api/documents/pdf` | Uploads a PDF, extracts text with `pypdf`, stores it, and processes it by default. |
| Notion | `POST /api/notion/workspaces/import` | Imports a Notion root page and child pages, stores each page as a source document, and processes each page by default. |

## Common Processing Flow

```text
input channel
  -> source_documents
  -> TextCleaningService
  -> ExperienceExtractionService
  -> drop empty/title-only experience drafts
  -> experiences
  -> experience_sources
  -> experience_chunks
  -> EmbeddingService
  -> experience_questions
```

`DocumentProcessingService` is the shared entry point for text, PDF, and Notion records.

## Notion Demo Flow

For the current demo, users do not use OAuth. They provide a Notion internal integration token and a page URL.

Recommended user flow:

1. Create a Notion internal integration from Notion Developers.
2. Copy the integration token, usually starting with `secret_`.
3. Open the Notion page to import.
4. Use `Add connections` on that page and select the integration from step 1.
5. In the frontend, paste:
   - Notion API token
   - Notion page URL
6. The backend parses the page ID from the URL and imports the root page plus child pages.

The backend currently supports `root_page_id`. The frontend-friendly next step is to also support `root_page_url`.

Recommended request shape:

```json
{
  "user_id": "user-1",
  "notion_token": "secret_xxx",
  "root_page_url": "https://www.notion.so/.../Notion-3907736fa64880df9e2ee9302f483c27",
  "process_documents": true,
  "max_pages": 50
}
```

Backend resolution should use this priority:

1. Use `root_page_id` when provided.
2. Else parse page ID from `root_page_url`.
3. Else search all pages accessible to the integration.

## Notion Page ID Parsing

Users should not manually enter page IDs. The frontend can send the full URL and the backend should extract the 32-character page ID.

Supported examples:

```text
https://www.notion.so/workspace/My-Page-3907736fa64880df9e2ee9302f483c27
https://www.notion.so/3907736fa64880df9e2ee9302f483c27
https://app.notion.com/p/Notion-3907736fa64880df9e2ee9302f483c27
```

Parsed page ID:

```text
3907736fa64880df9e2ee9302f483c27
```

## Empty Experience Filtering

Notion root pages often contain child page links such as `## 경험1` and `## 경험2`. LLMs may interpret those link titles as experiences.

Before saving an `ExperienceDraft`, the backend drops title-only drafts. A draft is saved only when at least one meaningful signal exists:

- `summary`
- `organization`
- `role`
- STAR fields: `situation`, `task`, `action`, `result`, `learned`
- evidence excerpt
- classification fields such as `experience_type`, `skills`, `competencies`, or `keywords`

This keeps root pages eligible for extraction when they contain real experience content, while dropping child-link-only false positives.

## Storage

PostgreSQL data is persisted locally through Docker Compose:

```yaml
- ./infra/postgres/data:/var/lib/postgresql/data
```

The data directory is ignored by git:

```gitignore
infra/postgres/data/*
```

Main tables:

| Table | Purpose |
| --- | --- |
| `source_documents` | Original imported text, PDF text, or Notion page text. |
| `experiences` | Structured experience cards extracted by the LLM. |
| `experience_sources` | Evidence link between an experience and its source document. |
| `experience_chunks` | RAG chunks derived from each experience. |
| `experience_questions` | Follow-up questions for missing information. |

## Frontend Notes

For the demo UI, prefer this form:

```text
Notion API token
Notion page URL
Max pages
Import button
```

Show these response values after import:

- imported page count
- processed document count
- experience count
- generated question count
- extracted experience titles

If Notion import fails with an authorization or not found error, show:

```text
Cannot read this Notion page. Check that the page is shared with your Notion integration through Add connections.
```

## Production Note

The demo flow uses user-provided internal integration tokens. A production multi-user service should replace this with Notion OAuth and store per-user access tokens securely.
