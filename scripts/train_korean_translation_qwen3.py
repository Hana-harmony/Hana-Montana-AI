import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_MODEL = "mlx-community/Qwen3-0.6B-4bit"
DEFAULT_DATA_DIR = Path("data/training/korean_translation_mlx")
DEFAULT_ADAPTER_DIR = Path("src/hannah_montana_ai/model_store/korean_translation_qwen3_lora")
DEFAULT_REPORT_PATH = Path("reports/korean-translation-qwen3-training.json")


def main() -> None:
    args = parse_args()
    command = [
        "uv",
        "run",
        "--extra",
        "llm-training",
        "mlx_lm.lora",
        "--model",
        args.model,
        "--train",
        "--data",
        str(args.data_dir),
        "--adapter-path",
        str(args.adapter_dir),
        "--iters",
        str(args.iters),
        "--batch-size",
        str(args.batch_size),
        "--learning-rate",
        str(args.learning_rate),
        "--num-layers",
        str(args.num_layers),
        "--val-batches",
        str(args.val_batches),
        "--test-batches",
        str(args.test_batches),
        "--steps-per-report",
        str(args.steps_per_report),
        "--steps-per-eval",
        str(args.steps_per_eval),
        "--max-seq-length",
        str(args.max_seq_length),
        "--grad-checkpoint",
    ]
    result: dict[str, object] = {"executed": False, "return_code": None, "command": command}
    if not args.prepare_only:
        if shutil.which("uv") is None:
            raise RuntimeError("uv executable is required for MLX LoRA training")
        completed = subprocess.run(  # noqa: S603
            command,
            check=False,
            text=True,
            capture_output=True,
        )
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        result = {
            "executed": True,
            "return_code": completed.returncode,
            "command": command,
            **parse_metrics(completed.stdout),
        }
        if completed.returncode != 0:
            raise RuntimeError(
                f"Korean translation Qwen3 LoRA training failed: {completed.returncode}"
            )

    report = {
        "schema_version": "korean-translation-qwen3-training/v1",
        "base_model": args.model,
        "mlx_data_dir": str(args.data_dir),
        "adapter_dir": str(args.adapter_dir),
        "training": result,
        "serving_note": (
            "로컬 Mac은 MLX로 adapter를 직접 로드하고, AWS t4g.medium은 Qwen3-0.6B "
            "GGUF Q4 sidecar를 OpenAI-compatible endpoint로 띄운다."
        ),
    }
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def parse_metrics(stdout: str) -> dict[str, object]:
    metrics: dict[str, object] = {}
    train_losses = [float(match) for match in re.findall(r"Train loss ([0-9.]+)", stdout)]
    val_losses = [float(match) for match in re.findall(r"Val loss ([0-9.]+)", stdout)]
    test_loss = re.search(r"Test loss ([0-9.]+)", stdout)
    test_ppl = re.search(r"Test ppl ([0-9.]+)", stdout)
    if train_losses:
        metrics["final_train_loss"] = train_losses[-1]
    if val_losses:
        metrics["final_val_loss"] = val_losses[-1]
    if test_loss:
        metrics["test_loss"] = float(test_loss.group(1))
    if test_ppl:
        metrics["test_ppl"] = float(test_ppl.group(1))
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--adapter-dir", type=Path, default=DEFAULT_ADAPTER_DIR)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--iters", type=int, default=420)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--num-layers", type=int, default=8)
    parser.add_argument("--val-batches", type=int, default=4)
    parser.add_argument("--test-batches", type=int, default=4)
    parser.add_argument("--steps-per-report", type=int, default=20)
    parser.add_argument("--steps-per-eval", type=int, default=70)
    parser.add_argument("--max-seq-length", type=int, default=1536)
    parser.add_argument("--prepare-only", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
