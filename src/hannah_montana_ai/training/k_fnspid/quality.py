from __future__ import annotations

from collections import Counter
from typing import Any

from hannah_montana_ai.training.k_fnspid.schema import (
    CanonicalDocument,
    DocumentEntity,
    MarketImpact,
)


def build_quality_report(
    documents: list[CanonicalDocument],
    entities: list[DocumentEntity],
    impacts: list[MarketImpact],
) -> dict[str, Any]:
    document_ids = {row.document_id for row in documents}
    primary_ids = {row.document_id for row in entities if row.relation == "PRIMARY"}
    primary_entities = [row for row in entities if row.relation == "PRIMARY"]
    impact_ids = {row.document_id for row in impacts if row.materiality_score is not None}
    errors: list[str] = []
    if len(document_ids) != len(documents):
        errors.append("duplicate document_id")
    if any(not row.published_at_kst or not row.effective_trade_date for row in documents):
        errors.append("missing normalized publication date")
    if any(row.document_id not in document_ids for row in entities):
        errors.append("orphan document entity")
    provider_count = Counter(row.provider for row in documents)
    source_type_count = Counter(row.source_type for row in documents)
    full_text_count = Counter(row.source_type for row in documents if row.full_text.strip())
    return {
        "schema_version": "k-fnspid-quality/v1",
        "status": "pass" if not errors else "fail",
        "document_count": len(documents),
        "entity_count": len(entities),
        "impact_count": len(impacts),
        "provider_count": dict(sorted(provider_count.items())),
        "source_type_count": dict(sorted(source_type_count.items())),
        "full_text_source_type_count": dict(sorted(full_text_count.items())),
        "full_text_coverage": {
            source_type: round(full_text_count[source_type] / count, 6)
            for source_type, count in sorted(source_type_count.items())
        },
        "primary_stock_count": len({row.stock_code for row in primary_entities}),
        "primary_market_count": dict(
            sorted(Counter(row.market for row in primary_entities).items())
        ),
        "effective_trade_date_range": {
            "minimum": min((row.effective_trade_date for row in documents), default=""),
            "maximum": max((row.effective_trade_date for row in documents), default=""),
        },
        "primary_entity_coverage": round(len(primary_ids) / len(documents), 6)
        if documents
        else 0.0,
        "market_impact_coverage": round(len(impact_ids) / len(primary_ids), 6)
        if primary_ids
        else 0.0,
        "errors": errors,
    }
