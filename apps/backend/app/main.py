from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, experiences, health, matches, notion, questions, resumes, retrieval
from app.core.errors import (
    BusinessError,
    business_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="KHU:DArchive API",
        version="0.1.0",
        description="커리어 기록을 경험 단위로 구조화해 저장하고, JD/문항에 맞는 경험을 찾아주는 KHU:DArchive 백엔드 API입니다.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(BusinessError, business_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    app.include_router(health.router)
    app.include_router(documents.router, prefix="/api", tags=["documents"])
    app.include_router(notion.router, prefix="/api", tags=["notion"])
    app.include_router(experiences.router, prefix="/api", tags=["experiences"])
    app.include_router(questions.router, prefix="/api", tags=["questions"])
    app.include_router(retrieval.router, prefix="/api", tags=["retrieval"])
    app.include_router(matches.router, prefix="/api", tags=["matches"])
    app.include_router(resumes.router, prefix="/api", tags=["resumes"])
    return app


app = create_app()
