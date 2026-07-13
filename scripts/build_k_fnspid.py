from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from hannah_montana_ai.training.collector import read_raw_alerts
from hannah_montana_ai.training.dataset import load_jsonl_payloads, resolve_jsonl_paths
from hannah_montana_ai.training.k_fnspid.entity_linker import ExactContextEntityLinker
from hannah_montana_ai.training.k_fnspid.event_clusterer import assign_event_clusters
from hannah_montana_ai.training.k_fnspid.impact_labeler import build_market_impacts
from hannah_montana_ai.training.k_fnspid.quality import build_quality_report
from hannah_montana_ai.training.k_fnspid.schema import CanonicalDocument, DailyPrice, DocumentEntity
from hannah_montana_ai.training.k_fnspid.splitter import temporal_split
from hannah_montana_ai.training.k_fnspid.temporal import (
    effective_trade_date,
    normalize_publication_time,
)
from hannah_montana_ai.training.stock_universe import load_stock_universe

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW = PROJECT_ROOT / "data/raw/collected_alerts.jsonl"
DEFAULT_FULL = PROJECT_ROOT / "data/training/financial_alert_full_content_gold.jsonl"
DEFAULT_STOCKS = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
DEFAULT_PRICES = PROJECT_ROOT / "data/market/market_daily_price.parquet"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/k_fnspid/v2"
DEFAULT_GOLD = PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the K-FNSPID research dataset.")
    parser.add_argument("--raw-path", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--full-content-path", type=Path, default=DEFAULT_FULL)
    parser.add_argument("--stock-universe-path", type=Path, default=DEFAULT_STOCKS)
    parser.add_argument("--prices", type=Path, default=DEFAULT_PRICES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gold-path", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--dataset-version", default="k-fnspid-v2")
    parser.add_argument("--minimum-document-count", type=int, default=500_000)
    parser.add_argument("--minimum-price-row-count", type=int, default=3_000_000)
    parser.add_argument("--minimum-price-stock-count", type=int, default=2_000)
    parser.add_argument("--validation-start", type=date.fromisoformat, default=date(2025, 1, 1))
    parser.add_argument("--test-start", type=date.fromisoformat, default=date(2026, 1, 1))
    args = parser.parse_args()

    prices = load_prices(args.prices)
    trading_dates = sorted({date.fromisoformat(row.trade_date) for row in prices})
    if not trading_dates:
        raise SystemExit("파일 기반 market daily price 데이터셋이 비어 있다.")
    if len(prices) < args.minimum_price_row_count:
        raise SystemExit("시세 행 수가 대규모 품질 gate에 미달한다.")
    if len({row.stock_code for row in prices}) < args.minimum_price_stock_count:
        raise SystemExit("시세 종목 수가 전체 시장 품질 gate에 미달한다.")
    trading_date_set = set(trading_dates)
    full_rows = load_jsonl_payloads(args.full_content_path)
    full_by_url = {
        str(row.get("source_url", "")): row for row in full_rows if row.get("source_url")
    }
    linker = ExactContextEntityLinker(load_stock_universe(args.stock_universe_path))

    documents: list[CanonicalDocument] = []
    entities: list[DocumentEntity] = []
    for raw in read_raw_alerts(args.raw_path):
        publication = normalize_publication_time(raw.published_at, trading_date_set)
        publication_date = date.fromisoformat(publication.published_at_kst[:10])
        if publication_date < trading_dates[0]:
            continue
        trade_date = effective_trade_date(publication, trading_dates)
        if not trade_date:
            continue
        full = full_by_url.get(raw.original_url, {})
        full_text = str(full.get("full_content", ""))
        content_hash = str(full.get("content_hash") or raw.content_hash)
        document_id = sha256(
            f"{raw.provider}:{raw.original_url}:{raw.published_at}:{content_hash}".encode()
        ).hexdigest()
        document = CanonicalDocument(
            document_id=document_id,
            provider=raw.provider,
            source_type=raw.source_type,
            title=raw.title,
            snippet=raw.snippet,
            full_text=full_text,
            source_url=raw.original_url,
            content_hash=content_hash,
            published_at_utc=publication.published_at_utc,
            published_at_kst=publication.published_at_kst,
            published_precision=publication.precision,
            market_session=publication.market_session,
            effective_trade_date=trade_date,
        )
        documents.append(document)
        result = linker.link(
            document_id=document_id,
            title=raw.title,
            body=f"{raw.snippet} {full_text}",
            source_type=raw.source_type,
        )
        entities.extend(result.links)

    documents = list({row.document_id: row for row in documents}.values())
    if len(documents) < args.minimum_document_count:
        raise SystemExit("문서 수가 K-FNSPID 대규모 품질 gate에 미달한다.")
    entities = list({(row.document_id, row.stock_code): row for row in entities}.values())
    clusters = assign_event_clusters(documents)
    documents = [replace(row, event_cluster_id=clusters[row.document_id]) for row in documents]
    document_dates = {row.document_id: row.effective_trade_date for row in documents}
    document_id_by_url = {row.source_url: row.document_id for row in documents}
    annotations = [
        {
            "document_id": document_id_by_url[str(row.get("source_url", ""))],
            "sentiment": row["sentiment"],
            "importance": row["importance"],
            "event_tags": row["tags"],
            "stock_code": row.get("stock_code"),
            "review_status": row.get("source_review_status", ""),
            "reviewer_id": row.get("reviewer_id", ""),
            "review_note": row.get("review_note", ""),
        }
        for row in load_jsonl_payloads(args.gold_path)
        if str(row.get("source_url", "")) in document_id_by_url
    ]
    primary_pairs = [
        (row.document_id, row.stock_code, document_dates[row.document_id])
        for row in entities
        if row.relation == "PRIMARY"
    ]
    impacts = build_market_impacts(primary_pairs, prices)
    clusters_by_stock_date: dict[tuple[str, str], set[str]] = defaultdict(set)
    cluster_by_document = {row.document_id: row.event_cluster_id for row in documents}
    for document_id, stock_code, trade_date in primary_pairs:
        clusters_by_stock_date[(stock_code, trade_date)].add(cluster_by_document[document_id])
    impacts = [
        replace(
            row,
            confounded=(
                row.confounded
                or len(clusters_by_stock_date[(row.stock_code, row.effective_trade_date)]) > 1
            ),
        )
        for row in impacts
    ]
    split_rows = [
        {
            "document_id": document.document_id,
            "event_cluster_id": document.event_cluster_id,
            "split": temporal_split(
                document.effective_trade_date,
                validation_start=args.validation_start,
                test_start=args.test_start,
            ),
        }
        for document in documents
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_parquet(args.output_dir / "documents.parquet", [row.to_dict() for row in documents])
    write_parquet(
        args.output_dir / "document_entities.parquet", [row.to_dict() for row in entities]
    )
    if args.prices.suffix == ".parquet":
        shutil.copyfile(args.prices, args.output_dir / "prices_daily.parquet")
    else:
        write_parquet(args.output_dir / "prices_daily.parquet", [row.__dict__ for row in prices])
    write_parquet(args.output_dir / "market_impacts.parquet", [row.to_dict() for row in impacts])
    write_parquet(args.output_dir / "annotations.parquet", annotations)
    write_parquet(args.output_dir / "splits.parquet", split_rows)

    report = build_quality_report(documents, entities, impacts)
    manifest = report | {
        "dataset_version": args.dataset_version,
        "generated_at": datetime.now().astimezone().isoformat(),
        "validation_start": args.validation_start.isoformat(),
        "test_start": args.test_start.isoformat(),
        "gold_annotation_count": len(annotations),
        "scale_gate": {
            "minimum_document_count": args.minimum_document_count,
            "minimum_price_row_count": args.minimum_price_row_count,
            "minimum_price_stock_count": args.minimum_price_stock_count,
            "passed": True,
        },
        "split_count": dict(sorted(Counter(row["split"] for row in split_rows).items())),
        "publication_year_count": dict(
            sorted(Counter(row.published_at_kst[:4] for row in documents).items())
        ),
        "unconfounded_impact_count": sum(
            row.materiality_score is not None and not row.confounded for row in impacts
        ),
        "raw_source": _source_manifest(args.raw_path),
        "price_source": _source_manifest(args.prices),
        "files": file_manifest(args.output_dir),
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False))


def load_prices(path: Path) -> list[DailyPrice]:
    if not path.exists():
        return []
    if path.suffix == ".parquet":
        rows: list[DailyPrice] = []
        for batch in pq.ParquetFile(path).iter_batches(batch_size=100_000):
            rows.extend(DailyPrice(**row) for row in batch.to_pylist())
        return rows
    rows: list[DailyPrice] = []
    with path.open(newline="", encoding="utf-8") as file:
        for payload in csv.DictReader(file):
            rows.append(
                DailyPrice(
                    stock_code=_field(payload, "stock_code", "stockCode"),
                    trade_date=_field(payload, "trade_date", "tradeDate"),
                    market=_field(payload, "market"),
                    open_price=_number(payload, "open_price_krw", "openPriceKrw"),
                    high_price=_number(payload, "high_price_krw", "highPriceKrw"),
                    low_price=_number(payload, "low_price_krw", "lowPriceKrw"),
                    close_price=_number(payload, "close_price_krw", "closePriceKrw"),
                    adjusted_close=_number(
                        payload, "adjusted_close_price_krw", "adjustedClosePriceKrw"
                    ),
                    volume=int(_number(payload, "trading_volume", "tradingVolume")),
                    trading_value=_number(payload, "trading_value_krw", "tradingValueKrw"),
                )
            )
    return rows


def write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        pq.write_table(
            pa.table({"empty": pa.array([], type=pa.string())}), path, compression="zstd"
        )
        return
    pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")


def file_manifest(directory: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": path.name,
            "bytes": path.stat().st_size,
            "sha256": _file_sha256(path),
        }
        for path in sorted(directory.glob("*.parquet"))
    ]


def _source_manifest(path: Path) -> dict[str, Any]:
    resolved = resolve_jsonl_paths(path) if path.suffix == ".jsonl" else [path]
    files = [path, *resolved] if resolved != [path] else [path]
    file_rows = [
        {
            "path": str(file.relative_to(PROJECT_ROOT)),
            "bytes": file.stat().st_size,
            "sha256": _file_sha256(file),
        }
        for file in files
    ]
    composite = sha256()
    for row in file_rows:
        composite.update(f"{row['path']}:{row['sha256']}\n".encode())
    source_sha256 = (
        str(file_rows[0]["sha256"]) if len(file_rows) == 1 else composite.hexdigest()
    )
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "bytes": sum(int(row["bytes"]) for row in file_rows),
        "sha256": source_sha256,
        "files": file_rows,
    }


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _field(row: dict[str, str], *names: str) -> str:
    return next((row.get(name, "") for name in names if row.get(name)), "")


def _number(row: dict[str, str], *names: str) -> float:
    value = _field(row, *names)
    return float(value) if value else 0.0


if __name__ == "__main__":
    main()
