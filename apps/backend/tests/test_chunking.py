from app.models.experience import Experience
from app.services.chunking_service import ChunkingService


def test_build_chunks_creates_summary_with_metadata():
    experience = Experience(
        id="exp-1",
        user_id="user-1",
        title="Recommendation API",
        summary="Built a recommendation API",
        skills=["FastAPI"],
        competencies=["problem solving"],
    )
    chunks = ChunkingService().build_chunks(experience, "doc-1")
    assert chunks
    assert chunks[0].experience_id == "exp-1"
    assert chunks[0].chunk_type == "experience_summary"
    assert "Recommendation API" in chunks[0].chunk_text
    assert chunks[0].chunk_metadata["skills"] == ["FastAPI"]

