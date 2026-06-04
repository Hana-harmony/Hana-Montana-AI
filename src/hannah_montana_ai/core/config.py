from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    model_path: Path = Path("src/hannah_montana_ai/model_store/financial_nlp_ml.joblib")
    stock_universe_path: Path = Path("data/reference/korea_stock_universe.csv")
    stock_linker_model_path: Path = Path("src/hannah_montana_ai/model_store/stock_linker_ml.joblib")


@lru_cache
def get_settings() -> Settings:
    return Settings()
