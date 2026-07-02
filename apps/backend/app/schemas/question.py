from pydantic import BaseModel, Field


class QuestionAnswerRequest(BaseModel):
    answer: str = Field(
        min_length=1,
        description="보완 질문의 답변. 답변 내용이 경험에 반영됩니다.",
        examples=["팀원 4명과 2주간 스프린트로 진행했고, 제가 API 설계를 맡았습니다."],
    )


class QuestionAnswerResponse(BaseModel):
    question_id: str = Field(description="답변한 질문 ID")
    experience_id: str = Field(description="답변이 반영된 경험 ID")
    status: str = Field(description="질문 상태 (answered)")
    updated_completeness_score: float = Field(description="답변 반영 후 경험 완성도 점수 (0~1)")
