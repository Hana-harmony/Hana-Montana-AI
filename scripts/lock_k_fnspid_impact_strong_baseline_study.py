from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

try:
    from scripts.train_k_fnspid_transformer import LABEL_ORDER, MODEL_PRESETS
except ModuleNotFoundError:  # 직접 실행 시 scripts 디렉터리에서 import한다.
    from train_k_fnspid_transformer import LABEL_ORDER, MODEL_PRESETS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "reports/k-fnspid-impact-strong-baseline-study-contract.json"
)
DATASET_MANIFEST = PROJECT_ROOT / "data/k_fnspid/v4/manifest.json"
CANDIDATE_NEWS_REPORT = (
    PROJECT_ROOT / "reports/k-fnspid-impact-news-transformer-training-report.json"
)
CANDIDATE_DISCLOSURE_AGGREGATE = (
    PROJECT_ROOT / "reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json"
)
CODE_PATHS = (
    PROJECT_ROOT / "scripts/lock_k_fnspid_impact_strong_baseline_study.py",
    PROJECT_ROOT / "scripts/train_k_fnspid_transformer.py",
    PROJECT_ROOT / "scripts/aggregate_k_fnspid_runs.py",
    PROJECT_ROOT / "scripts/verify_k_fnspid_impact_baseline_artifact.py",
    PROJECT_ROOT / "scripts/evaluate_k_fnspid_impact_strong_baselines.py",
    PROJECT_ROOT / "scripts/run_impact_strong_baseline_study.sh",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="중요도 강한 공개 비교군 연구 계약을 결과 생성 전에 잠근다."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    contract = build_contract()
    output = _project_path(args.output)
    encoded = json.dumps(contract, ensure_ascii=False, indent=2) + "\n"
    if output.exists():
        if output.read_text(encoding="utf-8") != encoded:
            raise SystemExit("기존 중요도 연구 계약과 현재 입력·코드 계약이 다릅니다.")
        print(json.dumps({"status": "REUSED_EXACT_CONTRACT", **_manifest(output)}))
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(encoded, encoding="utf-8")
    print(json.dumps({"status": "LOCKED_NEW_CONTRACT", **_manifest(output)}))


def build_contract() -> dict[str, Any]:
    news_report = json.loads(CANDIDATE_NEWS_REPORT.read_text(encoding="utf-8"))
    news_predictions = _project_path(Path(news_report["test_predictions"]["path"]))
    news_adapter = _project_path(
        Path(news_report["training_hyperparameters"]["lora"]["initial_adapter_path"])
    )
    disclosure_aggregate = json.loads(
        CANDIDATE_DISCLOSURE_AGGREGATE.read_text(encoding="utf-8")
    )
    disclosure_predictions = _project_path(
        Path(disclosure_aggregate["selected_predictions_path"])
    )
    disclosure_adapter = _project_path(
        Path(disclosure_aggregate["selected_artifact_dir"])
    )
    candidates = {
        "NEWS": {
            "evaluation_report": _manifest(CANDIDATE_NEWS_REPORT),
            "frozen_shared_adapter_seed": 42,
            "evaluation_seed": int(news_report["seed"]),
            "frozen_shared_adapter": _directory_manifest(news_adapter),
            "selected_predictions": _manifest(news_predictions),
        },
        "DISCLOSURE": {
            "aggregate": _manifest(CANDIDATE_DISCLOSURE_AGGREGATE),
            "initial_shared_adapter_seed": 42,
            "selected_seed_by_validation": int(
                disclosure_aggregate["selected_seed_by_validation"]
            ),
            "selected_artifact": _directory_manifest(disclosure_adapter),
            "selected_predictions": _manifest(disclosure_predictions),
        },
    }
    models = {}
    for preset_name in ("KR_FINBERT_SC", "KLUE_ROBERTA_LARGE"):
        preset = MODEL_PRESETS[preset_name]
        models[preset_name] = {
            "base_model": preset.model_id,
            "revision": preset.revision,
            "model_safetensors_sha256": preset.model_safetensors_sha256,
            "comparison_only": preset.comparison_only,
            "safe_serialization_only": True,
            "trust_remote_code": False,
        }
    return {
        "schema_version": "k-fnspid-impact-strong-baseline-study-contract/v1",
        "state": "LOCKED_BEFORE_STRONG_BASELINE_TRAINING",
        "claim_scope": (
            "same K-FNSPID temporal Test and named public strong baselines; "
            "not a global SOTA leaderboard"
        ),
        "task": {
            "name": "market-impact ordinal four-class classification",
            "label_order": list(LABEL_ORDER),
            "sources": ["NEWS", "DISCLOSURE"],
            "dataset_manifest": _manifest(DATASET_MANIFEST),
            "test_role": "final paired evaluation only",
            "seed_selection": (
                "NEWS reuses fixed shared seed 42 to mirror the candidate; "
                "DISCLOSURE selects its fine-tuning seed by validation macro F1 only"
            ),
            "pipeline": [
                "train shared NEWS+DISCLOSURE market-impact adapters for seeds 17/42/73",
                "evaluate frozen shared seed 42 adapter on NEWS",
                "fine-tune DISCLOSURE seeds 17/42/73 from shared seed 42 adapter",
            ],
        },
        "candidate": {
            "name": "Hana Montana AI(KF-DeBERTa + K-FNSPID)",
            "frozen_existing_runs": candidates,
        },
        "public_strong_baselines": models,
        "seeds": [17, 42, 73],
        "recipes": {
            "SHARED": {
                "max_length": 256,
                "epochs": 3,
                "effective_batch_size": 32,
                "learning_rate": 0.0002,
                "focal_gamma": 1.5,
                "ordinal_loss_weight": 0.30,
                "label_smoothing": 0.02,
            },
            "NEWS_EVALUATION": {
                "source": "NEWS",
                "evaluation_only": True,
                "initialization": "same-preset shared seed 42 adapter",
                "evaluation_seed": 73,
                "max_length": 256,
                "effective_batch_size": 64,
                "learning_rate": 0.0002,
                "focal_gamma": 1.5,
                "ordinal_loss_weight": 0.30,
                "label_smoothing": 0.02,
            },
            "DISCLOSURE": {
                "max_length": 128,
                "epochs": 1,
                "effective_batch_size": 32,
                "learning_rate": 0.00005,
                "focal_gamma": 1.0,
                "ordinal_loss_weight": 0.20,
                "label_smoothing": 0.01,
                "initialization": "same-preset shared seed 42 adapter",
            },
        },
        "statistics": {
            "primary_metric": "Macro-F1",
            "ordinal_metric": "quadratic weighted kappa",
            "paired_accuracy_test": "exact McNemar",
            "uncertainty": "trade-date clustered paired bootstrap 2000 samples",
            "multiplicity": "Holm correction over four source-by-baseline comparisons",
            "superiority_gate": [
                "clustered Macro-F1 difference 95% CI low > 0",
                "clustered QWK difference 95% CI low >= 0",
                "Holm-adjusted exact McNemar p < 0.05",
            ],
        },
        "artifact_reuse": {
            "mode": "exact-only",
            "required_identity": [
                "model preset and pinned revision",
                "source and seed",
                "K-FNSPID manifest SHA-256",
                "training recipe",
                "artifact file byte size and SHA-256",
                "prediction file byte size and SHA-256",
            ],
        },
        "code": {_display(path): _manifest(path) for path in CODE_PATHS},
    }


def _manifest(path: Path) -> dict[str, Any]:
    return {
        "path": _display(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _directory_manifest(path: Path) -> dict[str, Any]:
    files = sorted(item for item in path.iterdir() if item.is_file())
    if not files:
        raise ValueError(f"artifact 디렉터리가 비었습니다: {path}")
    return {
        "path": _display(path),
        "files": {item.name: _manifest(item) for item in files},
    }


def _display(path: Path) -> str:
    return str(path.resolve().relative_to(PROJECT_ROOT))


def _project_path(path: Path) -> Path:
    resolved = path.resolve() if path.is_absolute() else (PROJECT_ROOT / path).resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError(f"프로젝트 밖의 경로는 사용할 수 없습니다: {path}")
    return resolved


if __name__ == "__main__":
    main()
