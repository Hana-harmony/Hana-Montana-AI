from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.training.global_peer_trainer import (
    KoreaCompanyProfile,
    fetch_open_dart_company_profile,
    fetch_wise_report_business_summary,
    load_korea_company_profiles,
    write_korea_company_profiles,
)
from hannah_montana_ai.training.stock_universe import load_env_file, load_stock_universe

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=get_settings().global_peer_korea_company_profile_path,
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=get_settings().global_peer_korea_company_profile_sync_report_path,
    )
    parser.add_argument("--env-file", type=Path, default=PROJECT_ROOT / "secrets.local.env")
    parser.add_argument("--stock-limit", type=int, default=0)
    parser.add_argument("--stock-codes", default="")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--request-delay-sec", type=float, default=0.03)
    parser.add_argument("--checkpoint-every", type=int, default=200)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--skip-open-dart-company", action="store_true")
    parser.add_argument("--refresh-summaries", action="store_true")
    args = parser.parse_args()

    load_env_file(args.env_file)
    api_key = os.environ.get("OPEN_DART_API_KEY", "")
    if not api_key and not args.skip_open_dart_company:
        raise RuntimeError("OPEN_DART_API_KEY is required in gitignored local env")

    existing = {} if args.refresh else load_korea_company_profiles(args.output)
    stocks = load_stock_universe(get_settings().stock_universe_path)
    requested_codes = _csv_set(args.stock_codes)
    if requested_codes:
        stocks = [stock for stock in stocks if stock.stock_code in requested_codes]
    selected = stocks[: args.stock_limit] if args.stock_limit else stocks
    missing = (
        []
        if args.skip_open_dart_company
        else [
            stock
            for stock in selected
            if stock.dart_corp_code and (args.refresh or stock.stock_code not in existing)
        ]
    )
    summary_targets = [
        stock
        for stock in selected
        if args.refresh_summaries
        or stock.stock_code not in existing
        or not existing[stock.stock_code].business_summary_text
    ]

    failures: list[dict[str, str]] = []
    fetched: list[KoreaCompanyProfile] = []
    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(fetch_open_dart_company_profile, api_key, stock): stock
                for stock in missing
            }
            for index, future in enumerate(as_completed(futures), start=1):
                stock = futures[future]
                try:
                    profile = future.result()
                    if profile:
                        existing[profile.stock_code] = profile
                        fetched.append(profile)
                except Exception as exception:
                    failures.append({"stock_code": stock.stock_code, "reason": str(exception)})
                if index % args.checkpoint_every == 0:
                    _checkpoint(args.output, existing, index, len(missing), failures)
                time.sleep(args.request_delay_sec)
    else:
        for index, stock in enumerate(missing, start=1):
            try:
                profile = fetch_open_dart_company_profile(api_key, stock)
                if profile:
                    existing[profile.stock_code] = profile
                    fetched.append(profile)
            except Exception as exception:
                failures.append({"stock_code": stock.stock_code, "reason": str(exception)})
            if index % args.checkpoint_every == 0:
                _checkpoint(args.output, existing, index, len(missing), failures)
            time.sleep(args.request_delay_sec)

    summary_updates, summary_failures = sync_wise_report_summaries(
        stocks=summary_targets,
        profiles=existing,
        workers=args.workers,
        request_delay_sec=args.request_delay_sec,
        checkpoint_every=args.checkpoint_every,
        output_path=args.output,
    )
    failures.extend(summary_failures)

    write_korea_company_profiles(args.output, list(existing.values()))
    report = {
        "schema_version": "global-peer-korea-company-profile-sync/v1",
        "output_path": str(args.output),
        "selected_stock_count": len(selected),
        "existing_before_count": len(existing) - len(fetched),
        "missing_before_count": len(missing),
        "new_or_refreshed_count": len(fetched),
        "summary_target_count": len(summary_targets),
        "summary_update_count": summary_updates,
        "row_count": len(existing),
        "failure_count": len(failures),
        "failures_sample": failures[:30],
        "credential_policy": "OPEN_DART_API_KEY is loaded from gitignored local env only",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def sync_wise_report_summaries(
    *,
    stocks: list,
    profiles: dict[str, KoreaCompanyProfile],
    workers: int,
    request_delay_sec: float,
    checkpoint_every: int,
    output_path: Path,
) -> tuple[int, list[dict[str, str]]]:
    if not stocks:
        return 0, []
    failures: list[dict[str, str]] = []
    updated = 0
    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(fetch_wise_report_business_summary, stock.stock_code): stock
                for stock in stocks
            }
            for index, future in enumerate(as_completed(futures), start=1):
                stock = futures[future]
                try:
                    summary = future.result()
                    if summary:
                        profiles[stock.stock_code] = _merge_company_summary(
                            stock=stock,
                            profile=profiles.get(stock.stock_code),
                            summary=summary,
                        )
                        updated += 1
                except Exception as exception:
                    failures.append({"stock_code": stock.stock_code, "reason": str(exception)})
                if index % checkpoint_every == 0:
                    _checkpoint(output_path, profiles, index, len(stocks), failures)
                time.sleep(request_delay_sec)
        return updated, failures

    for index, stock in enumerate(stocks, start=1):
        try:
            summary = fetch_wise_report_business_summary(stock.stock_code)
            if summary:
                profiles[stock.stock_code] = _merge_company_summary(
                    stock=stock,
                    profile=profiles.get(stock.stock_code),
                    summary=summary,
                )
                updated += 1
        except Exception as exception:
            failures.append({"stock_code": stock.stock_code, "reason": str(exception)})
        if index % checkpoint_every == 0:
            _checkpoint(output_path, profiles, index, len(stocks), failures)
        time.sleep(request_delay_sec)
    return updated, failures


def _merge_company_summary(
    *,
    stock,
    profile: KoreaCompanyProfile | None,
    summary: str,
) -> KoreaCompanyProfile:
    if profile:
        source = profile.source or "OPEN_DART_COMPANY"
        if "WISE_REPORT_BUSINESS_SUMMARY" not in source:
            source = f"{source}+WISE_REPORT_BUSINESS_SUMMARY"
        return replace(profile, business_summary_text=summary, source=source)
    return KoreaCompanyProfile(
        stock_code=stock.stock_code,
        corp_code=stock.dart_corp_code,
        corp_name=stock.stock_name,
        corp_name_eng=stock.stock_name_en,
        stock_name=stock.stock_name,
        corp_cls="",
        induty_code="",
        est_dt="",
        acc_mt="",
        business_summary_text=summary,
        source="WISE_REPORT_BUSINESS_SUMMARY",
    )


def _checkpoint(
    output_path: Path,
    profiles: dict[str, KoreaCompanyProfile],
    processed: int,
    total: int,
    failures: list[dict[str, str]],
) -> None:
    write_korea_company_profiles(output_path, list(profiles.values()))
    print(
        json.dumps(
            {
                "phase": "KR_COMPANY_PROFILE",
                "processed": processed,
                "selected": total,
                "total_rows": len(profiles),
                "failures": len(failures),
            },
            ensure_ascii=False,
        )
    )


def _csv_set(value: str) -> set[str]:
    return {item.strip().upper() for item in value.split(",") if item.strip()}


if __name__ == "__main__":
    main()
