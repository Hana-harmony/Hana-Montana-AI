from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.training.global_peer_trainer import sync_us_stock_universe


def main() -> None:
    settings = get_settings()
    entries = sync_us_stock_universe(settings.us_stock_universe_path)
    print(
        "미국 상장 종목 universe "
        f"{len(entries)}개를 저장했습니다: {settings.us_stock_universe_path}"
    )


if __name__ == "__main__":
    main()
