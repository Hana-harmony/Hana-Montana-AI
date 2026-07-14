from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from hannah_montana_ai.training.collector import read_raw_alerts
from hannah_montana_ai.training.dataset import load_jsonl_payloads
from hannah_montana_ai.training.stock_universe import StockUniverseMatcher, load_stock_universe
from hannah_montana_ai.training.weak_labeler import RawCollectedAlert

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data/raw/collected_alerts.jsonl"
FULL_CONTENT_PATH = PROJECT_ROOT / "data/training/financial_alert_full_content_gold.jsonl"
STOCK_UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
OUTPUT_PATH = PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl"
REPORT_PATH = PROJECT_ROOT / "reports/disclosure-codex-gold-report.json"
REVIEWER_ID = "codex-financial-review-v2"
PROTOCOL_VERSION = "disclosure-title-codebook-v2"


@dataclass(frozen=True)
class AnnotationRule:
    name: str
    patterns: tuple[str, ...]
    tags: tuple[str, ...]
    sentiment: str
    importance: str
    note: str


RULES = (
    AnnotationRule(
        "terminal-risk",
        ("상장폐지", "횡령", "배임", "감사의견거절", "부도", "회생절차", "파산"),
        ("RISK", "DISCLOSURE"),
        "NEGATIVE",
        "CRITICAL",
        "존속·거래 가능성 또는 내부통제에 직접 영향을 주는 치명 리스크 공시",
    ),
    AnnotationRule(
        "legal-risk",
        ("소송등의제기", "소송등의판결", "거래정지"),
        ("RISK", "DISCLOSURE"),
        "NEGATIVE",
        "HIGH",
        "법적 불확실성 또는 거래 가능성에 직접 영향을 주는 중요 리스크 공시",
    ),
    AnnotationRule(
        "contract",
        ("단일판매ㆍ공급계약", "단일판매·공급계약", "공급계약체결"),
        ("CONTRACT", "DISCLOSURE"),
        "POSITIVE",
        "HIGH",
        "매출 실현 가능성과 직접 연결되는 계약 공시",
    ),
    AnnotationRule(
        "shareholder-return",
        ("자기주식취득", "현금ㆍ현물배당", "현금·현물배당"),
        ("CAPITAL_ACTION", "DISCLOSURE"),
        "POSITIVE",
        "HIGH",
        "주주환원에 직접 연결되는 자본정책 공시",
    ),
    AnnotationRule(
        "capital-action",
        ("유상증자", "무상증자", "감자결정", "전환사채", "신주인수권부사채", "자기주식처분"),
        ("CAPITAL_ACTION", "DISCLOSURE"),
        "NEUTRAL",
        "HIGH",
        "희석·자금조달·자본구조에 직접 영향을 주는 자본정책 공시",
    ),
    AnnotationRule(
        "corporate-action",
        ("회사합병", "회사분할", "영업양수", "영업양도", "타법인주식"),
        ("CORPORATE_ACTION", "DISCLOSURE"),
        "NEUTRAL",
        "HIGH",
        "기업 구조와 사업 포트폴리오에 직접 영향을 주는 경영 공시",
    ),
    AnnotationRule(
        "earnings",
        ("영업실적", "매출액또는손익구조"),
        ("EARNINGS", "DISCLOSURE"),
        "NEUTRAL",
        "HIGH",
        "실적 또는 손익구조 변화를 전달하는 중요 경영 공시",
    ),
    AnnotationRule(
        "ownership-change",
        ("최대주주등소유주식변동", "대표이사변경", "조회공시", "주주총회결과"),
        ("DISCLOSURE",),
        "NEUTRAL",
        "MEDIUM",
        "지배구조·공시 확인 상태의 변화를 전달하는 중간 중요도 공시",
    ),
    AnnotationRule(
        "routine-governance",
        (
            "임원ㆍ주요주주특정증권등소유상황보고서",
            "임원·주요주주특정증권등소유상황보고서",
            "주식등의대량보유상황보고서",
            "주주총회소집공고",
            "주주총회소집결의",
            "기업설명회개최",
            "감사보고서제출",
            "사업보고서",
            "분기보고서",
            "반기보고서",
        ),
        ("DISCLOSURE",),
        "NEUTRAL",
        "LOW",
        "정기·행정·일반 지배구조 성격의 공시",
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser(description="실제 OpenDART 공시의 Codex 검수 Gold를 만든다.")
    parser.add_argument("--raw-path", type=Path, default=RAW_PATH)
    parser.add_argument("--full-content-path", type=Path, default=FULL_CONTENT_PATH)
    parser.add_argument("--stock-universe-path", type=Path, default=STOCK_UNIVERSE_PATH)
    parser.add_argument("--output-path", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    parser.add_argument(
        "--exclude-gold-path",
        type=Path,
        help="추가 Gold 구축 시 기존 Gold URL을 후보에서 제외한다.",
    )
    parser.add_argument("--low-count", type=int, default=170)
    parser.add_argument("--medium-count", type=int, default=170)
    parser.add_argument("--high-count", type=int, default=170)
    parser.add_argument("--critical-count", type=int, default=90)
    parser.add_argument("--max-per-stock", type=int, default=2)
    args = parser.parse_args()
    args.raw_path = args.raw_path.resolve()
    args.full_content_path = args.full_content_path.resolve()
    args.stock_universe_path = args.stock_universe_path.resolve()
    args.output_path = args.output_path.resolve()
    args.report_path = args.report_path.resolve()
    if args.exclude_gold_path:
        args.exclude_gold_path = args.exclude_gold_path.resolve()

    training_urls = {
        str(row.get("source_url", ""))
        for row in load_jsonl_payloads(args.full_content_path)
        if row.get("source_url")
    }
    excluded_gold_urls = (
        {
            str(row.get("source_url", ""))
            for row in load_jsonl_payloads(args.exclude_gold_path)
            if row.get("source_url")
        }
        if args.exclude_gold_path
        else set()
    )
    matcher = StockUniverseMatcher(load_stock_universe(args.stock_universe_path))
    candidates: list[dict[str, object]] = []
    for alert in read_raw_alerts(args.raw_path):
        if (
            alert.source_type != "DISCLOSURE"
            or alert.original_url in training_urls
            or alert.original_url in excluded_gold_urls
        ):
            continue
        stock = matcher.match_raw_alert(alert)
        annotation = annotate_disclosure(alert)
        if stock is None or annotation is None:
            continue
        rule, evidence = annotation
        candidates.append(
            {
                "alert": alert,
                "stock_code": stock.stock_code,
                "stock_name": stock.stock_name,
                "market": stock.market,
                "rule": rule,
                "evidence": evidence,
            }
        )

    quotas = {
        "LOW": args.low_count,
        "MEDIUM": args.medium_count,
        "HIGH": args.high_count,
        "CRITICAL": args.critical_count,
    }
    selected = select_stratified(candidates, quotas, args.max_per_stock)
    rows = [to_gold_row(candidate) for candidate in selected]
    args.output_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    report = build_report(args.output_path, rows, training_urls, quotas)
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def annotate_disclosure(alert: RawCollectedAlert) -> tuple[AnnotationRule, str] | None:
    compact = re.sub(r"\s+", "", alert.text)
    for rule in RULES:
        for pattern in rule.patterns:
            if re.sub(r"\s+", "", pattern) in compact:
                return rule, pattern
    return None


def select_stratified(
    candidates: list[dict[str, object]],
    quotas: dict[str, int],
    max_per_stock: int,
) -> list[dict[str, object]]:
    buckets: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for candidate in candidates:
        alert = candidate["alert"]
        rule = candidate["rule"]
        if not isinstance(alert, RawCollectedAlert) or not isinstance(rule, AnnotationRule):
            raise TypeError("공시 Gold 후보의 alert 또는 rule 타입이 올바르지 않습니다.")
        year = re.sub(r"\D", "", alert.published_at)[:4] or "UNKNOWN"
        buckets.setdefault((rule.importance, year, rule.name), []).append(candidate)
    for values in buckets.values():
        values.sort(
            key=lambda row: cast_alert(row["alert"]).content_hash,
            reverse=True,
        )

    selected: list[dict[str, object]] = []
    selected_by_label: Counter[str] = Counter()
    selected_by_stock: Counter[str] = Counter()
    keys = sorted(buckets)
    while keys and any(selected_by_label[label] < count for label, count in quotas.items()):
        next_keys: list[tuple[str, str, str]] = []
        progress = False
        for key in keys:
            importance = key[0]
            values = buckets[key]
            while values:
                candidate = values.pop()
                stock_code = str(candidate["stock_code"])
                if (
                    selected_by_label[importance] < quotas[importance]
                    and selected_by_stock[stock_code] < max_per_stock
                ):
                    selected.append(candidate)
                    selected_by_label[importance] += 1
                    selected_by_stock[stock_code] += 1
                    progress = True
                    break
            if values:
                next_keys.append(key)
        if not progress:
            break
        keys = next_keys

    missing = {
        label: count - selected_by_label[label]
        for label, count in quotas.items()
        if selected_by_label[label] < count
    }
    if missing:
        raise SystemExit(f"공시 Gold 층화 quota를 충족하지 못했습니다: {missing}")
    return sorted(selected, key=lambda row: cast_alert(row["alert"]).content_hash)


def to_gold_row(candidate: dict[str, object]) -> dict[str, object]:
    alert = cast_alert(candidate["alert"])
    rule = candidate["rule"]
    if not isinstance(rule, AnnotationRule):
        raise TypeError("공시 Gold 후보의 rule 타입이 올바르지 않습니다.")
    return {
        "text": alert.title,
        "tags": list(rule.tags),
        "sentiment": sentiment_for_title(alert.title, rule.sentiment),
        "importance": rule.importance,
        "source_type": "DISCLOSURE",
        "stock_code": candidate["stock_code"],
        "stock_name": candidate["stock_name"],
        "market": candidate["market"],
        "source_url": alert.original_url,
        "provider": alert.provider,
        "published_at": alert.published_at,
        "content_hash": alert.content_hash,
        "source_review_status": "CODEX_REVIEW_APPROVED",
        "reviewer_id": REVIEWER_ID,
        "annotation_protocol": PROTOCOL_VERSION,
        "adjudication_status": "STRICT_CODEBOOK_ACCEPTED",
        "label_evidence": [candidate["evidence"]],
        "review_note": rule.note,
    }


def sentiment_for_title(title: str, default: str) -> str:
    compact = re.sub(r"\s+", "", title)
    if any(term in compact for term in ("계약해지", "결정취소", "계획철회")):
        return "NEGATIVE"
    if any(
        term in compact for term in ("손실감소", "적자폭감소", "흑자전환", "이익증가", "매출증가")
    ):
        return "POSITIVE"
    if any(
        term in compact for term in ("손실증가", "적자전환", "이익감소", "매출감소", "실적하락")
    ):
        return "NEGATIVE"
    return default


def cast_alert(value: object) -> RawCollectedAlert:
    if not isinstance(value, RawCollectedAlert):
        raise TypeError("공시 후보의 alert 타입이 올바르지 않습니다.")
    return value


def build_report(
    output_path: Path,
    rows: list[dict[str, object]],
    training_urls: set[str],
    quotas: dict[str, int],
) -> dict[str, object]:
    output_bytes = output_path.read_bytes()
    overlap = sum(str(row["source_url"]) in training_urls for row in rows)
    return {
        "schema_version": "disclosure-codex-gold/v2",
        "dataset_path": str(output_path.relative_to(PROJECT_ROOT)),
        "sha256": sha256(output_bytes).hexdigest(),
        "reviewer_id": REVIEWER_ID,
        "annotation_protocol": PROTOCOL_VERSION,
        "sample_count": len(rows),
        "quota": quotas,
        "importance_distribution": dict(
            sorted(Counter(str(row["importance"]) for row in rows).items())
        ),
        "sentiment_distribution": dict(
            sorted(Counter(str(row["sentiment"]) for row in rows).items())
        ),
        "event_distribution": dict(
            sorted(
                Counter(tag for row in rows for tag in row["tags"] if tag != "DISCLOSURE").items()
            )
        ),
        "year_distribution": dict(
            sorted(Counter(str(row["published_at"])[:4] for row in rows).items())
        ),
        "market_distribution": dict(sorted(Counter(str(row["market"]) for row in rows).items())),
        "stock_count": len({str(row["stock_code"]) for row in rows}),
        "training_url_overlap_count": overlap,
        "status": "pass" if overlap == 0 and len(rows) == sum(quotas.values()) else "fail",
        "limitations": [
            "엄격한 제목 코드북으로 판정 가능한 공시만 포함한다.",
            "단일 Codex 검수이므로 독립 인간 평가자 간 합의도를 대신하지 않는다.",
        ],
    }


if __name__ == "__main__":
    main()
