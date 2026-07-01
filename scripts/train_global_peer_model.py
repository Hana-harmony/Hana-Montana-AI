from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.training.global_peer_trainer import train_global_peer_model


def main() -> None:
    settings = get_settings()
    result = train_global_peer_model(
        korea_stock_universe_path=settings.stock_universe_path,
        us_stock_universe_path=settings.us_stock_universe_path,
        fundamentals_path=settings.global_peer_fundamentals_path,
        model_path=settings.global_peer_model_path,
        report_path=settings.global_peer_training_report_path,
        korea_industry_path=settings.global_peer_korea_industry_path,
        korea_company_profile_path=settings.global_peer_korea_company_profile_path,
    )
    print(
        "글로벌 피어 모델 학습 완료: "
        f"{result.report['korea_universe_count']}개 한국 종목, "
        f"{result.report['us_universe_count']}개 미국 종목"
    )


if __name__ == "__main__":
    main()
