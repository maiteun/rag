# 테스트는 항상 fake provider로 고정 — 실제 OpenAI 호출 0건 (빠르고·공짜·결정적).
# .env가 openai로 돼 있어도 os.environ이 .env보다 우선순위가 높아 여기서 덮어쓴다.
# db.session 등이 import 시점에 get_settings()를 호출하므로, 어떤 app 모듈 import보다 먼저 설정해야 한다.
import os

os.environ["LLM_PROVIDER"] = "fake"
os.environ["EMBEDDING_PROVIDER"] = "fake"

from app.core.config import get_settings

get_settings.cache_clear()  # 혹시 openai로 캐시됐을 값 제거 → 다음 호출부터 fake

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.db.base import Base

# 전용 테스트 DB — dev DB(experience_vault)와 완전 분리해 개발 데이터 무오염.
TEST_DB_NAME = "experience_vault_test"


@pytest.fixture(autouse=True)
def _force_fake_providers():
    """전 테스트에서 fake provider 보장 (설정 캐시 오염 방지용 이중 안전장치)."""
    os.environ["LLM_PROVIDER"] = "fake"
    os.environ["EMBEDDING_PROVIDER"] = "fake"
    get_settings.cache_clear()
    yield


@pytest.fixture(scope="session")
def _test_engine():
    """세션당 1회: 전용 테스트 DB 준비 → pgvector 확장 → 전 테이블 생성.

    실제 pgvector `vector(1536)` 경로를 그대로 검증하기 위해 sqlite 대신 Postgres 사용.
    postgres 컨테이너가 꺼져 있으면 명확한 안내와 함께 실패한다.
    """
    base_url = make_url(get_settings().database_url)
    test_url = base_url.set(database=TEST_DB_NAME)

    # 1) 테스트 DB가 없으면 생성 (유지보수 DB 'postgres'에 AUTOCOMMIT 접속)
    maint_url = base_url.set(database="postgres")
    try:
        maint_engine = create_engine(maint_url, isolation_level="AUTOCOMMIT", future=True)
        with maint_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": TEST_DB_NAME},
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
        maint_engine.dispose()
    except Exception as exc:  # noqa: BLE001
        pytest.exit(
            f"테스트용 Postgres에 접속할 수 없습니다 ({exc}).\n"
            "docker compose up -d postgres 로 컨테이너를 먼저 띄우세요.",
            returncode=1,
        )

    # 2) 테스트 DB에 pgvector 확장 + 스키마 생성 (모델 기준, embedding=vector(1536))
    engine = create_engine(test_url, future=True)
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)

    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(_test_engine):
    """테스트당 트랜잭션 → 종료 시 롤백으로 격리 (dev/테스트 DB 모두 무오염).

    서비스가 내부에서 db.commit()을 호출하므로 join_transaction_mode="create_savepoint"로
    커밋을 savepoint에 가두고, 바깥 트랜잭션을 롤백해 테스트 간 데이터가 남지 않게 한다.
    """
    connection = _test_engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
