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
uv run python scripts/build_weak_labeled_data.py
uv run python scripts/restore_k_fnspid_release.py
uv run python scripts/verify_k_fnspid_dataset.py
uv run python scripts/train_k_fnspid_impact_model.py
uv run python scripts/train_k_fnspid_transformer.py --seed 42
uv run python scripts/aggregate_k_fnspid_runs.py
uv run python scripts/promote_k_fnspid_transformer.py
uv run python scripts/evaluate_k_fnspid_research.py
uv run python scripts/ablate_k_fnspid_baseline.py
uv run python scripts/train_disclosure_importance_model.py
uv run python scripts/ablate_disclosure_importance.py
uv run python scripts/evaluate_disclosure_importance_research.py
uv run python scripts/train_stock_linker_model.py
uv run python scripts/train_global_peer_model.py
uv run python scripts/build_global_peer_full_coverage_report.py
uv run python scripts/train_foreign_ownership_quantity_model.py
uv run python scripts/evaluate_korean_financial_term_explainer.py
```

장시간 Transformer 학습이 중단된 경우에는 동일한 데이터·seed·학습 인자와 마지막 `checkpoint-*`를 지정한다. CLI 상대경로는 프로젝트 루트 기준으로 정규화되며 저장된 optimizer·scheduler·RNG 상태에서 재개한다.

약지도 shard는 Git에 추적된 12개 raw shard와 종목 universe에서 `build_weak_labeled_data.py`로 오프라인 재생성한다. 파생 shard는 Git 중복 저장을 피하고 manifest·release report에 재현 정책을 기록한다.

```bash
uv run python scripts/train_k_fnspid_transformer.py \
  --seed 42 \
  --resume-from-checkpoint src/hannah_montana_ai/model_store/.k_fnspid_impact_transformer-checkpoints/checkpoint-10050
```

## 현재 기준선

- 뉴스·공시 release: `financial-ml-tfidf-logreg-20260714023257`, `reports/model-release-report.json`의 `overall_status=pass`
- benchmark 768건: 이벤트 macro F1 0.9844, recall 1.0, 감성 accuracy 0.9492, v3 중요도 accuracy 0.9323 / macro F1 0.9193, 종목 accuracy 1.0
- 실제 공시 Gold 600건: 이벤트 macro F1 0.9979, recall 0.9967, 감성 accuracy 0.9233, 중요도 accuracy 1.0, 종목 accuracy 1.0
- 실제 뉴스 Gold 80건: 이벤트 macro F1 0.9184, recall 0.9875, 감성 accuracy 0.9000, 중요도 accuracy 0.9500, 종목 accuracy 1.0
- 감성 회귀 진단: 중복 제거 공개 Test 932건의 과거 KF-DeBERTa LoRA accuracy 0.8852 / macro F1 0.8849를 재현하되, 반복 조회 이력 때문에 선택·확증·SOTA gate에는 사용하지 않는다.
- 감성 Gold provenance: 새 이중 review·adjudication receipt 5개, 학습 Gold 1,794건, 개발 Gold 895건, 미해결 제외 11건, TRAIN/CHECKPOINT/CALIBRATION/SELECTION 논리 중복 0건을 검증한다.
- 감성 v6 확증: DAPT·감독학습·3-seed·공정 KR-FinBERT-SC·no-K ablation의 입력과 artifact hash를 잠그고 NEWS·DISCLOSURE 600건씩을 별도 평가했다. 결과는 `reports/korean-finance-sentiment-benchmark-v4.json`의 SHA-256 `be5c9eddc513e0f0d87df7ca05e31ef860de2e82c4954cf3d181073b94bbb149`에 고정하며 배포 판정은 `KEEP_CURRENT_MODEL`이다.
- K-FNSPID v4: 문서 1,247,685건, 문서–종목 1,136,118건, 시장영향 715,015건, 파일 기반 시세 10,691,998행
- Git 추적 raw·전문 JSONL shard: 최대 48MB, Parquet와 모든 raw/full-content/종목/시세/Gold 원천의 byte·개별/복합 SHA-256 검증, 경로 탈출·symlink·변조 fail-closed
- K-FNSPID v4 시간 Test: 뉴스 9,560건 기준선 macro F1 0.3484 / QWK 0.3421에서 전문가 0.3745 / 0.4754, 공시 4,615건 기준선 0.2677 / 0.1125에서 전문가 0.3216 / 0.1550으로 개선됐다. 통합 14,175건 거래일 cluster bootstrap 2,000회와 exact McNemar를 연구 평가 보고서에 고정한다.
- 시장영향 우월성: 행 단위 paired bootstrap과 70개 거래일 cluster bootstrap을 각각 2,000회 계산하고, 보수적인 거래일 cluster macro F1 차이 구간이 0을 넘을 때만 주장한다.
- 기본 공시 Codex Gold 600건: 모델 학습 전에 겹치는 원천 URL 401건을 제외해 post-filter 중복 0, 감성·중요도 accuracy와 macro F1 및 클래스별 지표를 함께 검증한다.
- 보조 스트레스 Gold 310건: 기본 Gold·전문 원천과 URL 중복 0, 기본 Gold와 합친 910건에서 paired bootstrap 2,000회·exact McNemar·ECE·Brier를 검증한다.
- 공시 중요도 입력 선택: 2026 Validation만 사용해 제목·제목+요약·전문 포함 뷰를 선택한다. 선택 모델 단독 기본 Gold는 accuracy 0.9850 / macro F1 0.9470, 코드북 floor 포함 910건은 0.9989 / 0.9962다.
- 글로벌 피어: KIS 활성 일반주식 2,752건 중 2,752건 성공, 구조 계약 실패 0건
- 외국인 보유 예측: 32종목 52,693개 샘플, persistence 대비 MAE 4.40% 개선, release `promoted`

도입 전 운영 수치와 비교하면 감성 accuracy는 Benchmark -0.0195, 실제 뉴스 Gold -0.0750, Stock review Gold -0.1300이며 실제 공시는 동일하다. 중요도 accuracy는 네 기존 평가셋에서 모두 동일하다. 공개 Test 개선만으로 운영 회귀를 통과 처리하지 않는다.

평가 수치는 해당 JSON report가 단일 원천이다. 수치나 dataset lineage가 바뀌면 기능별 모델 문서, [도입 전후·연구 준비도](models/k-fnspid-research-readiness.md), 구현 기록을 함께 갱신한다.
