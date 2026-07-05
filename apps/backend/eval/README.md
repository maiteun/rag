# R2 검색/추천 오프라인 평가 (eval)

RAG 검색 품질을 **눈대중이 아니라 숫자로** 재기 위한 하네스. 정답 라벨(골든셋)과
시스템 출력을 비교해 Recall@k / Precision@k / MRR / nDCG@k 를 계산한다.

> 정답 라벨은 **사람이 소유**한다. 이게 곧 채점 기준이라, 라벨이 곧 평가의 신뢰도다.
> 경험·질의 수가 적으면 숫자가 불안정하다 (경험 3개면 top-3에 다 들어가 R@3=1 자명).
> 실측 의미를 가지려면 경험 20~50개 + 질의 10~30개 규모를 권장.

## 파일

- `corpus.jsonl` — 검색 대상 경험. 한 줄에 `{"id", "title", "file"}` 또는 `{"id","title","text"}`.
  `file`은 repo 루트 기준 경로 (예: `testdata/ex1.txt`). 문단(빈 줄 제외 라인) 단위로 청킹.
- `golden.jsonl` — 평가 질의. 한 줄에:
  ```json
  {"id":"q1", "question":"자소서 문항", "job_description":"JD 본문",
   "relevant":["ex3","ex2"], "graded":{"ex3":2,"ex2":1}, "note":"메모(선택)"}
  ```
  - `relevant`: 이 질의에 나와야 하는 정답 경험 id들 (binary 관련성).
  - `graded`(선택): nDCG용 등급(높을수록 관련). 없으면 relevant를 1로 취급.

## 실행

```bash
cd apps/backend
./.venv/bin/python eval/run_eval.py
```

- `.env`의 provider를 사용한다. **실측은 `EMBEDDING_PROVIDER=openai`** (문단마다 임베딩 호출 → 비용).
  fake면 결과가 무의미(형식 확인용).
- 평가용 경험/청크는 트랜잭션 안에서만 만들고 **끝나면 롤백** — dev DB에 안 남는다.
- 테스트 인프라와 무관하게 dev DB(`experience_vault`)에 붙는다. docker Postgres 필요.

### 가중치 튜닝
문항 vs JD 결합 가중치를 바꿔가며 지표를 비교:
```bash
EVAL_QW=1.0 EVAL_JDW=0.3 ./.venv/bin/python eval/run_eval.py
```
(엔진 기본은 `QUESTION_WEIGHT=JD_WEIGHT=1.0`. 골든셋이 커지면 이걸로 최적 가중치를 정한다.)

## 지표 읽는 법
- **Recall@k** — 정답이 상위 k에 든 비율 (놓침 관리). 1차 검색 품질.
- **Precision@k / rec_P** — 뽑은 것 중 정답 비율. `rec_P`는 R4가 실제 추천한 집합의 정밀도(비추천 정확도).
- **MRR** — 첫 정답의 등수 역수 (1등=1.0). 순위를 위로 잘 올렸나.
- **nDCG@k** — 등급을 반영한 순서 품질.

## 주의
- `corpus.jsonl`이 참조하는 `testdata/`는 **개인 자소서라 gitignore**됨. 각자 로컬에 두거나,
  공유 가능한 샘플 경험으로 교체해 쓴다. `corpus.jsonl`/`golden.jsonl`은 텍스트가 아닌
  참조·라벨만 담으므로 커밋 가능(원문 미포함).
