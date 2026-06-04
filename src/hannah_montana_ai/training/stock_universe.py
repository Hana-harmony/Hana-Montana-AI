from __future__ import annotations

import csv
import io
import json
import os
import re
import zipfile
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from defusedxml import ElementTree

from hannah_montana_ai.training.dataset import LabeledAlert, load_labeled_alerts
from hannah_montana_ai.training.weak_labeler import RawCollectedAlert

STOCK_UNIVERSE_SCHEMA_VERSION = "korea-stock-universe/v1"
COVERAGE_REPORT_SCHEMA_VERSION = "stock-coverage-report/v1"
DEFAULT_NEWS_INTENTS = ("실적", "공시", "수주", "유상증자", "거래정지")
_NORMALIZE_PATTERN = re.compile(r"[^0-9a-z가-힣]+")


@dataclass(frozen=True)
class StockUniverseEntry:
    stock_code: str
    stock_name: str
    stock_name_en: str = ""
    market: str = ""
    dart_corp_code: str = ""
    aliases: tuple[str, ...] = field(default_factory=tuple)

    def terms(self) -> tuple[str, ...]:
        values = [
            self.stock_code,
            self.stock_name,
            self.stock_name_en,
            *self.aliases,
        ]
        return tuple(value for value in values if value)


@dataclass(frozen=True)
class StockCoverageReport:
    schema_version: str
    generated_at: str
    universe_path: str
    universe_count: int
    training_stock_count: int
    evaluation_stock_count: int
    raw_matched_stock_count: int
    training_coverage_ratio: float
    evaluation_coverage_ratio: float
    raw_coverage_ratio: float
    training_sample_count: int
    evaluation_sample_count: int
    raw_sample_count: int
    top_training_stocks: list[dict[str, int | str]]
    top_raw_stocks: list[dict[str, int | str]]
    coverage_gates: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def fetch_open_dart_stock_universe(api_key: str) -> list[StockUniverseEntry]:
    params = urlencode({"crtfc_key": api_key})
    request = Request(
        f"https://opendart.fss.or.kr/api/corpCode.xml?{params}",
        headers={"User-Agent": "Hannah-Montana-AI stock universe sync"},
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310  # nosec B310
        payload = response.read()

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        xml_name = archive.namelist()[0]
        root = ElementTree.fromstring(archive.read(xml_name))

    entries: dict[str, StockUniverseEntry] = {}
    for item in root.findall("list"):
        stock_code = (item.findtext("stock_code") or "").strip()
        stock_name = (item.findtext("corp_name") or "").strip()
        dart_corp_code = (item.findtext("corp_code") or "").strip()
        if not stock_code or not stock_name:
            continue
        entries[stock_code] = StockUniverseEntry(
            stock_code=stock_code,
            stock_name=stock_name,
            dart_corp_code=dart_corp_code,
        )
    return sorted(entries.values(), key=lambda stock: stock.stock_code)


def load_stock_universe(path: Path) -> list[StockUniverseEntry]:
    if not path.exists():
        return []
    entries: list[StockUniverseEntry] = []
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            aliases = tuple(
                alias.strip()
                for alias in row.get("aliases", "").split("|")
                if alias.strip()
            )
            entries.append(
                StockUniverseEntry(
                    stock_code=row["stock_code"].strip(),
                    stock_name=row["stock_name"].strip(),
                    stock_name_en=row.get("stock_name_en", "").strip(),
                    market=row.get("market", "").strip(),
                    dart_corp_code=row.get("dart_corp_code", "").strip(),
                    aliases=aliases,
                )
            )
    return entries


def write_stock_universe(path: Path, entries: Sequence[StockUniverseEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "stock_code",
                "stock_name",
                "stock_name_en",
                "market",
                "dart_corp_code",
                "aliases",
            ],
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "stock_code": entry.stock_code,
                    "stock_name": entry.stock_name,
                    "stock_name_en": entry.stock_name_en,
                    "market": entry.market,
                    "dart_corp_code": entry.dart_corp_code,
                    "aliases": "|".join(entry.aliases),
                }
            )


def build_stock_news_queries(
    stock_universe: Sequence[StockUniverseEntry],
    intents: Sequence[str] = DEFAULT_NEWS_INTENTS,
    stock_limit: int | None = None,
) -> list[str]:
    selected = list(stock_universe[:stock_limit]) if stock_limit else list(stock_universe)
    queries = [
        f"{stock.stock_name} {intent}"
        for stock in selected
        for intent in intents
        if stock.stock_name
    ]
    return list(dict.fromkeys(queries))


def attach_stock_metadata(
    sample: LabeledAlert,
    matcher: StockUniverseMatcher | None,
) -> LabeledAlert:
    if matcher is None or sample.stock_code:
        return sample
    stock = matcher.match(sample.text)
    if stock is None:
        return sample
    return LabeledAlert(
        text=sample.text,
        tags=sample.tags,
        sentiment=sample.sentiment,
        importance=sample.importance,
        source_type=sample.source_type,
        stock_code=stock.stock_code,
        stock_name=stock.stock_name,
        stock_aliases=list(stock.aliases),
    )


class StockUniverseMatcher:
    def __init__(self, stock_universe: Sequence[StockUniverseEntry]) -> None:
        terms: list[tuple[str, StockUniverseEntry]] = []
        for stock in stock_universe:
            for term in stock.terms():
                normalized = normalize_stock_term(term)
                if _is_usable_match_term(normalized):
                    terms.append((normalized, stock))
        self._terms = tuple(sorted(terms, key=lambda item: (-len(item[0]), item[0])))

    def match(self, text: str) -> StockUniverseEntry | None:
        normalized_text = normalize_stock_term(text)
        matches: list[tuple[int, StockUniverseEntry]] = []
        for term, stock in self._terms:
            position = normalized_text.find(term)
            if position >= 0:
                matches.append((position, stock))
        if not matches:
            return None
        return min(matches, key=lambda item: item[0])[1]

    def match_raw_alert(self, alert: RawCollectedAlert) -> StockUniverseEntry | None:
        return self.match(alert.text)


def build_stock_coverage_report(
    universe_path: Path,
    training_paths: Sequence[Path],
    evaluation_paths: Sequence[Path],
    raw_alert_path: Path,
    minimum_universe_count: int = 2_000,
    minimum_real_data_stock_count: int = 300,
) -> StockCoverageReport:
    universe = load_stock_universe(universe_path)
    matcher = StockUniverseMatcher(universe)
    training_samples = _load_samples(training_paths)
    evaluation_samples = _load_samples(evaluation_paths)
    raw_alerts = _load_raw_alerts(raw_alert_path)

    training_counter = _sample_stock_counter(training_samples)
    evaluation_counter = _sample_stock_counter(evaluation_samples)
    raw_counter = _raw_stock_counter(raw_alerts, matcher)

    coverage_gates = _coverage_gates(
        universe_count=len(universe),
        training_stock_count=len(training_counter),
        evaluation_stock_count=len(evaluation_counter),
        raw_matched_stock_count=len(raw_counter),
        minimum_universe_count=minimum_universe_count,
        minimum_real_data_stock_count=minimum_real_data_stock_count,
    )
    return StockCoverageReport(
        schema_version=COVERAGE_REPORT_SCHEMA_VERSION,
        generated_at=datetime.now(UTC).isoformat(),
        universe_path=_report_path(universe_path),
        universe_count=len(universe),
        training_stock_count=len(training_counter),
        evaluation_stock_count=len(evaluation_counter),
        raw_matched_stock_count=len(raw_counter),
        training_coverage_ratio=_ratio(len(training_counter), len(universe)),
        evaluation_coverage_ratio=_ratio(len(evaluation_counter), len(universe)),
        raw_coverage_ratio=_ratio(len(raw_counter), len(universe)),
        training_sample_count=len(training_samples),
        evaluation_sample_count=len(evaluation_samples),
        raw_sample_count=len(raw_alerts),
        top_training_stocks=_top_stock_rows(training_counter, universe),
        top_raw_stocks=_top_stock_rows(raw_counter, universe),
        coverage_gates=coverage_gates,
    )


def write_json_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_stock_term(value: str) -> str:
    return _NORMALIZE_PATTERN.sub("", value.lower())


def _is_usable_match_term(value: str) -> bool:
    if value.isdigit() and len(value) == 6:
        return True
    return len(value) >= 3


def _load_samples(paths: Sequence[Path]) -> list[LabeledAlert]:
    samples: list[LabeledAlert] = []
    for path in paths:
        if path.exists():
            samples.extend(load_labeled_alerts(path))
    return samples


def _load_raw_alerts(path: Path) -> list[RawCollectedAlert]:
    if not path.exists():
        return []
    alerts: list[RawCollectedAlert] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        alerts.append(
            RawCollectedAlert(
                source_type=payload["source_type"],
                title=payload["title"],
                snippet=payload["snippet"],
                original_url=payload["original_url"],
                published_at=payload["published_at"],
                provider=payload["provider"],
            )
        )
    return alerts


def _sample_stock_counter(samples: Iterable[LabeledAlert]) -> Counter[str]:
    return Counter(sample.stock_code for sample in samples if sample.stock_code)


def _raw_stock_counter(
    alerts: Iterable[RawCollectedAlert],
    matcher: StockUniverseMatcher,
) -> Counter[str]:
    counter: Counter[str] = Counter()
    for alert in alerts:
        stock = matcher.match_raw_alert(alert)
        if stock is not None:
            counter[stock.stock_code] += 1
    return counter


def _coverage_gates(
    universe_count: int,
    training_stock_count: int,
    evaluation_stock_count: int,
    raw_matched_stock_count: int,
    minimum_universe_count: int,
    minimum_real_data_stock_count: int,
) -> dict[str, Any]:
    checks = {
        "universe_count": {
            "actual": universe_count,
            "minimum": minimum_universe_count,
            "status": "pass" if universe_count >= minimum_universe_count else "fail",
        },
        "raw_matched_stock_count": {
            "actual": raw_matched_stock_count,
            "minimum": minimum_real_data_stock_count,
            "status": (
                "pass" if raw_matched_stock_count >= minimum_real_data_stock_count else "fail"
            ),
        },
        "training_stock_count": {
            "actual": training_stock_count,
            "minimum": minimum_real_data_stock_count,
            "status": (
                "pass" if training_stock_count >= minimum_real_data_stock_count else "fail"
            ),
        },
        "evaluation_stock_count": {
            "actual": evaluation_stock_count,
            "minimum": min(100, minimum_real_data_stock_count),
            "status": (
                "pass"
                if evaluation_stock_count >= min(100, minimum_real_data_stock_count)
                else "fail"
            ),
        },
    }
    return {
        "overall_status": "pass"
        if all(check["status"] == "pass" for check in checks.values())
        else "fail",
        "checks": checks,
    }


def _top_stock_rows(
    counter: Counter[str],
    universe: Sequence[StockUniverseEntry],
    limit: int = 20,
) -> list[dict[str, int | str]]:
    names = {stock.stock_code: stock.stock_name for stock in universe}
    return [
        {
            "stock_code": stock_code,
            "stock_name": names.get(stock_code, ""),
            "sample_count": sample_count,
        }
        for stock_code, sample_count in counter.most_common(limit)
    ]


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())
