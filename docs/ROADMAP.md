# 구현 로드맵

전체 구현 순서와 단계별 완료 기준은 `docs/IMPLEMENTATION_SEQUENCE.md`를 따른다.

## M1 분석 계약 안정화
- Hana-OmniLens-API 연동 계약 고정
- 분석 API request/response 버전 관리
- 기준 모델 benchmark 평가 데이터셋 추가 완료

## M2 모델 개선
- 한국어 금융 tokenizer 추가 완료
- 이벤트 분류 모델 학습 파이프라인 확장 완료
- 감성·중요도 분류 모델 분리 완료
- 중복 제거 정밀도 개선 완료
- 사람이 검수한 OpenDART 실공시 gold label set 추가 완료
- 사람이 검수한 Naver 뉴스 도메인 gold label set 추가 완료
- 뉴스 제목체 증강 corpus 기반 재학습 완료
- 약지도 대량 후보 distillation gate 추가 완료
- 40,907건 수집 후보 기반 teacher-gated pseudo-label 이벤트 학습 완료
- 실제 뉴스 gold 56건 확장과 `CORPORATE_ACTION` pseudo-label 승격 완료

## M3 운영 하드닝
- 모델 버전별 성능 리포트 완료
- 모델 confidence calibration report 완료
- 뉴스 gold label set 종목·기간 확대 완료
- teacher-student promotion gate 품질 모니터링과 라벨별 확대 검증 완료
- 추론 latency 모니터링 완료
- audit log 완료
- 배포 환경별 secret 관리 완료

## M4 전 종목 커버리지 확장
- OpenDART 고유번호 기반 국내주식 universe 3,967개 추적 완료
- stock coverage report로 raw, training, evaluation 종목 커버리지 계측 완료
- Naver News Search 수집기를 stock universe 기반 쿼리 모드로 확장 완료
- 후보 큐와 gold가 없는 458개 누락 종목을 5개 shard로 나누는 수집 plan 완료
- shard 기반 Naver News Search 수집으로 raw 후보 68,710건, raw 매칭 3,613개 종목까지 확장 완료
- raw 후보에서 종목·라벨 균형 학습 승격 후보 큐 15,720건, 3,506개 종목 생성 완료
- 종목 후보 큐 중 teacher gate와 release gate를 통과한 781건, 781개 종목을 event-model-only pseudo-label로 제한 승격 완료
- stock candidate quota experiment로 이전 release, risk/contract 확장, calibrated current release의 gold gate 통과와 current release best profile 선정을 기록 완료
- 후보 큐에서 학습 300개 종목, 평가 100개 종목 검수 배치 생성 완료
- 검수자 메타데이터와 최종 라벨이 있는 `human_review_approved` row만 학습·평가 gold 파일로 편입하는 승격 파이프라인 완료
- 검수 배치 승인 가능 종목 수를 계측하는 validation report 완료
- 모델 제안·불확실성 기반 active review report 완료
- raw 후보는 3,613개 종목까지 매칭되지만 supervised 학습 종목은 38개, evaluation 종목은 57개라 coverage gate는 아직 fail이다.
- 다음 단계는 검수 배치를 사람이 승인해 gold/supervised 데이터에 승격하고 최소 300개 이상 종목의 supervised 학습셋과 100개 이상 종목의 evaluation gold를 확보하는 것이다.
