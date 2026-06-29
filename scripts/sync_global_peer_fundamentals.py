from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.training.global_peer_trainer import (
    GlobalPeerFundamentals,
    fetch_krx_market_caps_usd,
    fetch_nasdaq_market_cap_usd,
    fetch_naver_korea_market_cap_usd,
    fetch_open_dart_annual_fundamentals,
    fetch_sec_annual_fundamentals,
    fetch_sec_ticker_cik_map,
    is_eligible_us_peer,
    load_global_peer_fundamentals,
    load_us_stock_universe,
    write_global_peer_fundamentals,
)
from hannah_montana_ai.training.stock_universe import load_env_file, load_stock_universe

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports/global-peer-fundamentals-sync-report.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=get_settings().global_peer_fundamentals_path)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--env-file", type=Path, default=PROJECT_ROOT / "secrets.local.env")
    parser.add_argument("--fiscal-year", type=int, default=date.today().year - 1)
    parser.add_argument("--fiscal-year-lookback", type=int, default=2)
    parser.add_argument("--krw-usd-rate", type=float, default=0.00072)
    parser.add_argument("--krx-base-date", default=_previous_weekday().strftime("%Y%m%d"))
    parser.add_argument("--korea-stock-limit", type=int, default=0)
    parser.add_argument("--us-stock-limit", type=int, default=0)
    parser.add_argument("--korea-stock-codes", default="")
    parser.add_argument("--us-tickers", default="")
    parser.add_argument("--include-ineligible-us", action="store_true")
    parser.add_argument("--us-workers", type=int, default=4)
    parser.add_argument("--request-delay-sec", type=float, default=0.06)
    parser.add_argument("--checkpoint-every", type=int, default=100)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--skip-korea", action="store_true")
    parser.add_argument("--skip-us", action="store_true")
    parser.add_argument("--skip-korea-market-cap", action="store_true")
    parser.add_argument("--skip-us-market-cap", action="store_true")
    args = parser.parse_args()

    load_env_file(args.env_file)
    row_map = (
        {}
        if args.refresh
        else load_global_peer_fundamentals(args.output)
    )
    failures: list[dict[str, str]] = []

    korea_rows: list[GlobalPeerFundamentals] = []
    us_rows: list[GlobalPeerFundamentals] = []
    if not args.skip_korea:
        korea_rows, korea_failures = sync_korea_fundamentals(
            output_path=args.output,
            row_map=row_map,
            fiscal_year=args.fiscal_year,
            fiscal_year_lookback=args.fiscal_year_lookback,
            krw_usd_rate=args.krw_usd_rate,
            krx_base_date=args.krx_base_date,
            stock_limit=args.korea_stock_limit,
            stock_codes=_csv_set(args.korea_stock_codes),
            request_delay_sec=args.request_delay_sec,
            checkpoint_every=args.checkpoint_every,
        )
        failures.extend(korea_failures)
    if not args.skip_korea_market_cap:
        korea_market_cap_rows, korea_market_cap_failures = sync_korea_market_caps(
            output_path=args.output,
            row_map=row_map,
            krw_usd_rate=args.krw_usd_rate,
            stock_limit=args.korea_stock_limit,
            stock_codes=_csv_set(args.korea_stock_codes),
            request_delay_sec=args.request_delay_sec,
            checkpoint_every=args.checkpoint_every,
            workers=args.us_workers,
        )
        korea_rows.extend(korea_market_cap_rows)
        failures.extend(korea_market_cap_failures)

    if not args.skip_us:
        us_rows, us_failures = sync_us_fundamentals(
            output_path=args.output,
            row_map=row_map,
            fiscal_year=args.fiscal_year,
            stock_limit=args.us_stock_limit,
            tickers=_csv_set(args.us_tickers),
            include_ineligible_us=args.include_ineligible_us,
            request_delay_sec=args.request_delay_sec,
            checkpoint_every=args.checkpoint_every,
            workers=args.us_workers,
        )
        failures.extend(us_failures)
        if not args.skip_us_market_cap:
            us_market_cap_rows, us_market_cap_failures = sync_us_market_caps(
                output_path=args.output,
                row_map=row_map,
                stock_limit=args.us_stock_limit,
                tickers=_csv_set(args.us_tickers),
                include_ineligible_us=args.include_ineligible_us,
                request_delay_sec=args.request_delay_sec,
                checkpoint_every=args.checkpoint_every,
                workers=args.us_workers,
            )
            us_rows.extend(us_market_cap_rows)
            failures.extend(us_market_cap_failures)

    rows = list(row_map.values())
    write_global_peer_fundamentals(args.output, rows)
    report = {
        "schema_version": "global-peer-fundamentals-sync/v1",
        "fiscal_year": args.fiscal_year,
        "fiscal_year_lookback": args.fiscal_year_lookback,
        "output_path": str(args.output),
        "row_count": len(rows),
        "korea_row_count": sum(1 for row in rows if row.market == "KR"),
        "us_row_count": sum(1 for row in rows if row.market == "US"),
        "new_or_refreshed_korea_row_count": len(korea_rows),
        "new_or_refreshed_us_row_count": len(us_rows),
        "failure_count": len(failures),
        "failures_sample": failures[:20],
        "credential_policy": "credentials are loaded from gitignored local env only",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def sync_korea_fundamentals(
    output_path: Path,
    row_map: dict[tuple[str, str], GlobalPeerFundamentals],
    fiscal_year: int,
    fiscal_year_lookback: int,
    krw_usd_rate: float,
    krx_base_date: str,
    stock_limit: int,
    stock_codes: set[str],
    request_delay_sec: float,
    checkpoint_every: int,
) -> tuple[list[GlobalPeerFundamentals], list[dict[str, str]]]:
    api_key = os.environ.get("OPEN_DART_API_KEY", "")
    if not api_key:
        return [], [{"market": "KR", "reason": "OPEN_DART_API_KEY is not configured"}]
    stocks = load_stock_universe(get_settings().stock_universe_path)
    if stock_codes:
        stocks = [stock for stock in stocks if stock.stock_code in stock_codes]
    selected = stocks[:stock_limit] if stock_limit else stocks
    market_caps = _optional_krx_market_caps(krx_base_date, krw_usd_rate)
    rows: list[GlobalPeerFundamentals] = []
    failures: list[dict[str, str]] = []
    fiscal_years = _fiscal_year_candidates(fiscal_year, fiscal_year_lookback)
    for index, stock in enumerate(selected, start=1):
        if not stock.dart_corp_code:
            continue
        key = ("KR", stock.stock_code.upper())
        if key in row_map:
            continue
        try:
            row = None
            for year in fiscal_years:
                row = fetch_open_dart_annual_fundamentals(
                    api_key=api_key,
                    stock_code=stock.stock_code,
                    corp_code=stock.dart_corp_code,
                    fiscal_year=year,
                    krw_usd_rate=krw_usd_rate,
                )
                if row:
                    break
                time.sleep(request_delay_sec)
            if row:
                row = replace(row, market_cap_usd=market_caps.get(stock.stock_code))
                row_map[key] = row
                rows.append(row)
        except Exception as exception:
            failures.append(
                {
                    "market": "KR",
                    "identifier": stock.stock_code,
                    "reason": str(exception),
                }
            )
        if index % checkpoint_every == 0:
            write_global_peer_fundamentals(output_path, list(row_map.values()))
            print(
                json.dumps(
                    {
                        "phase": "KR",
                        "processed": index,
                        "selected": len(selected),
                        "total_rows": len(row_map),
                        "failures": len(failures),
                    },
                    ensure_ascii=False,
                )
            )
        time.sleep(request_delay_sec)
    return rows, failures


def sync_us_fundamentals(
    output_path: Path,
    row_map: dict[tuple[str, str], GlobalPeerFundamentals],
    fiscal_year: int,
    stock_limit: int,
    tickers: set[str],
    include_ineligible_us: bool,
    request_delay_sec: float,
    checkpoint_every: int,
    workers: int,
) -> tuple[list[GlobalPeerFundamentals], list[dict[str, str]]]:
    ticker_cik = fetch_sec_ticker_cik_map()
    stocks = load_us_stock_universe(get_settings().us_stock_universe_path)
    if tickers:
        stocks = [stock for stock in stocks if stock.ticker.upper() in tickers]
    if not include_ineligible_us:
        stocks = [stock for stock in stocks if is_eligible_us_peer(stock)]
    selected = stocks[:stock_limit] if stock_limit else stocks
    if workers > 1:
        return _sync_us_fundamentals_parallel(
            output_path=output_path,
            row_map=row_map,
            ticker_cik=ticker_cik,
            selected=selected,
            fiscal_year=fiscal_year,
            request_delay_sec=request_delay_sec,
            checkpoint_every=checkpoint_every,
            workers=workers,
        )
    rows: list[GlobalPeerFundamentals] = []
    failures: list[dict[str, str]] = []
    for index, stock in enumerate(selected, start=1):
        cik = ticker_cik.get(stock.ticker.upper())
        if not cik:
            continue
        key = ("US", stock.ticker.upper())
        if key in row_map:
            continue
        try:
            row = fetch_sec_annual_fundamentals(
                ticker=stock.ticker,
                cik=cik,
                fiscal_year=fiscal_year,
            )
            if row:
                row_map[key] = row
                rows.append(row)
        except Exception as exception:
            failures.append(
                {
                    "market": "US",
                    "identifier": stock.ticker,
                    "reason": str(exception),
                }
            )
        if index % checkpoint_every == 0:
            write_global_peer_fundamentals(output_path, list(row_map.values()))
            print(
                json.dumps(
                    {
                        "phase": "US",
                        "processed": index,
                        "selected": len(selected),
                        "total_rows": len(row_map),
                        "failures": len(failures),
                    },
                    ensure_ascii=False,
                )
            )
        time.sleep(request_delay_sec)
    return rows, failures


def sync_korea_market_caps(
    output_path: Path,
    row_map: dict[tuple[str, str], GlobalPeerFundamentals],
    krw_usd_rate: float,
    stock_limit: int,
    stock_codes: set[str],
    request_delay_sec: float,
    checkpoint_every: int,
    workers: int,
) -> tuple[list[GlobalPeerFundamentals], list[dict[str, str]]]:
    stocks = load_stock_universe(get_settings().stock_universe_path)
    if stock_codes:
        stocks = [stock for stock in stocks if stock.stock_code in stock_codes]
    selected = stocks[:stock_limit] if stock_limit else stocks
    pending = [
        stock.stock_code
        for stock in selected
        if row_map.get(("KR", stock.stock_code)) is None
        or row_map[("KR", stock.stock_code)].market_cap_usd is None
    ]
    rows: list[GlobalPeerFundamentals] = []
    failures: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(
                _fetch_korea_market_cap_worker,
                stock_code,
                krw_usd_rate,
                request_delay_sec,
            ): stock_code
            for stock_code in pending
        }
        for processed, future in enumerate(as_completed(futures), start=1):
            stock_code = futures[future]
            try:
                market_cap = future.result()
                if market_cap is not None:
                    key = ("KR", stock_code)
                    existing = row_map.get(key)
                    if existing:
                        source = _append_source(existing.source, "NAVER_STOCK_MARKET_CAP")
                        row = replace(existing, market_cap_usd=market_cap, source=source)
                    else:
                        row = GlobalPeerFundamentals(
                            market="KR",
                            identifier=stock_code,
                            fiscal_year=None,
                            market_cap_usd=market_cap,
                            revenue_usd=None,
                            operating_income_usd=None,
                            net_income_usd=None,
                            currency="USD",
                            source="NAVER_STOCK_MARKET_CAP",
                        )
                    row_map[key] = row
                    rows.append(row)
            except Exception as exception:
                failures.append(
                    {
                        "market": "KR",
                        "identifier": stock_code,
                        "reason": str(exception),
                    }
                )
            if processed % checkpoint_every == 0:
                write_global_peer_fundamentals(output_path, list(row_map.values()))
                print(
                    json.dumps(
                        {
                            "phase": "KR_MARKET_CAP",
                            "processed": processed,
                            "pending": len(pending),
                            "total_rows": len(row_map),
                            "failures": len(failures),
                            "workers": workers,
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
    write_global_peer_fundamentals(output_path, list(row_map.values()))
    return rows, failures


def _sync_us_fundamentals_parallel(
    output_path: Path,
    row_map: dict[tuple[str, str], GlobalPeerFundamentals],
    ticker_cik: dict[str, str],
    selected: list,
    fiscal_year: int,
    request_delay_sec: float,
    checkpoint_every: int,
    workers: int,
) -> tuple[list[GlobalPeerFundamentals], list[dict[str, str]]]:
    pending = []
    for stock in selected:
        cik = ticker_cik.get(stock.ticker.upper())
        key = ("US", stock.ticker.upper())
        if cik and key not in row_map:
            pending.append((stock.ticker, cik, key))

    rows: list[GlobalPeerFundamentals] = []
    failures: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                _fetch_us_fundamental_worker,
                ticker,
                cik,
                fiscal_year,
                request_delay_sec,
            ): (ticker, key)
            for ticker, cik, key in pending
        }
        for processed, future in enumerate(as_completed(futures), start=1):
            ticker, key = futures[future]
            try:
                row = future.result()
                if row:
                    row_map[key] = row
                    rows.append(row)
            except Exception as exception:
                failures.append(
                    {
                        "market": "US",
                        "identifier": ticker,
                        "reason": str(exception),
                    }
                )
            if processed % checkpoint_every == 0:
                write_global_peer_fundamentals(output_path, list(row_map.values()))
                print(
                    json.dumps(
                        {
                            "phase": "US",
                            "processed": processed,
                            "selected": len(selected),
                            "pending": len(pending),
                            "total_rows": len(row_map),
                            "failures": len(failures),
                            "workers": workers,
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
    write_global_peer_fundamentals(output_path, list(row_map.values()))
    return rows, failures


def _fetch_us_fundamental_worker(
    ticker: str,
    cik: str,
    fiscal_year: int,
    request_delay_sec: float,
) -> GlobalPeerFundamentals | None:
    if request_delay_sec > 0:
        time.sleep(request_delay_sec)
    return fetch_sec_annual_fundamentals(
        ticker=ticker,
        cik=cik,
        fiscal_year=fiscal_year,
    )


def _fetch_korea_market_cap_worker(
    stock_code: str,
    krw_usd_rate: float,
    request_delay_sec: float,
) -> float | None:
    if request_delay_sec > 0:
        time.sleep(request_delay_sec)
    return fetch_naver_korea_market_cap_usd(stock_code, krw_usd_rate)


def sync_us_market_caps(
    output_path: Path,
    row_map: dict[tuple[str, str], GlobalPeerFundamentals],
    stock_limit: int,
    tickers: set[str],
    include_ineligible_us: bool,
    request_delay_sec: float,
    checkpoint_every: int,
    workers: int,
) -> tuple[list[GlobalPeerFundamentals], list[dict[str, str]]]:
    stocks = load_us_stock_universe(get_settings().us_stock_universe_path)
    if tickers:
        stocks = [stock for stock in stocks if stock.ticker.upper() in tickers]
    if not include_ineligible_us:
        stocks = [stock for stock in stocks if is_eligible_us_peer(stock)]
    selected = stocks[:stock_limit] if stock_limit else stocks
    pending = [
        stock.ticker.upper()
        for stock in selected
        if row_map.get(("US", stock.ticker.upper())) is None
        or row_map[("US", stock.ticker.upper())].market_cap_usd is None
    ]
    rows: list[GlobalPeerFundamentals] = []
    failures: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(_fetch_us_market_cap_worker, ticker, request_delay_sec): ticker
            for ticker in pending
        }
        for processed, future in enumerate(as_completed(futures), start=1):
            ticker = futures[future]
            try:
                market_cap = future.result()
                if market_cap is not None:
                    key = ("US", ticker)
                    existing = row_map.get(key)
                    if existing:
                        source = _append_source(existing.source, "NASDAQ_SUMMARY_MARKET_CAP")
                        row = replace(existing, market_cap_usd=market_cap, source=source)
                    else:
                        row = GlobalPeerFundamentals(
                            market="US",
                            identifier=ticker,
                            fiscal_year=None,
                            market_cap_usd=market_cap,
                            revenue_usd=None,
                            operating_income_usd=None,
                            net_income_usd=None,
                            currency="USD",
                            source="NASDAQ_SUMMARY_MARKET_CAP",
                        )
                    row_map[key] = row
                    rows.append(row)
            except Exception as exception:
                failures.append(
                    {
                        "market": "US",
                        "identifier": ticker,
                        "reason": str(exception),
                    }
                )
            if processed % checkpoint_every == 0:
                write_global_peer_fundamentals(output_path, list(row_map.values()))
                print(
                    json.dumps(
                        {
                            "phase": "US_MARKET_CAP",
                            "processed": processed,
                            "pending": len(pending),
                            "total_rows": len(row_map),
                            "failures": len(failures),
                            "workers": workers,
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
    write_global_peer_fundamentals(output_path, list(row_map.values()))
    return rows, failures


def _fetch_us_market_cap_worker(ticker: str, request_delay_sec: float) -> float | None:
    if request_delay_sec > 0:
        time.sleep(request_delay_sec)
    return fetch_nasdaq_market_cap_usd(ticker)


def _append_source(existing: str, addition: str) -> str:
    sources = [source for source in existing.split("+") if source]
    if addition not in sources:
        sources.append(addition)
    return "+".join(sources)


def _csv_set(value: str) -> set[str]:
    return {item.strip().upper() for item in value.split(",") if item.strip()}


def _fiscal_year_candidates(fiscal_year: int, lookback: int) -> tuple[int, ...]:
    return tuple(fiscal_year - offset for offset in range(max(0, lookback) + 1))


def _optional_krx_market_caps(base_date: str, krw_usd_rate: float) -> dict[str, float]:
    auth_key = os.environ.get("KRX_OPEN_API_AUTH_KEY", "")
    if not auth_key:
        return {}
    return fetch_krx_market_caps_usd(
        auth_key=auth_key,
        base_date=base_date,
        krw_usd_rate=krw_usd_rate,
    )


def _previous_weekday() -> date:
    candidate = date.today() - timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate


if __name__ == "__main__":
    main()
