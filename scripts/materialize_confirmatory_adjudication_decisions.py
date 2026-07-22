from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

LABELS = frozenset({"POSITIVE", "NEUTRAL", "NEGATIVE", "UNRESOLVED"})

NEWS_LABELS = """
POSITIVE POSITIVE POSITIVE NEUTRAL NEGATIVE POSITIVE POSITIVE POSITIVE NEUTRAL POSITIVE
NEUTRAL POSITIVE POSITIVE NEUTRAL NEGATIVE NEGATIVE POSITIVE POSITIVE NEGATIVE NEGATIVE
NEGATIVE POSITIVE NEGATIVE POSITIVE POSITIVE POSITIVE NEGATIVE NEGATIVE NEUTRAL POSITIVE
POSITIVE POSITIVE POSITIVE POSITIVE POSITIVE POSITIVE POSITIVE NEGATIVE POSITIVE NEUTRAL
POSITIVE NEGATIVE POSITIVE POSITIVE NEGATIVE POSITIVE POSITIVE NEUTRAL NEGATIVE NEUTRAL
NEUTRAL POSITIVE NEGATIVE NEUTRAL POSITIVE POSITIVE NEGATIVE POSITIVE POSITIVE POSITIVE
POSITIVE POSITIVE NEGATIVE POSITIVE NEUTRAL NEUTRAL POSITIVE POSITIVE NEGATIVE POSITIVE
NEUTRAL POSITIVE NEGATIVE POSITIVE NEGATIVE NEUTRAL NEUTRAL POSITIVE NEGATIVE POSITIVE
POSITIVE NEGATIVE POSITIVE NEGATIVE NEUTRAL POSITIVE NEGATIVE POSITIVE POSITIVE NEGATIVE
NEUTRAL POSITIVE NEGATIVE POSITIVE NEGATIVE POSITIVE POSITIVE NEGATIVE NEUTRAL POSITIVE
NEUTRAL POSITIVE NEUTRAL NEUTRAL POSITIVE NEGATIVE POSITIVE NEUTRAL
""".split()

DISCLOSURE_LABELS = """
NEGATIVE NEGATIVE NEGATIVE POSITIVE NEGATIVE NEGATIVE POSITIVE POSITIVE NEUTRAL NEUTRAL
NEGATIVE NEGATIVE NEGATIVE NEGATIVE POSITIVE POSITIVE POSITIVE NEGATIVE POSITIVE POSITIVE
NEGATIVE POSITIVE POSITIVE NEGATIVE NEGATIVE NEUTRAL NEUTRAL POSITIVE NEGATIVE NEGATIVE
POSITIVE NEUTRAL POSITIVE POSITIVE NEUTRAL NEGATIVE NEGATIVE NEGATIVE NEGATIVE POSITIVE
""".split()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"조정 패킷이 없거나 symlink입니다: {path}")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if not rows or not all(isinstance(row, dict) for row in rows):
        raise ValueError("조정 패킷이 비었거나 JSON 객체가 아닙니다.")
    return rows


def _note(source_record: dict[str, Any], label: str) -> str:
    title = " ".join(str(source_record.get("title", "")).split())
    if label == "POSITIVE":
        return f"확정 개선·기회 또는 위험 해소 근거를 우선 판정: {title}"
    if label == "NEGATIVE":
        return f"확정 악화·손실 또는 법적·존속 위험 근거를 우선 판정: {title}"
    if label == "UNRESOLVED":
        return f"입력만으로 방향을 책임 있게 확정할 수 없어 제외: {title}"
    return f"대상 직접성·확정성 또는 혼합 방향이 부족해 중립 판정: {title}"


def _write_exclusive(path: Path, rows: list[dict[str, Any]]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError(f"출력이 이미 존재합니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            for row in rows:
                file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o600)
        os.link(temporary, path, follow_symlinks=False)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="봉인 평가 불일치 조정 결정을 원자적으로 기록한다."
    )
    parser.add_argument("--source", choices=("NEWS", "DISCLOSURE"), required=True)
    parser.add_argument("--packet-path", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    args = parser.parse_args()

    packet = _read_jsonl(args.packet_path)
    labels = NEWS_LABELS if args.source == "NEWS" else DISCLOSURE_LABELS
    if len(labels) != len(packet) or any(label not in LABELS for label in labels):
        raise ValueError("조정 라벨 수 또는 값이 패킷과 일치하지 않습니다.")
    if len({str(row.get("item_id", "")) for row in packet}) != len(packet):
        raise ValueError("조정 패킷 item_id가 비었거나 중복됩니다.")

    adjudicated_at = datetime.now(UTC).isoformat()
    decisions = [
        {
            "item_id": row["item_id"],
            "final_sentiment": label,
            "adjudication_note": _note(row["source_record"], label),
            "adjudicator_id": "codex-confirmatory-adjudicator-1",
            "adjudicated_at": adjudicated_at,
            "adjudication_status": (
                "UNRESOLVED" if label == "UNRESOLVED" else "CODEX_ADJUDICATED"
            ),
        }
        for row, label in zip(packet, labels, strict=True)
    ]
    _write_exclusive(args.output_path, decisions)
    print(json.dumps({"source": args.source, "count": len(decisions)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
