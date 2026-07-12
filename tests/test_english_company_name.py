from hannah_montana_ai.services.english_company_name import resolve_english_company_name


def test_verified_english_name_is_authoritative() -> None:
    assert (
        resolve_english_company_name(
            stock_code="005930", stock_name="삼성전자", stock_name_en="Samsung Electronics"
        )
        == "Samsung Electronics"
    )


def test_missing_english_name_is_transliterated_without_hangul() -> None:
    assert (
        resolve_english_company_name(stock_code="000050", stock_name="경방", stock_name_en="")
        == "Gyeongbang"
    )


def test_korean_placeholder_english_name_does_not_leak_into_peer_copy() -> None:
    assert (
        resolve_english_company_name(
            stock_code="000070", stock_name="삼양홀딩스", stock_name_en="삼양홀딩스"
        )
        == "Samyang Holdings"
    )


def test_known_group_name_is_preserved_when_translating_suffix() -> None:
    assert (
        resolve_english_company_name(stock_code="000000", stock_name="삼성전자", stock_name_en="")
        == "Samsung Electronics"
    )
