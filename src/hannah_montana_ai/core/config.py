import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


def _optional_path_env(name: str) -> Path | None:
    value = os.getenv(name, "").strip()
    return Path(value) if value else None


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_path: Path = Path("src/hannah_montana_ai/model_store/financial_nlp_ml.joblib")
    market_impact_news_model_path: Path = Path(
        "src/hannah_montana_ai/model_store/k_fnspid_impact_news_ml.joblib"
    )
    market_impact_news_training_report_path: Path = Path(
        "reports/k-fnspid-impact-news-training-report.json"
    )
    market_impact_disclosure_model_path: Path = Path(
        "src/hannah_montana_ai/model_store/k_fnspid_impact_disclosure_ml.joblib"
    )
    market_impact_disclosure_training_report_path: Path = Path(
        "reports/k-fnspid-impact-disclosure-training-report.json"
    )
    transformer_base_model_path: Path = Field(
        default_factory=lambda: Path(
            os.getenv(
                "HANNAH_SENTIMENT_BASE_MODEL_PATH",
                "/app/models/kf-deberta-base",
            )
        )
    )
    sentiment_transformer_path: Path = Path(
        "src/hannah_montana_ai/model_store/kf_deberta_sentiment"
    )
    sentiment_transformer_training_report_path: Path = Path(
        "reports/kf-deberta-sentiment-training-report.json"
    )
    sentiment_transformer_benchmark_report_path: Path = Path(
        "reports/korean-finance-sentiment-benchmark.json"
    )
    sentiment_release_current_path: Path = Field(
        default_factory=lambda: Path(
            os.getenv(
                "HANNAH_SENTIMENT_RELEASE_CURRENT_PATH",
                "releases/sentiment/current.json",
            )
        )
    )
    sentiment_release_project_root: Path = Field(
        default_factory=lambda: Path(os.getenv("HANNAH_PROJECT_ROOT", "."))
    )
    sentiment_release_attestation_mode: str = Field(
        default_factory=lambda: os.getenv(
            "HANNAH_SENTIMENT_RELEASE_ATTESTATION_MODE",
            "local-untrusted",
        )
    )
    sentiment_release_public_key_path: Path | None = Field(
        default_factory=lambda: _optional_path_env(
            "HANNAH_SENTIMENT_RELEASE_PUBLIC_KEY_PATH"
        )
    )
    sentiment_release_signer_key_id: str = Field(
        default_factory=lambda: os.getenv("HANNAH_SENTIMENT_RELEASE_SIGNER_KEY_ID", "")
    )
    sentiment_release_expected_id: str = Field(
        default_factory=lambda: os.getenv("HANNAH_SENTIMENT_RELEASE_EXPECTED_ID", "")
    )
    sentiment_release_expected_git_commit: str = Field(
        default_factory=lambda: os.getenv(
            "HANNAH_SENTIMENT_RELEASE_EXPECTED_GIT_COMMIT",
            "",
        )
    )
    sentiment_stacker_path: Path = Path(
        "src/hannah_montana_ai/model_store/sentiment_stacker.joblib"
    )
    sentiment_stacker_report_path: Path = Path("reports/sentiment-stacker-training-report.json")
    disclosure_importance_model_path: Path = Path(
        "src/hannah_montana_ai/model_store/disclosure_importance_ml.joblib"
    )
    disclosure_importance_report_path: Path = Path(
        "reports/disclosure-importance-training-report.json"
    )
    market_impact_news_transformer_path: Path = Path(
        "src/hannah_montana_ai/model_store/k_fnspid_impact_news_transformer"
    )
    market_impact_news_transformer_report_path: Path = Path(
        "reports/k-fnspid-impact-news-transformer-training-report.json"
    )
    market_impact_disclosure_transformer_path: Path = Path(
        "src/hannah_montana_ai/model_store/k_fnspid_impact_disclosure_transformer"
    )
    market_impact_disclosure_transformer_report_path: Path = Path(
        "reports/k-fnspid-impact-disclosure-transformer-training-report.json"
    )
    stock_universe_path: Path = Path("data/reference/korea_stock_universe.csv")
    stock_linker_model_path: Path = Path("src/hannah_montana_ai/model_store/stock_linker_ml.joblib")
    global_peer_model_path: Path = Path("src/hannah_montana_ai/model_store/global_peer_ml.joblib")
    us_stock_universe_path: Path = Path("data/reference/us_stock_universe.csv")
    global_peer_fundamentals_path: Path = Path("data/reference/global_peer_fundamentals.csv")
    global_peer_korea_industry_path: Path = Path("data/reference/korea_stock_industries.csv")
    global_peer_korea_company_profile_path: Path = Path("data/reference/korea_company_profiles.csv")
    global_peer_training_report_path: Path = Path("reports/global-peer-training-report.json")
    global_peer_ai_smoke_report_path: Path = Path("reports/global-peer-ai-smoke-report.json")
    global_peer_full_coverage_report_path: Path = Path(
        "reports/global-peer-full-coverage-report.json"
    )
    global_peer_all_results_report_path: Path = Path("reports/global-peer-all-results.json")
    global_peer_all_results_csv_path: Path = Path("reports/global-peer-all-results.csv")
    global_peer_all_results_doc_path: Path = Path("docs/GLOBAL_PEER_ALL_RESULTS.md")
    korean_financial_terms_seed_path: Path = Path("data/reference/korean_financial_terms_seed.json")
    korean_financial_term_model_version: str = "k-finance-term-dictionary-v3"
    korean_translation_llm_endpoint: str = Field(
        default_factory=lambda: os.getenv(
            "HANNAH_KOREAN_TRANSLATION_LLM_ENDPOINT",
            "http://127.0.0.1:18081",
        )
    )
    korean_translation_llm_timeout_seconds: float = Field(
        default_factory=lambda: float(
            os.getenv("HANNAH_KOREAN_TRANSLATION_LLM_TIMEOUT_SECONDS", "300.0")
        )
    )
    korean_translation_llm_max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("HANNAH_KOREAN_TRANSLATION_LLM_MAX_TOKENS", "2048"))
    )
    korean_translation_max_concurrency: int = Field(
        default_factory=lambda: int(os.getenv("HANNAH_KOREAN_TRANSLATION_MAX_CONCURRENCY", "1")),
        ge=1,
        le=8,
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
    runtime_environment: str = Field(
        default_factory=lambda: os.getenv("HANNAH_RUNTIME_ENVIRONMENT", "local")
    )
    discord_webhook_url: str = Field(
        default_factory=lambda: os.getenv("HANNAH_DISCORD_WEBHOOK_URL", "")
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
