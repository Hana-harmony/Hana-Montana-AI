from hannah_montana_ai.training.stock_universe import (
    StockUniverseEntry,
    merge_stock_universe_metadata,
    parse_kis_stock_master,
)


def _line(code: str, isin: str, name: str, tail_width: int, group: str) -> str:
    tail = f"{group}{'N' * tail_width}"[:tail_width]
    return f"{code:<9}{isin}{name}{tail}"


def test_kis_master_keeps_only_six_digit_equities() -> None:
    tail_width = 228
    content = "\n".join(
        [
            _line("005930", "KR7005930003", "삼성전자", tail_width, " ST"),
            _line("069500", "KR7069500007", "KODEX 200", tail_width, " EF"),
            _line("F70100026", "KR5701000261", "한투글로벌", tail_width, " BC"),
        ]
    )

    stocks = parse_kis_stock_master(content, market="KOSPI", tail_width=tail_width)

    assert stocks == [
        StockUniverseEntry(stock_code="005930", stock_name="삼성전자", market="KOSPI")
    ]


def test_active_kis_row_keeps_dart_metadata_and_rename_alias() -> None:
    active = [StockUniverseEntry("123456", "신규상호", market="KOSDAQ")]
    metadata = [
        StockUniverseEntry(
            "123456",
            "기존상호",
            stock_name_en="Existing Corp",
            dart_corp_code="00123456",
        )
    ]

    assert merge_stock_universe_metadata(active, [metadata]) == [
        StockUniverseEntry(
            "123456",
            "신규상호",
            stock_name_en="Existing Corp",
            market="KOSDAQ",
            dart_corp_code="00123456",
            aliases=("기존상호",),
        )
    ]
