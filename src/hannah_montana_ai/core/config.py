from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    model_path: Path = Path("src/hannah_montana_ai/model_store/financial_nlp_ml.joblib")


@lru_cache
def get_settings() -> Settings:
    return Settings()
