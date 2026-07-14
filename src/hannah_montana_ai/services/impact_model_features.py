from __future__ import annotations

IMPACT_INPUT_FEATURE_VERSION = "k-fnspid-text-v2"


def build_impact_model_text(text: str, source_type: str) -> str:
    normalized_source = source_type.strip().upper()
    if normalized_source not in {"NEWS", "DISCLOSURE"}:
        normalized_source = "UNKNOWN"
    return f"[SOURCE={normalized_source}] {text.strip()}".strip()
