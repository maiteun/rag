"""convert experience_chunks.embedding json -> pgvector vector(1536) + hnsw index

Revision ID: 0004_pgvector_embedding
Revises: 0003_add_selection_events
Create Date: 2026-07-05

데이터 보존 경로 (원자적, 트랜잭션 내):
  1. 새 컬럼 embedding_vec vector(1536) 추가 (전부 NULL로 시작)
  2. 백필: JSON array 인 행만 vector로 캐스팅 (json::text::vector). JSON `null`/비-array 행은
     건드리지 않아 NULL로 남음 → "임베딩 없음"을 그대로 보존.
  3. 기존 json 컬럼 drop → embedding_vec 를 embedding 으로 rename
  4. hnsw 코사인 인덱스 생성
downgrade는 역방향으로 데이터 보존 (vector -> json).
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0004_pgvector_embedding"
down_revision: str | None = "0003_add_selection_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 1) 새 vector 컬럼 (NULL 시작)
    op.execute("ALTER TABLE experience_chunks ADD COLUMN embedding_vec vector(1536)")

    # 2) 백필 — JSON array 인 행만 캐스팅. json `null`/비-array 행은 제외되어 NULL 유지.
    #    (json_array_length 를 WHERE 에 쓰지 않음 → null 행에서 에러 안 남.
    #     차원은 vector(1536) 캐스팅이 강제 — 1536 아니면 마이그레이션이 안전하게 중단됨)
    op.execute(
        """
        UPDATE experience_chunks
        SET embedding_vec = embedding::text::vector(1536)
        WHERE json_typeof(embedding) = 'array'
        """
    )

    # 3) 기존 json 컬럼 제거 → 새 컬럼을 embedding 으로 rename
    op.execute("ALTER TABLE experience_chunks DROP COLUMN embedding")
    op.execute("ALTER TABLE experience_chunks RENAME COLUMN embedding_vec TO embedding")

    # 4) hnsw 코사인 인덱스 (pgvector 0.8.4)
    op.execute(
        "CREATE INDEX ix_experience_chunks_embedding_hnsw "
        "ON experience_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_experience_chunks_embedding_hnsw")

    # vector -> json 되돌리기 (데이터 보존)
    op.execute("ALTER TABLE experience_chunks ADD COLUMN embedding_json json")
    # vector 의 텍스트 표현('[...]')은 유효한 JSON 배열 → json 으로 캐스팅.
    op.execute(
        """
        UPDATE experience_chunks
        SET embedding_json = embedding::text::json
        WHERE embedding IS NOT NULL
        """
    )
    op.execute("ALTER TABLE experience_chunks DROP COLUMN embedding")
    op.execute("ALTER TABLE experience_chunks RENAME COLUMN embedding_json TO embedding")
