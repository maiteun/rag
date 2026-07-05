from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.ai.clients.base import ExperienceLLMClient
from app.core.config import Settings
from app.schemas.llm import ExperienceExtractionResult


EXPERIENCE_EXTRACTION_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "experience_extraction.md"


def load_experience_extraction_prompt() -> str:
    return EXPERIENCE_EXTRACTION_PROMPT_PATH.read_text(encoding="utf-8").strip()


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
                ("system", load_experience_extraction_prompt()),
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
