from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models import (  # noqa: E402,F401
    experience,
    experience_chunk,
    experience_question,
    experience_source,
    match_request,
    source_document,
    user,
)

