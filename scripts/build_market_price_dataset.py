from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pyarrow as pa
import pyarrow.parquet as pq

from hannah_montana_ai.training.stock_universe import load_stock_universe

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXTERNAL = PROJECT_ROOT / "data/external/kospi-daily-stock-features.parquet"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/market/market_daily_price.parquet"
DEFAULT_MANIFEST = PROJECT_ROOT / "data/market/manifest.json"
DEFAULT_STOCKS = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
HF_KOSPI_URL = (
    "https://huggingface.co/datasets/podongchip/kospi-daily-stock-features-2021-2026/"
    "resolve/main/kospi_data_v1.parquet"
)
PUBLIC_DATA_URL = (
    "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the file-backed K-FNSPID market dataset.")
    parser.add_argument("--hf-kospi-path", type=Path, default=DEFAULT_EXTERNAL)
    parser.add_argument("--download-hf-kospi", action="store_true")
    parser.add_argument("--public-data-from", type=date.fromisoformat)
    parser.add_argument("--public-data-to", type=date.fromisoformat)
    parser.add_argument("--yahoo-from", type=date.fromisoformat)
    parser.add_argument("--yahoo-to", type=date.fromisoformat)
    parser.add_argument("--stock-universe", type=Path, default=DEFAULT_STOCKS)
    parser.add_argument("--yahoo-workers", type=int, default=8)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    sources: list[dict[str, Any]] = []
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    if args.download_hf_kospi and not args.hf_kospi_path.exists():
        download_file(HF_KOSPI_URL, args.hf_kospi_path)
    if args.hf_kospi_path.exists():
        imported = load_hf_kospi(args.hf_kospi_path)
        rows.update({(row["stock_code"], row["trade_date"]): row for row in imported})
        sources.append(
            source_manifest("hf-kospi-daily-features", args.hf_kospi_path, len(imported))
        )

    if args.public_data_from and args.public_data_to:
        service_key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "")
        if not service_key:
            raise SystemExit("DATA_GO_KR_SERVICE_KEY is required for public-data collection")
        imported = collect_public_data_prices(
            service_key,
            from_date=args.public_data_from,
            to_date=args.public_data_to,
        )
        rows.update({(row["stock_code"], row["trade_date"]): row for row in imported})
        sources.append({"source": "data-go-kr-stock-prices", "row_count": len(imported)})

    if args.yahoo_from and args.yahoo_to:
        imported = collect_yahoo_prices(
            args.stock_universe,
            from_date=args.yahoo_from,
            to_date=args.yahoo_to,
            workers=args.yahoo_workers,
            allowed_stock_codes={stock_code for stock_code, _ in rows},
        )
        rows.update({(row["stock_code"], row["trade_date"]): row for row in imported})
        sources.append({"source": "yahoo-finance-chart-daily", "row_count": len(imported)})

    normalized = sorted(rows.values(), key=lambda row: (row["stock_code"], row["trade_date"]))
    if not normalized:
        raise SystemExit("no market price source was provided")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(normalized), args.output, compression="zstd")
    manifest = {
        "schema_version": "k-fnspid-market-price/v1",
        "generated_at": datetime.now().astimezone().isoformat(),
        "row_count": len(normalized),
        "stock_count": len({row["stock_code"] for row in normalized}),
        "min_trade_date": min(row["trade_date"] for row in normalized),
        "max_trade_date": max(row["trade_date"] for row in normalized),
        "sources": sources,
        "output": {
            "path": str(args.output.relative_to(PROJECT_ROOT)),
            "bytes": args.output.stat().st_size,
            "sha256": sha256(args.output.read_bytes()).hexdigest(),
        },
    }
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False))


def download_file(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.part")
    request = Request(  # noqa: S310  # nosec B310
        url,
        headers={"User-Agent": "Hannah-Montana-AI K-FNSPID research"},
    )
    with urlopen(request, timeout=60) as response, temporary.open("wb") as output:  # noqa: S310
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    temporary.replace(path)


def load_hf_kospi(path: Path) -> list[dict[str, Any]]:
    table = pq.read_table(
        path,
        columns=["Date", "Code", "Open", "High", "Low", "Close", "Volume", "Marcap"],
    )
    rows: list[dict[str, Any]] = []
    for source in table.to_pylist():
        close = float(source["Close"] or 0.0)
        rows.append(
            {
                "stock_code": str(source["Code"]),
                "trade_date": str(source["Date"]),
                "market": "KOSPI",
                "open_price": float(source["Open"] or 0.0),
                "high_price": float(source["High"] or 0.0),
                "low_price": float(source["Low"] or 0.0),
                "close_price": close,
                "adjusted_close": close,
                "volume": int(source["Volume"] or 0),
                "trading_value": float(source["Marcap"] or 0.0),
            }
        )
    return rows


def collect_public_data_prices(
    service_key: str,
    *,
    from_date: date,
    to_date: date,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = 1
    while True:
        params = urlencode(
            {
                "serviceKey": service_key,
                "resultType": "json",
                "beginBasDt": from_date.strftime("%Y%m%d"),
                "endBasDt": to_date.strftime("%Y%m%d"),
                "numOfRows": 10_000,
                "pageNo": page,
            }
        )
        request = Request(f"{PUBLIC_DATA_URL}?{params}")  # noqa: S310  # nosec B310
        with urlopen(request, timeout=30) as response:  # noqa: S310
            payload = json.loads(response.read())
        body = payload.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        for source in items:
            close = float(source.get("clpr") or 0.0)
            rows.append(
                {
                    "stock_code": str(source.get("srtnCd", ""))[-6:],
                    "trade_date": _public_date(str(source.get("basDt", ""))),
                    "market": str(source.get("mrktCtg", "")),
                    "open_price": float(source.get("mkp") or 0.0),
                    "high_price": float(source.get("hipr") or 0.0),
                    "low_price": float(source.get("lopr") or 0.0),
                    "close_price": close,
                    "adjusted_close": close,
                    "volume": int(source.get("trqu") or 0),
                    "trading_value": float(source.get("trPrc") or 0.0),
                }
            )
        total = int(body.get("totalCount") or 0)
        if page * 10_000 >= total or not items:
            break
        page += 1
        time.sleep(0.2)
    return rows


def collect_yahoo_prices(
    stock_universe_path: Path,
    *,
    from_date: date,
    to_date: date,
    workers: int,
    allowed_stock_codes: set[str],
) -> list[dict[str, Any]]:
    stocks = [
        stock
        for stock in load_stock_universe(stock_universe_path)
        if stock.stock_code in allowed_stock_codes
    ]
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, min(workers, 16))) as executor:
        futures = {
            executor.submit(
                fetch_yahoo_stock, stock.stock_code, stock.market, from_date, to_date
            ): stock.stock_code
            for stock in stocks
        }
        for future in as_completed(futures):
            try:
                rows.extend(future.result())
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue
    return rows


def fetch_yahoo_stock(
    stock_code: str,
    market: str,
    from_date: date,
    to_date: date,
) -> list[dict[str, Any]]:
    suffix = "KS" if market == "KOSPI" else "KQ"
    period1 = int(datetime.combine(from_date, datetime.min.time()).timestamp())
    period2 = int(datetime.combine(to_date, datetime.min.time()).timestamp()) + 86_400
    params = urlencode(
        {"period1": period1, "period2": period2, "interval": "1d", "events": "history"}
    )
    request = Request(  # noqa: S310  # nosec B310
        f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_code}.{suffix}?{params}",
        headers={"User-Agent": "Mozilla/5.0 Hannah-Montana-AI K-FNSPID"},
    )
    with urlopen(request, timeout=5) as response:  # noqa: S310
        payload = json.loads(response.read())
    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    quote = result["indicators"]["quote"][0]
    adjusted = result["indicators"].get("adjclose", [{}])[0].get("adjclose", [])
    rows: list[dict[str, Any]] = []
    for index, timestamp in enumerate(timestamps):
        close = quote["close"][index]
        if close is None:
            continue
        rows.append(
            {
                "stock_code": stock_code,
                "trade_date": datetime.fromtimestamp(timestamp).date().isoformat(),
                "market": market,
                "open_price": float(quote["open"][index] or close),
                "high_price": float(quote["high"][index] or close),
                "low_price": float(quote["low"][index] or close),
                "close_price": float(close),
                "adjusted_close": float(
                    adjusted[index] if index < len(adjusted) and adjusted[index] else close
                ),
                "volume": int(quote["volume"][index] or 0),
                "trading_value": float(close) * int(quote["volume"][index] or 0),
            }
        )
    return rows


def source_manifest(source: str, path: Path, row_count: int) -> dict[str, Any]:
    return {
        "source": source,
        "path": str(path.relative_to(PROJECT_ROOT)),
        "row_count": row_count,
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _public_date(value: str) -> str:
    return date(int(value[:4]), int(value[4:6]), int(value[6:8])).isoformat()


if __name__ == "__main__":
    main()
