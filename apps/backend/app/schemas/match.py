from datetime import datetime

from pydantic import BaseModel, Field


class MatchCreateRequest(BaseModel):
    user_id: str = Field(
        description="사용자 ID (UUID). 이 사용자의 경험을 대상으로 추천합니다.",
        examples=["00000000-0000-0000-0000-000000000001"],
    )
    job_description: str = Field(
        min_length=1,
        description="채용 공고(JD) 원문",
        examples=["FastAPI 기반 서비스 개발, PostgreSQL 성능 최적화 경험 우대"],
    )
    questions: list[str] = Field(
        min_length=1,
        description="자기소개서 문항 목록. 입력한 순서가 유지됩니다.",
        examples=[["문제 해결 경험을 서술하시오.", "협업 경험을 서술하시오."]],
    )


class MatchCreateResponse(BaseModel):
    match_id: str = Field(description="생성된 매칭 요청 ID. 이 ID로 결과를 폴링합니다.")
    status: str = Field(description="매칭 상태 (pending, processing, completed, failed)")


class MatchRecommendation(BaseModel):
    experience_id: str = Field(description="추천된 경험 ID")
    rank: int = Field(description="추천 순위 (1부터 시작)", examples=[1])
    score: float = Field(description="추천 점수 (0~1)", examples=[0.87])
    reason: str | None = Field(
        default=None,
        description="이 경험을 추천한 이유",
        examples=["문제와 해결 과정이 명확함"],
    )


class MatchQuestionResult(BaseModel):
    id: str = Field(description="문항 ID")
    text: str = Field(description="문항 내용", examples=["문제 해결 경험을 서술하시오."])
    recommendations: list[MatchRecommendation] = Field(
        default_factory=list, description="이 문항에 추천된 경험 목록. 순위 순으로 정렬됩니다."
    )


class MatchDetailResponse(BaseModel):
    id: str = Field(description="매칭 요청 ID")
    status: str = Field(description="매칭 상태. completed가 되면 recommendations가 채워집니다.")
    job_description: str = Field(description="요청 당시 입력한 JD 원문")
    questions: list[MatchQuestionResult] = Field(description="문항별 추천 결과")
    created_at: datetime = Field(description="요청 생성 시각")
