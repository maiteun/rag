from app.schemas.llm import ExperienceDraft, ExperienceExtractionResult, FacetDraft
from app.services.experience_extraction_service import ExperienceExtractionService, max_facets_for_text_length


class _ManyFacetClient:
    def extract_experiences(self, cleaned_text: str) -> ExperienceExtractionResult:
        return ExperienceExtractionResult(
            experiences=[
                ExperienceDraft(
                    title="project",
                    facets=[
                        FacetDraft(
                            capability=f"capability-{index}",
                            label=f"label-{index}",
                            situation=None,
                            action="did work",
                            result=None,
                        )
                        for index in range(20)
                    ],
                )
            ]
        )


def test_max_facets_for_text_length():
    assert max_facets_for_text_length("a" * 500) == 3
    assert max_facets_for_text_length("a" * 1500) == 5
    assert max_facets_for_text_length("a" * 3000) == 8
    assert max_facets_for_text_length("a" * 5000) == 10
    assert max_facets_for_text_length("a" * 5001) == 15


def test_extraction_service_truncates_facets_by_source_length():
    result = ExperienceExtractionService(client=_ManyFacetClient()).extract("a" * 1200)

    assert len(result.experiences[0].facets) == 5
    assert result.experiences[0].facets[-1].capability == "capability-4"
