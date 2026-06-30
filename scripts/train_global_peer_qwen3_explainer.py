import argparse
import json
import shutil
import subprocess
from pathlib import Path

from hannah_montana_ai.core.config import get_settings

DEFAULT_MODEL = "mlx-community/Qwen3-0.6B-4bit"
DEFAULT_DATA_DIR = Path("data/training/global_peer_explanation_mlx")
DEFAULT_ADAPTER_DIR = Path("src/hannah_montana_ai/model_store/global_peer_qwen3_explainer_lora")
DEFAULT_REPORT_PATH = Path("reports/global-peer-qwen3-explainer-training.json")


def main() -> None:
    args = _parse_args()
    settings = get_settings()
    source_path = args.source_path or settings.global_peer_explanation_training_path
    data_dir = args.data_dir
    adapter_dir = args.adapter_dir
    report_path = args.report_path

    split_counts = prepare_mlx_chat_dataset(
        source_path=source_path,
        data_dir=data_dir,
        validation_ratio=args.validation_ratio,
        test_ratio=args.test_ratio,
    )
    command = _training_command(
        model=args.model,
        data_dir=data_dir,
        adapter_dir=adapter_dir,
        iters=args.iters,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        num_layers=args.num_layers,
        val_batches=args.val_batches,
        test_batches=args.test_batches,
        steps_per_report=args.steps_per_report,
        steps_per_eval=args.steps_per_eval,
        max_seq_length=args.max_seq_length,
        grad_checkpoint=args.grad_checkpoint,
    )
    training_result: dict[str, object] = {
        "executed": False,
        "return_code": None,
        "command": command,
    }
    if not args.prepare_only:
        executable = shutil.which("mlx_lm.lora")
        if executable is None:
            raise RuntimeError(
                "mlx_lm.lora 실행 파일을 찾을 수 없음. "
                "`uv run --extra llm-training mlx_lm.lora --help`로 의존성을 설치해야 함"
            )
        completed = subprocess.run(command, check=False, text=True)  # noqa: S603
        training_result = {
            "executed": True,
            "return_code": completed.returncode,
            "command": command,
        }
        if completed.returncode != 0:
            raise RuntimeError(f"Qwen3 explainer LoRA training failed: {completed.returncode}")

    report = {
        "schema_version": "global-peer-qwen3-explainer-training/v1",
        "base_model": args.model,
        "training_dataset": str(source_path),
        "mlx_data_dir": str(data_dir),
        "adapter_dir": str(adapter_dir),
        "split_counts": split_counts,
        "training": training_result,
        "serving_note": (
            "운영 t4g.medium에서는 병합/양자화된 GGUF를 llama.cpp OpenAI-compatible "
            "server로 띄우고 HANNAH_GLOBAL_PEER_LLM_ENDPOINT로 연결한다."
        ),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def prepare_mlx_chat_dataset(
    *,
    source_path: Path,
    data_dir: Path,
    validation_ratio: float,
    test_ratio: float,
) -> dict[str, int]:
    rows = [
        json.loads(line)
        for line in source_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) < 100:
        raise ValueError("Qwen3 설명 학습에는 최소 100개 이상의 샘플이 필요함")
    data_dir.mkdir(parents=True, exist_ok=True)
    valid_count = max(1, int(len(rows) * validation_ratio))
    test_count = max(1, int(len(rows) * test_ratio))
    train_count = len(rows) - valid_count - test_count
    if train_count <= 0:
        raise ValueError("train split이 비어 있음")

    splits = {
        "train": rows[:train_count],
        "valid": rows[train_count : train_count + valid_count],
        "test": rows[train_count + valid_count :],
    }
    for split_name, split_rows in splits.items():
        with (data_dir / f"{split_name}.jsonl").open("w", encoding="utf-8") as file:
            for row in split_rows:
                file.write(json.dumps({"messages": row["messages"]}, ensure_ascii=False) + "\n")
    return {split_name: len(split_rows) for split_name, split_rows in splits.items()}


def _training_command(
    *,
    model: str,
    data_dir: Path,
    adapter_dir: Path,
    iters: int,
    batch_size: int,
    learning_rate: float,
    num_layers: int,
    val_batches: int,
    test_batches: int,
    steps_per_report: int,
    steps_per_eval: int,
    max_seq_length: int,
    grad_checkpoint: bool,
) -> list[str]:
    command = [
        "mlx_lm.lora",
        "--model",
        model,
        "--train",
        "--test",
        "--fine-tune-type",
        "lora",
        "--optimizer",
        "adamw",
        "--data",
        str(data_dir),
        "--adapter-path",
        str(adapter_dir),
        "--iters",
        str(iters),
        "--batch-size",
        str(batch_size),
        "--learning-rate",
        str(learning_rate),
        "--num-layers",
        str(num_layers),
        "--val-batches",
        str(val_batches),
        "--test-batches",
        str(test_batches),
        "--steps-per-report",
        str(steps_per_report),
        "--steps-per-eval",
        str(steps_per_eval),
        "--max-seq-length",
        str(max_seq_length),
        "--save-every",
        str(iters),
        "--mask-prompt",
    ]
    if grad_checkpoint:
        command.append("--grad-checkpoint")
    return command


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Qwen3-0.6B peer explanation LoRA with MLX.")
    parser.add_argument("--source-path", type=Path, default=None)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--adapter-dir", type=Path, default=DEFAULT_ADAPTER_DIR)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--iters", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--num-layers", type=int, default=8)
    parser.add_argument("--val-batches", type=int, default=20)
    parser.add_argument("--test-batches", type=int, default=20)
    parser.add_argument("--steps-per-report", type=int, default=10)
    parser.add_argument("--steps-per-eval", type=int, default=50)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--grad-checkpoint", action="store_true", default=True)
    parser.add_argument("--validation-ratio", type=float, default=0.05)
    parser.add_argument("--test-ratio", type=float, default=0.05)
    parser.add_argument("--prepare-only", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
