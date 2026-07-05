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
        facets=[
            {
                "capability": "problem solving",
                "theme": "프로젝트 수행",
                "label": "API latency issue resolved",
                "situation": "The recommendation API was slow.",
                "action": "Optimized query paths.",
                "result": "Latency improved.",
                "details": ["FastAPI", "PostgreSQL index"],
                "evidence": ["Optimized query paths."],
            }
        ],
    )
    chunks = ChunkingService().build_chunks(experience, "doc-1")
    assert chunks
    assert chunks[0].experience_id == "exp-1"
    assert chunks[0].chunk_type == "experience_summary"
    assert "Recommendation API" in chunks[0].chunk_text
    assert chunks[0].chunk_metadata["skills"] == ["FastAPI"]
    facet_chunks = [chunk for chunk in chunks if chunk.chunk_type == "facet"]
    assert len(facet_chunks) == 1
    assert "Capability: problem solving" in facet_chunks[0].chunk_text
    assert "PostgreSQL index" in facet_chunks[0].chunk_text
    assert facet_chunks[0].chunk_metadata["facet_capability"] == "problem solving"

