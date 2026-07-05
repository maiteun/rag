from app.ai.clients.openai_client import load_experience_extraction_prompt
from app.schemas.llm import ExperienceDraft, FacetDraft, StarDraft


def test_experience_extraction_prompt_requires_contextual_role_and_evidence():
    prompt = load_experience_extraction_prompt()

    assert "Do not reduce an experience to labels" in prompt
    assert "label should be a one-line claim" in prompt
    assert "details[] should archive source-grounded supporting detail sentences" in prompt
    assert "Evidence excerpts should be short but specific" in prompt
    assert "Capability facet standard" in prompt
    assert "theme must be one of these exact values" in prompt
    assert "프로젝트 수행" in prompt
    assert "Theme mapping rules" in prompt
    assert "problem definition" in prompt
    assert "not \"문제 해결\"" in prompt
    assert "A single experience may contain facets across multiple themes" in prompt
    assert "3,001-5,000 chars: at most 10 facets" in prompt


def test_experience_output_schema_describes_cover_letter_ready_fields():
    role_description = ExperienceDraft.model_fields["role"].description
    action_description = StarDraft.model_fields["action"].description
    facets_description = ExperienceDraft.model_fields["facets"].description
    theme_description = FacetDraft.model_fields["theme"].description
    label_description = FacetDraft.model_fields["label"].description
    details_description = FacetDraft.model_fields["details"].description

    assert role_description is not None
    assert "Do not use only a label" in role_description
    assert action_description is not None
    assert "Concrete actions" in action_description
    assert facets_description is not None
    assert "Capability-level facets" in facets_description
    assert theme_description is not None
    assert "프로젝트 수행" in theme_description
    assert "A single experience may have facets across multiple themes" in theme_description
    assert "problem definition" in theme_description
    assert "not 문제 해결" in theme_description
    assert label_description is not None
    assert "One-line source-backed claim" in label_description
    assert details_description is not None
    assert "supporting detail sentences" in details_description
