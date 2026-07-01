from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, experiences, health, notion, questions, retrieval
from app.core.errors import AppError, app_error_handler, unhandled_error_handler


def create_app() -> FastAPI:
    app = FastAPI(
        title="KHU:DArchive API",
        version="0.1.0",
        description="APIs for storing past career records as a RAG-ready archive.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    app.include_router(health.router)
    app.include_router(documents.router, prefix="/api", tags=["documents"])
    app.include_router(notion.router, prefix="/api", tags=["notion"])
    app.include_router(experiences.router, prefix="/api", tags=["experiences"])
    app.include_router(questions.router, prefix="/api", tags=["questions"])
    app.include_router(retrieval.router, prefix="/api", tags=["retrieval"])
    return app


app = create_app()
