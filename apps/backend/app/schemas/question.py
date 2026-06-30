from pydantic import BaseModel, Field


class QuestionAnswerRequest(BaseModel):
    answer: str = Field(min_length=1)


class QuestionAnswerResponse(BaseModel):
    question_id: str
    experience_id: str
    status: str
    updated_completeness_score: float

