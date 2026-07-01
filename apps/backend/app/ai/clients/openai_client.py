from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.ai.clients.base import ExperienceLLMClient
from app.core.config import Settings
from app.schemas.llm import ExperienceExtractionResult


class OpenAIExperienceLLMClient(ExperienceLLMClient):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=0,
        ).with_structured_output(ExperienceExtractionResult)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You convert a user's career records into a RAG-ready experience vault. "
                    "Extract resume-ready experiences without inventing facts. "
                    "Return an empty experiences array when the document has no meaningful career experience. "
                    "Use null for unclear fields, include evidence excerpts, and include missing_fields questions.",
                ),
                (
                    "human",
                    "Extract career experiences from this document.\n\nDocument:\n{cleaned_text}",
                ),
            ]
        )

    def extract_experiences(self, cleaned_text: str) -> ExperienceExtractionResult:
        response = (self.prompt | self.client).invoke({"cleaned_text": cleaned_text})
        if isinstance(response, ExperienceExtractionResult):
            return response
        return ExperienceExtractionResult.model_validate(response)
