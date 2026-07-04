"""R2 검색/추천 품질 오프라인 평가 하네스.

corpus.jsonl(경험) + golden.jsonl(질의→정답경험 라벨)을 읽어, 실제 파이프라인
(R2 검색 → R3 리랭킹 → R4 컷)을 돌리고 Recall@k / Precision@k / MRR / nDCG@k 를 계산한다.

정답 라벨(golden.jsonl의 relevant/graded)은 **사람이 소유**한다 — 이게 채점 기준.
경험·질의가 늘수록 숫자가 의미 있어진다 (지금은 형식·배선 확인용).

실행 (repo 루트 기준):
    cd apps/backend
    ./.venv/bin/python eval/run_eval.py                 # .env provider(openai) 사용
    EVAL_QW=1.0 EVAL_JDW=0.5 ./.venv/bin/python eval/run_eval.py   # 가중치 튜닝

주의: openai provider면 경험 문단마다 실제 임베딩 호출(비용 발생). 검증 후 DB는 롤백.
"""

import json
import math
import os
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.services.recommendation_engine as engine_mod
from app.core.config import get_settings
from app.models.experience import Experience
from app.models.experience_chunk import ExperienceChunk
from app.models.user import User
from app.repositories.experience_repository import ExperienceRepository
from app.services.embedding_service import EmbeddingService
from app.services.recommendation_engine import RagRecommendationEngine
from app.services.retrieval_service import RetrievalService

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parents[2]  # apps/backend/eval → repo root
K_VALUES = (1, 3, 5)
USER = "eval-user"


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _paragraphs(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def _corpus_text(item: dict) -> str:
    if item.get("text"):
        return item["text"]
    return (REPO_ROOT / item["file"]).read_text(encoding="utf-8")


# ---- 지표 (정답 relevant 집합 / graded 등급 기준) ----

def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(ranked[:k]) & relevant) / len(relevant)


def precision_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    return len(set(ranked[:k]) & relevant) / k


def mrr(ranked: list[str], relevant: set[str]) -> float:
    for i, block_id in enumerate(ranked):
        if block_id in relevant:
            return 1.0 / (i + 1)
    return 0.0


def ndcg_at_k(ranked: list[str], grades: dict[str, float], k: int) -> float:
    def dcg(gains: list[float]) -> float:
        return sum(g / math.log2(i + 2) for i, g in enumerate(gains))

    actual = dcg([grades.get(bid, 0.0) for bid in ranked[:k]])
    ideal = dcg(sorted(grades.values(), reverse=True)[:k])
    return actual / ideal if ideal > 0 else 0.0


def main() -> None:
    settings = get_settings()
    # 가중치 튜닝용 오버라이드 (없으면 엔진 기본값)
    if os.environ.get("EVAL_QW"):
        engine_mod.QUESTION_WEIGHT = float(os.environ["EVAL_QW"])
    if os.environ.get("EVAL_JDW"):
        engine_mod.JD_WEIGHT = float(os.environ["EVAL_JDW"])

    corpus = _load_jsonl(EVAL_DIR / "corpus.jsonl")
    golden = _load_jsonl(EVAL_DIR / "golden.jsonl")
    print(f"provider={settings.embedding_provider} model={settings.embedding_model} "
          f"| 경험 {len(corpus)}개 · 질의 {len(golden)}개 "
          f"| weights(Q={engine_mod.QUESTION_WEIGHT}, JD={engine_mod.JD_WEIGHT})")
    if settings.embedding_provider != "openai":
        print("⚠️  fake 임베딩 — 의미 없는 결과(형식 확인용). 실측은 EMBEDDING_PROVIDER=openai.")

    emb = EmbeddingService()
    eng = create_engine(settings.database_url, future=True)
    conn = eng.connect(); trans = conn.begin()
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        session.add(User(id=USER))
        for item in corpus:
            session.add(Experience(
                id=item["id"], user_id=USER, title=item.get("title", item["id"]),
                skills=[], competencies=[], keywords=[], has_role=True, has_result=True,
                completeness_score=Decimal(0), confidence_score=Decimal(0), status="confirmed",
            ))
            for idx, para in enumerate(_paragraphs(_corpus_text(item))):
                session.add(ExperienceChunk(id=f"{item['id']}-p{idx}", user_id=USER,
                                            experience_id=item["id"], chunk_text=para,
                                            embedding=emb.embed(para)))
        session.flush()

        rec = RagRecommendationEngine(db=session, retrieval=RetrievalService(session),
                                      experiences=ExperienceRepository(session))
        rows = []
        for q in golden:
            relevant = set(q.get("relevant", []))
            grades = q.get("graded") or {bid: 1.0 for bid in relevant}
            reranked, rec_ids, _ = rec._run_pipeline(USER, q.get("job_description", ""), q.get("question", ""))
            ranked = [r.block_id for r in reranked]  # final_score 내림차순
            row = {
                "id": q["id"],
                "recall": {k: recall_at_k(ranked, relevant, k) for k in K_VALUES},
                "precision": {k: precision_at_k(ranked, relevant, k) for k in K_VALUES},
                "mrr": mrr(ranked, relevant),
                "ndcg": {k: ndcg_at_k(ranked, grades, k) for k in K_VALUES},
                "rec_precision": (len(set(rec_ids) & relevant) / len(rec_ids)) if rec_ids else 0.0,
                "ranked": ranked, "recommended": rec_ids, "relevant": sorted(relevant),
            }
            rows.append(row)

        # ---- 출력 ----
        kh = "  ".join(f"R@{k}" for k in K_VALUES)
        print("\n" + "=" * 72)
        print(f"{'query':<16}{'MRR':>6}  {kh:>18}  {'nDCG@5':>7}  {'rec_P':>6}")
        print("-" * 72)
        for r in rows:
            rec_str = "  ".join(f"{r['recall'][k]:.2f}" for k in K_VALUES)
            print(f"{r['id']:<16}{r['mrr']:>6.2f}  {rec_str:>18}  {r['ndcg'][5]:>7.2f}  {r['rec_precision']:>6.2f}")
        print("-" * 72)
        n = len(rows)
        avg = lambda f: sum(f(r) for r in rows) / n if n else 0.0  # noqa: E731
        rec_avg = "  ".join(f"{avg(lambda r: r['recall'][k]):.2f}" for k in K_VALUES)
        print(f"{'MEAN':<16}{avg(lambda r: r['mrr']):>6.2f}  {rec_avg:>18}  "
              f"{avg(lambda r: r['ndcg'][5]):>7.2f}  {avg(lambda r: r['rec_precision']):>6.2f}")
        print("=" * 72)
        print("\n질의별 순위 (정답=★):")
        for r in rows:
            order = "  ".join(("★" if b in r["relevant"] else "") + b for b in r["ranked"])
            print(f"  {r['id']:<16} {order}   | 추천(R4컷): {r['recommended']}")
    finally:
        trans.rollback(); session.close(); conn.close()
        print("\n(dev DB 롤백 완료 — 저장 안 됨)")


if __name__ == "__main__":
    main()
