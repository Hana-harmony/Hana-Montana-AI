from __future__ import annotations

import re
from collections import defaultdict
from hashlib import sha256

from hannah_montana_ai.training.k_fnspid.schema import CanonicalDocument

_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
_TOKEN = re.compile(r"[0-9A-Za-z가-힣]+")


def assign_event_clusters(documents: list[CanonicalDocument]) -> dict[str, str]:
    buckets: dict[str, list[CanonicalDocument]] = defaultdict(list)
    for document in documents:
        bucket_key = f"{document.effective_trade_date}:{_fingerprint(document.title)}"
        buckets[bucket_key].append(document)
    assignments: dict[str, str] = {}
    for fingerprint, rows in buckets.items():
        cluster_id = sha256(fingerprint.encode()).hexdigest()
        for row in rows:
            assignments[row.document_id] = cluster_id
    return assignments


def _fingerprint(title: str) -> str:
    normalized = _NUMBER.sub("<NUM>", title.lower())
    tokens = [token for token in _TOKEN.findall(normalized) if len(token) > 1]
    return " ".join(tokens[:18]) or normalized.strip()
