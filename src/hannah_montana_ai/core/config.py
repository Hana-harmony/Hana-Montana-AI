import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    model_path: Path = Path("src/hannah_montana_ai/model_store/financial_nlp_ml.joblib")
    stock_universe_path: Path = Path("data/reference/korea_stock_universe.csv")
    stock_linker_model_path: Path = Path("src/hannah_montana_ai/model_store/stock_linker_ml.joblib")
    global_peer_model_path: Path = Path("src/hannah_montana_ai/model_store/global_peer_ml.joblib")
    us_stock_universe_path: Path = Path("data/reference/us_stock_universe.csv")
    global_peer_fundamentals_path: Path = Path("data/reference/global_peer_fundamentals.csv")
    global_peer_korea_industry_path: Path = Path(
        "data/reference/korea_stock_industries.csv"
    )
    global_peer_korea_company_profile_path: Path = Path(
        "data/reference/korea_company_profiles.csv"
    )
    global_peer_training_report_path: Path = Path("reports/global-peer-training-report.json")
    global_peer_ai_smoke_report_path: Path = Path("reports/global-peer-ai-smoke-report.json")
    global_peer_full_coverage_report_path: Path = Path(
        "reports/global-peer-full-coverage-report.json"
    )
    global_peer_all_results_report_path: Path = Path(
        "reports/global-peer-all-results.json"
    )
    global_peer_all_results_csv_path: Path = Path(
        "reports/global-peer-all-results.csv"
    )
    global_peer_all_results_doc_path: Path = Path(
        "docs/GLOBAL_PEER_ALL_RESULTS.md"
    )
    global_peer_explanation_training_path: Path = Path(
        "data/training/global_peer_explanation_sft.jsonl"
    )
    global_peer_explanation_readiness_report_path: Path = Path(
        "reports/global-peer-explanation-llm-readiness.json"
    )
    global_peer_explanation_mode: str = Field(
        default_factory=lambda: os.getenv("HANNAH_GLOBAL_PEER_EXPLANATION_MODE", "template")
    )
    global_peer_explanation_llm_endpoint: str = Field(
        default_factory=lambda: os.getenv("HANNAH_GLOBAL_PEER_LLM_ENDPOINT", "")
    )
    global_peer_explanation_llm_model: str = Field(
        default_factory=lambda: os.getenv("HANNAH_GLOBAL_PEER_LLM_MODEL", "Qwen3-0.6B-GGUF-Q4")
    )
    global_peer_explanation_llm_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("HANNAH_GLOBAL_PEER_LLM_TIMEOUT_SECONDS", "2.5"))
    )
    global_peer_explanation_llm_max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("HANNAH_GLOBAL_PEER_LLM_MAX_TOKENS", "220"))
    )
    global_peer_korea_industry_sync_report_path: Path = Path(
        "reports/global-peer-korea-industry-sync-report.json"
    )
    global_peer_korea_company_profile_sync_report_path: Path = Path(
        "reports/global-peer-korea-company-profile-sync-report.json"
    )
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
