# 테스트는 항상 fake provider로 고정 — 실제 OpenAI 호출 0건 (빠르고·공짜·결정적).
# .env가 openai로 돼 있어도 os.environ이 .env보다 우선순위가 높아 여기서 덮어쓴다.
# db.session 등이 import 시점에 get_settings()를 호출하므로, 어떤 app 모듈 import보다 먼저 설정해야 한다.
import os

os.environ["LLM_PROVIDER"] = "fake"
os.environ["EMBEDDING_PROVIDER"] = "fake"

from app.core.config import get_settings

get_settings.cache_clear()  # 혹시 openai로 캐시됐을 값 제거 → 다음 호출부터 fake

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base


@pytest.fixture(autouse=True)
def _force_fake_providers():
    """전 테스트에서 fake provider 보장 (설정 캐시 오염 방지용 이중 안전장치)."""
    os.environ["LLM_PROVIDER"] = "fake"
    os.environ["EMBEDDING_PROVIDER"] = "fake"
    get_settings.cache_clear()
    yield


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
