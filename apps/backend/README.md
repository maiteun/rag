# Backend

FastAPI backend for the career experience vault MVP.

## Run

```bash
cd apps/backend
uvicorn app.main:app --reload
```

The app exposes:

- `GET /health`
- `POST /api/documents/text`
- `POST /api/documents/{document_id}/process`
- `GET /api/documents/{document_id}/processing-result`
- `GET /api/experiences`
- `GET /api/experiences/{experience_id}`
- `POST /api/experience-questions/{question_id}/answer`
- `POST /api/retrieval/search`

## Configuration

See the repository root `.env.example`.

