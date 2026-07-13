# 테스트

## 필수 검증

```bash
uv sync --all-groups
uv run ruff check .
uv run mypy
uv run bandit -c pyproject.toml -r src
uv run python scripts/verify_secret_hygiene.py
uv run pytest
```

CI는 Python 3.12와 uv를 사용한다. PR에서는 `verify_message_conventions.py`로 브랜치, 커밋, PR 제목·본문 규칙도 검사한다.

## 테스트 범위

| 영역 | 검증 내용 |
| --- | --- |
| API | health/readiness, 공통 envelope, validation, artifact 장애 시 503, OmniLens JSON 계약 |
| 뉴스·공시 | 이벤트·감성·중요도, 종목 linker, What/Why/Impact 품질, 전문·중복 키·glossary, audit 원문 비노출 |
| 번역 | Qwen3 요청, 문서 유형별 prompt, 전문 분할·완결성, dictionary 표면형, source-language fallback |
| 글로벌 피어 | 활성 종목 universe 일치, 전종목 추론, 비교 3개·강점 4개, 동적 순위, 중복·더미 방지 |
| 외국인 예측 | walk-forward 학습, persistence guard, 제한 종목 allowlist, 재학습 promotion과 원자적 artifact 교체 |
| 금융 용어 | 단일 seed loader, alias 단어 경계, evidence, cacheable/review 상태 |
| 세무 | 이미지/PDF signature, OCR·parser·reviewer, 세 문서 필수 필드, 위변조 위험, 환급 규칙 계약 |
| 보안 | 시크릿 추적 방지, credential 값 비노출, 유지보수 토큰, 원문 hash logging |

## 모델 재현 검증

필요한 모델만 해당 스크립트로 재생성한다. 생성 결과는 코드와 함께 검토하고 자동으로 운영 artifact를 덮어쓰지 않는다.

```bash
uv run python scripts/train_ml_model.py
uv run python scripts/evaluate_ml_model.py
uv run python scripts/build_model_release_report.py
uv run python scripts/train_stock_linker_model.py
uv run python scripts/train_global_peer_model.py
uv run python scripts/build_global_peer_full_coverage_report.py
uv run python scripts/train_foreign_ownership_quantity_model.py
uv run python scripts/evaluate_korean_financial_term_explainer.py
```

## 현재 기준선

- 뉴스·공시 release: `financial-ml-tfidf-logreg-20260622090407`, `reports/model-release-report.json`의 `overall_status=pass`
- benchmark 768건: 이벤트 macro F1 0.9844, recall 1.0, 감성 accuracy 0.9492, 중요도 accuracy 0.9583, 종목 accuracy 1.0
- 실제 뉴스 gold 80건: 이벤트 macro F1 0.9221, recall 0.9875, 감성 accuracy 0.9000, 중요도 accuracy 0.9625, 종목 accuracy 1.0
- 글로벌 피어: KIS 활성 일반주식 2,752건 중 2,752건 성공, 구조 계약 실패 0건
- 외국인 보유 예측: 32종목 52,693개 샘플, persistence 대비 MAE 4.40% 개선, release `promoted`

평가 수치는 해당 JSON report가 단일 원천이다. 수치나 dataset lineage가 바뀌면 기능별 모델 문서와 구현 기록을 함께 갱신한다.
