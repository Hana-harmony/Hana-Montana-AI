import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.training.global_peer_trainer import (
    GENERIC_LISTED_SECTOR,
    KoreaIndustryProfile,
    fetch_naver_korea_industry_profile,
    load_korea_industry_profiles,
    write_korea_industry_profiles,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry, load_stock_universe


def sync_korea_stock_industries(
    workers: int = 8,
    request_delay_sec: float = 0.03,
    checkpoint_every: int = 200,
) -> dict[str, object]:
    settings = get_settings()
    stocks = load_stock_universe(settings.stock_universe_path)
    existing = load_korea_industry_profiles(settings.global_peer_korea_industry_path)
    rows = dict(existing)
    pending = [stock for stock in stocks if stock.stock_code not in rows]
    failures: list[dict[str, str]] = []

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(_fetch_profile_worker, stock, request_delay_sec): stock
            for stock in pending
        }
        for processed, future in enumerate(as_completed(futures), start=1):
            stock = futures[future]
            try:
                profile = future.result()
                if profile:
                    rows[profile.stock_code] = profile
            except Exception as exception:
                failures.append(
                    {
                        "stock_code": stock.stock_code,
                        "stock_name": stock.stock_name,
                        "reason": str(exception),
                    }
                )
            if processed % checkpoint_every == 0:
                write_korea_industry_profiles(
                    settings.global_peer_korea_industry_path,
                    list(rows.values()),
                )
                print(
                    json.dumps(
                        {
                            "processed": processed,
                            "pending": len(pending),
                            "row_count": len(rows),
                            "failures": len(failures),
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )

    write_korea_industry_profiles(settings.global_peer_korea_industry_path, list(rows.values()))
    specific_count = sum(1 for row in rows.values() if row.sector != GENERIC_LISTED_SECTOR)
    report = {
        "schema_version": "global-peer-korea-industry-sync/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "source": "NAVER_STOCK_INDUSTRY_COMPARE",
        "stock_universe_count": len(stocks),
        "existing_count_before_sync": len(existing),
        "attempted_count": len(pending),
        "profile_count": len(rows),
        "specific_profile_count": specific_count,
        "generic_profile_count": len(rows) - specific_count,
        "failure_count": len(failures),
        "failures": failures[:100],
    }
    settings.global_peer_korea_industry_sync_report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.global_peer_korea_industry_sync_report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    return report


def _fetch_profile_worker(
    stock: StockUniverseEntry,
    request_delay_sec: float,
) -> KoreaIndustryProfile | None:
    if request_delay_sec > 0:
        time.sleep(request_delay_sec)
    return fetch_naver_korea_industry_profile(stock)


if __name__ == "__main__":
    result = sync_korea_stock_industries()
    print(
        "국내 업종 profile 동기화 완료: "
        f"{result['profile_count']}/{result['stock_universe_count']}개, "
        f"specific={result['specific_profile_count']}, "
        f"failures={result['failure_count']}"
    )
