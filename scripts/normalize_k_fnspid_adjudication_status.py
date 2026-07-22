from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, cast

FIELDS = frozenset(
    {
        "item_id",
        "final_sentiment",
        "adjudication_note",
        "adjudicator_id",
        "adjudicated_at",
        "adjudication_status",
    }
)
LABELS = frozenset({"POSITIVE", "NEUTRAL", "NEGATIVE"})


def normalize_status(input_path: Path, output_path: Path) -> dict[str, object]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict) or set(value) != FIELDS:
            raise ValueError(f"재정 {line_number}행 스키마가 올바르지 않습니다.")
        row = cast(dict[str, Any], value)
        if (
            row["final_sentiment"] not in LABELS
            or row["adjudication_status"] != "CODEX_ADJUDICATION_APPROVED"
        ):
            raise ValueError(f"재정 {line_number}행 상태를 안전하게 정규화할 수 없습니다.")
        # 병합 계약의 상태 enum만 바꾸고 판정 내용은 그대로 보존한다.
        rows.append({**row, "adjudication_status": "CODEX_ADJUDICATED"})
    if not rows:
        raise ValueError("재정 입력이 비었습니다.")
    encoded = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
    ).encode("utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as file:
            os.chmod(temporary, 0o600)
            file.write(encoded)
            file.flush()
            os.fsync(file.fileno())
        try:
            os.link(temporary, output_path, follow_symlinks=False)
        except FileExistsError as error:
            raise ValueError(f"출력이 이미 존재합니다: {output_path}") from error
    finally:
        temporary.unlink(missing_ok=True)
    return {"row_count": len(rows), "output_path": str(output_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="재정 상태 enum을 병합 계약에 맞춘다.")
    parser.add_argument("--input-path", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(normalize_status(args.input_path, args.output_path), ensure_ascii=False))


if __name__ == "__main__":
    main()
