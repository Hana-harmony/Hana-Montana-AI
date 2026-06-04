import json
from pathlib import Path

import pytest

from hannah_montana_ai.services.stock_linker import (
    MachineLearningStockLinker,
    StockLinkerModelArtifactInvalidError,
    StockLinkerModelArtifactNotFoundError,
)
from hannah_montana_ai.training.stock_linker_trainer import (
    build_stock_linker_training_rows,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry


def test_stock_linker_training_rows_cover_code_and_trainable_names() -> None:
    rows = build_stock_linker_training_rows(
        [
            StockUniverseEntry("005930", "삼성전자"),
            StockUniverseEntry("003600", "SK"),
        ]
    )

    assert [row.stock_code for row in rows] == ["003600", "005930", "005930"]
    assert {row.source for row in rows} == {"stock_code", "stock_name"}


def test_stock_linker_report_covers_entire_stock_universe() -> None:
    report = json.loads(Path("reports/stock-linker-training-report.json").read_text())

    assert report["coverage_gate"]["status"] == "pass"
    assert report["universe_count"] >= 3_000
    assert report["training_stock_count"] == report["universe_count"]
    assert report["evaluation"]["all_stock_code_template_accuracy"] == 1.0
    assert report["evaluation"]["trainable_stock_name_template_accuracy"] >= 0.99


def test_stock_linker_predicts_stock_code_from_leading_name_and_code() -> None:
    linker = MachineLearningStockLinker(
        Path("src/hannah_montana_ai/model_store/stock_linker_ml.joblib")
    )

    assert linker.predict_stock_code("삼성전자 2분기 영업이익 증가") == "005930"
    assert linker.predict_stock_code("005930 주요사항보고서 공시") == "005930"
    assert linker.predict_stock_code("모바일어플라이언스, 경영 안정성 흔들") == "087260"
    assert linker.predict_stock_code("한국 증시 고환율과 금리 변동성 확대") is None


def test_stock_linker_model_artifact_validation(tmp_path: Path) -> None:
    with pytest.raises(StockLinkerModelArtifactNotFoundError):
        MachineLearningStockLinker(tmp_path / "missing.joblib")

    invalid_path = tmp_path / "invalid.joblib"
    invalid_path.write_bytes(b"not-a-joblib")

    with pytest.raises(StockLinkerModelArtifactInvalidError):
        MachineLearningStockLinker(invalid_path)
