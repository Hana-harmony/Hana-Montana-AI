import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    model_path: Path = Path("src/hannah_montana_ai/model_store/financial_nlp_ml.joblib")
    stock_universe_path: Path = Path("data/reference/korea_stock_universe.csv")
    stock_linker_model_path: Path = Path("src/hannah_montana_ai/model_store/stock_linker_ml.joblib")
    foreign_ownership_quantity_model_path: Path = Path(
        "src/hannah_montana_ai/model_store/foreign_ownership_quantity_ml.joblib"
    )
    foreign_ownership_quantity_training_data_path: Path = Path(
        "data/training/foreign_ownership_quantity_history.csv"
    )
    foreign_ownership_quantity_restricted_codes_path: Path = Path(
        "data/training/foreign_ownership_restricted_stock_codes.csv"
    )
    foreign_ownership_quantity_training_report_path: Path = Path(
        "reports/foreign-ownership-quantity-training-report.json"
    )
    foreign_ownership_quantity_candidate_report_path: Path = Path(
        "reports/foreign-ownership-quantity-training-candidate-report.json"
    )
    foreign_ownership_maintenance_token: str = Field(
        default_factory=lambda: os.getenv("HANNAH_AI_MAINTENANCE_TOKEN", "")
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
