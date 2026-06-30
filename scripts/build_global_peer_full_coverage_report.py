from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.training.global_peer_quality import (
    build_global_peer_full_coverage_report,
)

if __name__ == "__main__":
    settings = get_settings()
    report = build_global_peer_full_coverage_report(
        stock_universe_path=settings.stock_universe_path,
        model_path=settings.global_peer_model_path,
        report_path=settings.global_peer_full_coverage_report_path,
    )
    print(
        "글로벌 피어 전종목 coverage 완료: "
        f"{report['success_count']}/{report['attempted_count']}개, "
        f"gate={report['quality_gate']['status']}"
    )
