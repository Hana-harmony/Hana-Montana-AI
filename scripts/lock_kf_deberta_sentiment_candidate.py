from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import tempfile
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from hannah_montana_ai.services.model_artifact_integrity import verify_artifact_manifest
from hannah_montana_ai.services.sentiment_artifact_contract import (
    LOCK_SCHEMA_VERSION as V6_LOCK_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY as V6_MODEL_FAMILY,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    TRAINING_SCHEMA_VERSION as V6_TRAINING_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    SourceHierarchicalArtifactContract,
    validate_source_hierarchical_artifact,
)
from hannah_montana_ai.services.sentiment_input import validated_sentiment_logit_biases
from hannah_montana_ai.services.sentiment_runtime_parity import (
    build_runtime_parity_lock_commitment,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    baseline_commitments_sha256,
    build_confirmatory_baseline_commitments,
)
from hannah_montana_ai.training.sentiment_evaluation_plan import (
    RECIPE_RELATIVE_PATHS,
    canonical_statistical_analysis_plan,
)
from hannah_montana_ai.training.sentiment_v6_evaluation_contract import (
    build_v6_confirmatory_baseline_commitments,
    canonical_v6_statistical_analysis_plan,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports/candidates"
DEFAULT_ARTIFACT_ROOT = PROJECT_ROOT / "artifacts/sentiment/candidates"
DEFAULT_V6_ARTIFACT_ROOT = PROJECT_ROOT / "artifacts/sentiment/v6-candidates"
DEFAULT_LOCKED_DIR = PROJECT_ROOT / "artifacts/sentiment/locked"
DEFAULT_MANIFEST = PROJECT_ROOT / "reports/sentiment-candidate-lock.json"
DEFAULT_TFIDF_MODEL = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
DEFAULT_RAW_REFERENCE_ARTIFACT = PROJECT_ROOT / "models/kr-finbert-sc-raw-reference"
DEFAULT_PRE_K_ARTIFACT = PROJECT_ROOT / "src/hannah_montana_ai/model_store/kf_deberta_sentiment"
DEFAULT_PRE_K_REPORT = (
    PROJECT_ROOT / "reports/kf-deberta-sentiment-training-report-pre-k-fnspid.json"
)
DEFAULT_FAIR_ARTIFACT_ROOT = PROJECT_ROOT / "artifacts/sentiment/fair_baselines/kr-finbert-sc"
DEFAULT_FAIR_SELECTION = PROJECT_ROOT / "reports/fair_baselines/kr-finbert-sc/selection.json"
DEFAULT_V6_FAIR_ARTIFACT_ROOT = (
    PROJECT_ROOT / "artifacts/sentiment/fair_baselines/kr-finbert-sc-v6"
)
DEFAULT_V6_FAIR_SELECTION = (
    PROJECT_ROOT / "reports/fair_baselines/kr-finbert-sc-v6/selection.json"
)
DEFAULT_NO_K_SELECTION = (
    PROJECT_ROOT / "reports/ablations/kf-deberta-sentiment-no-k-selection.json"
)
DEFAULT_NO_K_WINNER_MANIFEST = (
    PROJECT_ROOT
    / "artifacts/sentiment/ablations/no-k/selection/winner-artifact-manifest.json"
)
DEFAULT_V6_NO_K_SELECTION = (
    PROJECT_ROOT / "reports/ablations/v6/no-k/selection.json"
)
DEFAULT_V6_NO_K_WINNER_MANIFEST = (
    PROJECT_ROOT / "reports/ablations/v6/no-k/winner.json"
)
DEFAULT_RUNTIME_PARITY_EVIDENCE = PROJECT_ROOT / "reports/sentiment-cpu-runtime-parity.json"
REQUIRED_ARTIFACTS = (
    "adapter_config.json",
    "adapter_model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
    "hannah_metadata.json",
)
TRAINING_ARTIFACTS = REQUIRED_ARTIFACTS[:-1]
REQUIRED_SEEDS = frozenset({17, 42, 73})
REQUIRED_SELECTION_PARTITIONS = (
    "PUBLIC_SELECTION",
    "K_FNSPID_DEVELOPMENT_SELECTION",
    "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION",
)
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
INPUT_FEATURE_VERSION = "source-target-prefix-head-tail/v2"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
DATA_SELECTION_SEED = 20_260_715
DATASET_REVISION = "K-FNSPID-v4"
PUBLIC_DATASET_REVISION = "7a8dc8cf6548a08e0a5dab3a12ad0fb8dccfd23f"
CODEBOOK_PATH = PROJECT_ROOT / "docs/datasets/k-fnspid-sentiment-codebook.md"
SAMPLING_IMPLEMENTATION_PATH = PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_sampling.py"
DATASET_REPORT_PATHS = {
    "NEWS": PROJECT_ROOT / "reports/k-fnspid-sentiment-dataset-report.json",
    "DISCLOSURE": PROJECT_ROOT / "reports/k-fnspid-disclosure-sentiment-dataset-report.json",
    "SAMPLING_DESIGN": PROJECT_ROOT
    / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json",
}
REQUIRED_TRAINING_INPUTS = frozenset(
    {
        "public_train",
        "public_validation",
        "news_silver",
        "disclosure_silver",
        "train_gold",
        "news_auxiliary_training_gold",
        "disclosure_auxiliary_training_gold",
        "news_auxiliary_training_report",
        "disclosure_auxiliary_training_report",
        "news_development_gold",
        "disclosure_development_gold",
        "news_sealed_review_reservation",
        "disclosure_sealed_review_reservation",
        "sealed_sampling_design",
        "legacy_evaluation_1",
        "legacy_evaluation_2",
        "legacy_evaluation_3",
        "legacy_evaluation_4",
    }
)
V6_RECIPE_RELATIVE_PATHS = {
    "candidate_trainer": "scripts/train_kf_deberta_sentiment_v6.py",
    "candidate_locker": "scripts/lock_kf_deberta_sentiment_candidate.py",
    "canonical_evaluator": "scripts/evaluate_locked_kf_deberta_sentiment.py",
    "runtime_parity_generator": "scripts/generate_sentiment_cpu_runtime_parity.py",
    "artifact_contract": "src/hannah_montana_ai/services/sentiment_artifact_contract.py",
    "hierarchical_runtime": (
        "src/hannah_montana_ai/services/source_hierarchical_sentiment.py"
    ),
    "serving_loader": "src/hannah_montana_ai/services/transformer_sentiment_model.py",
    "input_contract": "src/hannah_montana_ai/services/sentiment_input.py",
    "protocol": "src/hannah_montana_ai/training/sentiment_protocol.py",
    "v6_ablation_trainer": "scripts/train_kf_deberta_sentiment_v6_ablation.py",
    "v6_evaluation_contract": (
        "src/hannah_montana_ai/training/sentiment_v6_evaluation_contract.py"
    ),
    "v6_fair_baseline_trainer": "scripts/train_kr_finbert_sc_sentiment_v6.py",
    "v6_fair_baseline_runtime": (
        "src/hannah_montana_ai/services/kr_finbert_sc_v6_baseline.py"
    ),
    "v6_raw_reference_runtime": (
        "src/hannah_montana_ai/services/kr_finbert_sc_raw_reference.py"
    ),
    "v6_raw_reference_materializer": (
        "scripts/materialize_kr_finbert_sc_raw_reference.py"
    ),
    "v6_fair_baseline_commitment": (
        "src/hannah_montana_ai/training/sentiment_v6_baseline_commitment.py"
    ),
    "dependency_manifest": "pyproject.toml",
    "dependency_lock": "uv.lock",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Selection 성능만으로 감성 후보를 선택하고 artifact hash를 잠근다."
    )
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument(
        "--pipeline-version",
        choices=("auto", "v5", "v6"),
        default="auto",
    )
    parser.add_argument("--locked-dir", type=Path, default=DEFAULT_LOCKED_DIR)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--tfidf-model", type=Path, default=DEFAULT_TFIDF_MODEL)
    parser.add_argument(
        "--raw-reference-artifact",
        type=Path,
        default=DEFAULT_RAW_REFERENCE_ARTIFACT,
    )
    parser.add_argument("--pre-k-artifact", type=Path, default=DEFAULT_PRE_K_ARTIFACT)
    parser.add_argument("--pre-k-report", type=Path, default=DEFAULT_PRE_K_REPORT)
    parser.add_argument(
        "--fair-artifact-root", type=Path, default=DEFAULT_FAIR_ARTIFACT_ROOT
    )
    parser.add_argument("--fair-selection", type=Path, default=DEFAULT_FAIR_SELECTION)
    parser.add_argument("--no-k-selection", type=Path, default=DEFAULT_NO_K_SELECTION)
    parser.add_argument(
        "--no-k-winner-manifest", type=Path, default=DEFAULT_NO_K_WINNER_MANIFEST
    )
    parser.add_argument(
        "--runtime-parity-evidence", type=Path, default=DEFAULT_RUNTIME_PARITY_EVIDENCE
    )
    args = parser.parse_args()

    if args.locked_dir.exists() or args.locked_dir.is_symlink():
        raise SystemExit(f"잠긴 artifact가 이미 존재합니다: {args.locked_dir}")
    if args.manifest_path.exists() or args.manifest_path.is_symlink():
        raise SystemExit(f"후보 lock manifest가 이미 존재합니다: {args.manifest_path}")

    v6_reports = sorted(args.report_dir.glob("kf-deberta-sentiment-v6-seed*.json"))
    v5_reports = sorted(args.report_dir.glob("kf-deberta-sentiment-seed*.json"))
    if args.pipeline_version == "auto" and v5_reports and v6_reports:
        raise SystemExit("v5/v6 후보가 함께 있어 --pipeline-version을 명시해야 합니다.")
    use_v6 = args.pipeline_version == "v6" or (
        args.pipeline_version == "auto" and bool(v6_reports)
    )
    if use_v6:
        artifact_root = (
            DEFAULT_V6_ARTIFACT_ROOT
            if args.artifact_root == DEFAULT_ARTIFACT_ROOT
            else args.artifact_root
        )
        fair_artifact_root = (
            DEFAULT_V6_FAIR_ARTIFACT_ROOT
            if args.fair_artifact_root == DEFAULT_FAIR_ARTIFACT_ROOT
            else args.fair_artifact_root
        )
        fair_selection = (
            DEFAULT_V6_FAIR_SELECTION
            if args.fair_selection == DEFAULT_FAIR_SELECTION
            else args.fair_selection
        )
        no_k_selection = (
            DEFAULT_V6_NO_K_SELECTION
            if args.no_k_selection == DEFAULT_NO_K_SELECTION
            else args.no_k_selection
        )
        no_k_winner_manifest = (
            DEFAULT_V6_NO_K_WINNER_MANIFEST
            if args.no_k_winner_manifest == DEFAULT_NO_K_WINNER_MANIFEST
            else args.no_k_winner_manifest
        )
        manifest = lock_v6_candidates(
            report_dir=args.report_dir,
            artifact_root=artifact_root,
            locked_dir=args.locked_dir,
            manifest_path=args.manifest_path,
            raw_reference_artifact=args.raw_reference_artifact,
            tfidf_model=args.tfidf_model,
            pre_k_artifact=args.pre_k_artifact,
            pre_k_report=args.pre_k_report,
            fair_artifact_root=fair_artifact_root,
            fair_selection=fair_selection,
            no_k_selection=no_k_selection,
            no_k_winner_manifest=no_k_winner_manifest,
            runtime_parity_evidence=args.runtime_parity_evidence,
        )
        print(json.dumps(manifest, ensure_ascii=False))
        return

    candidates = load_candidates(args.report_dir, args.artifact_root)
    winner = select_candidate(candidates)
    news_reservation, news_identity_keys = _sealed_reservation_commitment(
        winner["report"],
        artifact_name="news_sealed_review_reservation",
        expected_partition="CONFIRMATORY_SEALED_TEST_REVIEW",
        expected_source="NEWS",
    )
    disclosure_reservation, disclosure_identity_keys = _sealed_reservation_commitment(
        winner["report"],
        artifact_name="disclosure_sealed_review_reservation",
        expected_partition="DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
        expected_source="DISCLOSURE",
    )
    if news_identity_keys & disclosure_identity_keys:
        raise SystemExit("뉴스와 공시 봉인 reservation의 사건 식별자가 겹칩니다.")
    source_files = {
        name: {
            "bytes": (winner["artifact_dir"] / name).stat().st_size,
            "sha256": file_sha256(winner["artifact_dir"] / name),
        }
        for name in REQUIRED_ARTIFACTS
    }
    source_manifest_sha256 = _canonical_json_sha256(source_files)
    try:
        baseline_commitments = build_confirmatory_baseline_commitments(
            project_root=PROJECT_ROOT,
            tfidf_model=args.tfidf_model,
            pre_k_artifact=args.pre_k_artifact,
            pre_k_training_report=args.pre_k_report,
            fair_artifact_root=args.fair_artifact_root,
            fair_selection_report=args.fair_selection,
            no_k_selection_report=args.no_k_selection,
            no_k_winner_manifest=args.no_k_winner_manifest,
        )
        runtime_parity = build_runtime_parity_lock_commitment(
            evidence_path=args.runtime_parity_evidence,
            project_root=PROJECT_ROOT,
            expected_candidate_version=str(winner["report"]["version"]),
            expected_candidate_artifact_manifest_sha256=source_manifest_sha256,
            sealed_reservations={
                "NEWS": news_reservation,
                "DISCLOSURE": disclosure_reservation,
            },
        )
    except ValueError as exception:
        raise SystemExit(str(exception)) from exception
    copy_locked_artifact(winner["artifact_dir"], args.locked_dir)
    locked_files = {
        name: {
            "bytes": (args.locked_dir / name).stat().st_size,
            "sha256": file_sha256(args.locked_dir / name),
        }
        for name in REQUIRED_ARTIFACTS
    }
    recipe_blobs = _recipe_commitments()
    manifest = {
        "schema_version": "sentiment-candidate-lock/v1",
        "locked_at": datetime.now(UTC).isoformat(),
        "selection_only": True,
        "public_test_evaluated_before_lock": False,
        "operational_sealed_gold_evaluated_before_lock": False,
        "external_git_commitment_required": True,
        "sealed_reservations": {
            "NEWS": news_reservation,
            "DISCLOSURE": disclosure_reservation,
        },
        "dataset_provenance": {
            "codebook": _regular_file_commitment(CODEBOOK_PATH),
            "sampling_implementation": _regular_file_commitment(SAMPLING_IMPLEMENTATION_PATH),
            "dataset_reports": {
                source: _regular_file_commitment(path)
                for source, path in DATASET_REPORT_PATHS.items()
            },
        },
        "training_input_artifacts": winner["report"]["input_artifacts"],
        "statistical_analysis_plan": canonical_statistical_analysis_plan(),
        "baseline_commitments": baseline_commitments,
        "baseline_commitments_sha256": baseline_commitments_sha256(baseline_commitments),
        "runtime_parity": runtime_parity,
        "winner": {
            "seed": winner["seed"],
            "version": winner["report"]["version"],
            "selection_score": winner["selection_score"],
            "report_path": str(winner["report_path"].relative_to(PROJECT_ROOT)),
            "report_sha256": file_sha256(winner["report_path"]),
            "source_artifact_dir": str(winner["artifact_dir"].relative_to(PROJECT_ROOT)),
            "locked_artifact_dir": str(args.locked_dir.relative_to(PROJECT_ROOT)),
            "artifact_files": locked_files,
            "data_selection_seed": winner["report"]["training_arguments"][
                "data_selection_seed"
            ],
            "prepared_partition_commitments": winner["report"][
                "prepared_partition_commitments"
            ],
        },
        "ranking": [
            {
                "seed": candidate["seed"],
                "version": candidate["report"]["version"],
                "selection_score": candidate["selection_score"],
                "report_sha256": file_sha256(candidate["report_path"]),
            }
            for candidate in sorted(
                candidates,
                key=lambda row: (-row["selection_score"], row["seed"]),
            )
        ],
        "recipe": {
            "schema_version": "sentiment-candidate-recipe/v2",
            "training_script": recipe_blobs["candidate_trainer"]["path"],
            "training_script_sha256": recipe_blobs["candidate_trainer"]["sha256"],
            "auxiliary_training_gold_promoter": (
                recipe_blobs["historical_auxiliary_promoter"]["path"]
            ),
            "auxiliary_training_gold_promoter_sha256": (
                recipe_blobs["historical_auxiliary_promoter"]["sha256"]
            ),
            "blobs": recipe_blobs,
        },
    }
    args.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(args.manifest_path, manifest)
    print(json.dumps(manifest, ensure_ascii=False))


def lock_v6_candidates(
    *,
    report_dir: Path,
    artifact_root: Path,
    locked_dir: Path,
    manifest_path: Path,
    raw_reference_artifact: Path,
    tfidf_model: Path,
    pre_k_artifact: Path,
    pre_k_report: Path,
    fair_artifact_root: Path,
    fair_selection: Path,
    no_k_selection: Path,
    no_k_winner_manifest: Path,
    runtime_parity_evidence: Path,
) -> dict[str, Any]:
    if locked_dir.exists() or locked_dir.is_symlink():
        raise SystemExit(f"잠긴 v6 artifact가 이미 존재합니다: {locked_dir}")
    if manifest_path.exists() or manifest_path.is_symlink():
        raise SystemExit(f"v6 후보 lock manifest가 이미 존재합니다: {manifest_path}")
    candidates = load_v6_candidates(report_dir, artifact_root)
    winner = max(
        candidates,
        key=lambda row: (
            float(row["selection_score"]),
            float(row["selection_secondary"]),
            -int(row["seed"]),
        ),
    )
    report = winner["report"]
    news_reservation, news_keys = _sealed_reservation_commitment(
        report,
        artifact_name="news_sealed_review_reservation",
        expected_partition="CONFIRMATORY_SEALED_TEST_REVIEW",
        expected_source="NEWS",
    )
    disclosure_reservation, disclosure_keys = _sealed_reservation_commitment(
        report,
        artifact_name="disclosure_sealed_review_reservation",
        expected_partition="DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
        expected_source="DISCLOSURE",
    )
    if news_keys & disclosure_keys:
        raise SystemExit("v6 뉴스와 공시 봉인 reservation 사건 식별자가 겹칩니다.")
    reservations = {"NEWS": news_reservation, "DISCLOSURE": disclosure_reservation}
    contract: SourceHierarchicalArtifactContract = winner["contract"]
    try:
        baselines = build_v6_confirmatory_baseline_commitments(
            project_root=PROJECT_ROOT,
            candidate_training_report=report,
            raw_reference_artifact=raw_reference_artifact,
            tfidf_model=tfidf_model,
            pre_k_artifact=pre_k_artifact,
            pre_k_training_report=pre_k_report,
            fair_artifact_root=fair_artifact_root,
            fair_selection_report=fair_selection,
            no_k_selection_report=no_k_selection,
            no_k_winner_manifest=no_k_winner_manifest,
        )
        parity = build_runtime_parity_lock_commitment(
            evidence_path=runtime_parity_evidence,
            project_root=PROJECT_ROOT,
            expected_candidate_version=contract.version,
            expected_candidate_artifact_manifest_sha256=contract.locked_manifest_sha256,
            expected_candidate_model_family=V6_MODEL_FAMILY,
            expected_base_source_kind=contract.base_source_kind,
            sealed_reservations=reservations,
        )
    except ValueError as exception:
        raise SystemExit(str(exception)) from exception
    copy_locked_v6_artifact(contract, locked_dir)
    locked_contract = validate_source_hierarchical_artifact(locked_dir)
    if (
        locked_contract.locked_manifest != contract.locked_manifest
        or locked_contract.locked_manifest_sha256 != contract.locked_manifest_sha256
    ):
        raise SystemExit("복사된 v6 artifact가 선택 후보와 다릅니다.")
    recipe = {
        "schema_version": "sentiment-candidate-recipe/v3",
        "blobs": _v6_recipe_commitments(),
    }
    manifest = {
        "schema_version": V6_LOCK_SCHEMA_VERSION,
        "locked_at": datetime.now(UTC).isoformat(),
        "selection_only": True,
        "public_test_evaluated_before_lock": False,
        "operational_sealed_gold_evaluated_before_lock": False,
        "external_git_commitment_required": True,
        "sealed_reservations": reservations,
        "dataset_provenance": {
            "codebook": _regular_file_commitment(CODEBOOK_PATH),
            "sampling_implementation": _regular_file_commitment(
                SAMPLING_IMPLEMENTATION_PATH
            ),
            "dataset_reports": {
                source: _regular_file_commitment(path)
                for source, path in DATASET_REPORT_PATHS.items()
            },
        },
        "training_input_artifacts": report["input_artifacts"],
        "statistical_analysis_plan": canonical_v6_statistical_analysis_plan(),
        "baseline_commitments": baselines,
        "baseline_commitments_sha256": baseline_commitments_sha256(baselines),
        "runtime_parity": parity,
        "winner": {
            "seed": winner["seed"],
            "model_family": V6_MODEL_FAMILY,
            "version": contract.version,
            "selection_score": winner["selection_score"],
            "selection_secondary": winner["selection_secondary"],
            "report_path": str(winner["report_path"].relative_to(PROJECT_ROOT)),
            "report_sha256": file_sha256(winner["report_path"]),
            "source_artifact_dir": str(contract.artifact_dir.relative_to(PROJECT_ROOT)),
            "locked_artifact_dir": str(locked_dir.relative_to(PROJECT_ROOT)),
            "artifact_files": locked_contract.locked_manifest,
            "artifact_manifest_sha256": locked_contract.locked_manifest_sha256,
            "base_source_kind": contract.base_source_kind,
            "base_source": contract.base_source,
            "prepared_partition_commitments": report[
                "prepared_partition_commitments"
            ],
        },
        "ranking": [
            {
                "seed": candidate["seed"],
                "version": candidate["contract"].version,
                "selection_score": candidate["selection_score"],
                "selection_secondary": candidate["selection_secondary"],
                "report_sha256": file_sha256(candidate["report_path"]),
                "artifact_manifest_sha256": candidate[
                    "contract"
                ].locked_manifest_sha256,
            }
            for candidate in sorted(
                candidates,
                key=lambda row: (
                    -float(row["selection_score"]),
                    -float(row["selection_secondary"]),
                    int(row["seed"]),
                ),
            )
        ],
        "recipe": recipe,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(manifest_path, manifest)
    return manifest


def load_v6_candidates(report_dir: Path, artifact_root: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for report_path in sorted(report_dir.glob("kf-deberta-sentiment-v6-seed*.json")):
        if report_path.is_symlink() or not report_path.is_file():
            raise SystemExit(f"v6 후보 report가 없거나 symlink입니다: {report_path}")
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exception:
            raise SystemExit(
                f"v6 후보 report JSON이 올바르지 않습니다: {report_path}"
            ) from exception
        if not isinstance(report, dict):
            raise SystemExit(f"v6 후보 report는 JSON 객체여야 합니다: {report_path}")
        seed = report.get("seed")
        selection = report.get("candidate_selection")
        if (
            report.get("schema_version") != V6_TRAINING_SCHEMA_VERSION
            or isinstance(seed, bool)
            or not isinstance(seed, int)
            or not isinstance(selection, dict)
            or selection.get("public_test_used") is not False
            or selection.get("confirmatory_used") is not False
            or selection.get("independent_generalization_evidence") is not False
            or report.get("public_test_opened") is not False
            or report.get("confirmatory_labels_opened") is not False
        ):
            raise SystemExit(f"봉인 전 평가 계약을 위반한 v6 후보입니다: {report_path}")
        artifact_dir = artifact_root / f"seed{seed}"
        try:
            contract = validate_source_hierarchical_artifact(artifact_dir, report)
        except RuntimeError as exception:
            raise SystemExit(str(exception)) from exception
        score = _finite_selection_value(
            selection.get("primary_value"),
            "v6 weakest-source selection score",
        )
        secondary = _finite_selection_value(
            selection.get("secondary_overall_macro_f1"),
            "v6 overall selection score",
        )
        metrics = selection.get("metrics")
        if not isinstance(metrics, dict):
            raise SystemExit("v6 후보 selection metrics가 없습니다.")
        domain_scores: list[float] = []
        for domain in ("NEWS_UNTARGETED", "NEWS_TARGETED", "DISCLOSURE_TARGETED"):
            block = metrics.get(domain)
            if not isinstance(block, dict):
                raise SystemExit(f"v6 후보 selection domain이 없습니다: {domain}")
            domain_scores.append(
                _finite_selection_value(block.get("macro_f1"), f"v6 {domain} Macro-F1")
            )
        overall = metrics.get("OVERALL")
        if (
            not isinstance(overall, dict)
            or not math.isclose(score, min(domain_scores), rel_tol=0.0, abs_tol=1e-12)
            or not math.isclose(
                secondary,
                _finite_selection_value(overall.get("macro_f1"), "v6 overall Macro-F1"),
                rel_tol=0.0,
                abs_tol=1e-12,
            )
        ):
            raise SystemExit("v6 후보 selection score를 원천 metrics에서 재현할 수 없습니다.")
        _validate_v6_execution_commitments(report)
        candidates.append(
            {
                "seed": seed,
                "selection_score": score,
                "selection_secondary": secondary,
                "report": report,
                "report_path": report_path,
                "contract": contract,
            }
        )
    seeds = [int(candidate["seed"]) for candidate in candidates]
    if len(seeds) != len(set(seeds)) or set(seeds) != set(REQUIRED_SEEDS):
        raise SystemExit(f"v6 후보 seed 집합은 {sorted(REQUIRED_SEEDS)}여야 합니다: {seeds}")
    kinds = {candidate["contract"].base_source_kind for candidate in candidates}
    sources = {
        _canonical_json_sha256(candidate["contract"].base_source)
        for candidate in candidates
    }
    if len(kinds) != 1 or len(sources) != 1:
        raise SystemExit("v6 후보에서 raw/DAPT base 또는 DAPT 계보를 혼용할 수 없습니다.")
    partitions = {
        _canonical_json_sha256(candidate["report"]["prepared_partition_commitments"])
        for candidate in candidates
    }
    if len(partitions) != 1:
        raise SystemExit("v6 세 seed의 준비 파티션 commitment가 다릅니다.")
    return candidates


def _finite_selection_value(value: object, label: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(float(value))
        or not 0.0 <= float(value) <= 1.0
    ):
        raise SystemExit(f"{label} 값이 올바르지 않습니다.")
    return float(value)


def _validate_v6_execution_commitments(report: dict[str, Any]) -> None:
    for field in ("input_artifacts", "training_code", "dependency_artifacts"):
        records = report.get(field)
        if not isinstance(records, dict) or not records:
            raise SystemExit(f"v6 {field} commitment가 없습니다.")
        for name, record in records.items():
            if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
                raise SystemExit(f"v6 {field}/{name} commitment가 올바르지 않습니다.")
            path = _safe_project_path(record.get("path"), f"v6 {field}/{name}")
            if record.get("bytes") != path.stat().st_size or record.get("sha256") != file_sha256(
                path
            ):
                raise SystemExit(f"v6 {field}/{name} 파일이 학습 후 변경됐습니다.")


def copy_locked_v6_artifact(
    contract: SourceHierarchicalArtifactContract,
    destination: Path,
) -> None:
    if destination.exists() or destination.is_symlink():
        raise SystemExit(f"잠긴 v6 artifact 목적지가 이미 존재합니다: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        destination.mkdir(mode=0o700)
        created = True
        for relative in sorted(contract.locked_manifest):
            source = contract.artifact_dir / relative
            target = destination / relative
            if source.is_symlink() or not source.is_file():
                raise SystemExit(f"v6 필수 artifact가 없습니다: {source}")
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with source.open("rb") as source_file, target.open("xb") as target_file:
                shutil.copyfileobj(source_file, target_file)
                target_file.flush()
                os.fsync(target_file.fileno())
            shutil.copystat(source, target, follow_symlinks=False)
        for directory in sorted(
            (path for path in destination.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            directory_fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        directory_fd = os.open(destination, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if created:
            actual = {
                path.relative_to(destination).as_posix()
                for path in destination.rglob("*")
                if path.is_file()
            }
            if actual != set(contract.locked_manifest):
                shutil.rmtree(destination)


def _v6_recipe_commitments() -> dict[str, dict[str, int | str]]:
    return {
        name: _regular_file_commitment(PROJECT_ROOT / relative)
        for name, relative in V6_RECIPE_RELATIVE_PATHS.items()
    }


def load_candidates(report_dir: Path, artifact_root: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for report_path in sorted(report_dir.glob("kf-deberta-sentiment-seed*.json")):
        if report_path.is_symlink() or not report_path.is_file():
            raise SystemExit(f"후보 report가 없거나 symlink입니다: {report_path}")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise SystemExit(f"후보 report는 JSON 객체여야 합니다: {report_path}")
        selection = report.get("candidate_selection", {})
        test = report.get("test", {})
        raw_seed = report.get("seed")
        if isinstance(raw_seed, bool) or not isinstance(raw_seed, int):
            raise SystemExit(f"후보 seed가 올바르지 않습니다: {report_path}")
        seed = raw_seed
        artifact_dir = artifact_root / f"seed{seed}"
        if (
            report.get("schema_version") != "kf-deberta-sentiment-training/v2"
            or report.get("base_model") != BASE_MODEL
            or report.get("base_model_revision") != BASE_MODEL_REVISION
            or report.get("input_feature_version") != INPUT_FEATURE_VERSION
            or tuple(report.get("label_order", ())) != LABEL_ORDER
            or report.get("dataset_revision") != DATASET_REVISION
            or report.get("public_dataset_revision") != PUBLIC_DATASET_REVISION
            or report.get("training_strategy")
            != "group-purged-three-way-dual-gold-target-swap-rdrop-hierarchical-upper6-lora/v5"
            or not isinstance(report.get("training_arguments"), dict)
            or report["training_arguments"].get("data_selection_seed") != DATA_SELECTION_SEED
            or selection.get("test_used_for_selection") is not False
            or selection.get("operational_gold_used_for_selection") is not False
            or selection.get("sealed_test_evaluated") is not False
            or int(test.get("sample_count", -1)) != 0
            or test.get("status") != "SEALED_UNTIL_CANDIDATE_LOCK"
        ):
            raise SystemExit(f"봉인 전 평가 계약을 위반한 후보입니다: {report_path}")
        selection_score = _validated_selection_score(report)
        if artifact_dir.is_symlink() or not artifact_dir.is_dir():
            raise SystemExit(f"후보 artifact 디렉터리가 올바르지 않습니다: {artifact_dir}")
        artifact_manifest = report.get("artifact_files")
        if (
            not isinstance(artifact_manifest, dict)
            or set(artifact_manifest) != set(TRAINING_ARTIFACTS)
            or not verify_artifact_manifest(artifact_dir, artifact_manifest)
        ):
            raise SystemExit(f"artifact 무결성 검증에 실패했습니다: {artifact_dir}")
        metadata_path = artifact_dir / "hannah_metadata.json"
        if metadata_path.is_symlink() or not metadata_path.is_file():
            raise SystemExit(f"artifact metadata가 없거나 symlink입니다: {metadata_path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict) or not _metadata_matches(metadata, report):
            raise SystemExit(f"artifact metadata 계약이 일치하지 않습니다: {artifact_dir}")
        _validate_training_code(report)
        _validate_dependency_provenance(report)
        _validate_training_inputs(report)
        _validate_prepared_partition_commitments(report.get("prepared_partition_commitments"))
        _validate_training_runtime(report.get("training_runtime"))
        candidates.append(
            {
                "seed": seed,
                "selection_score": selection_score,
                "report": report,
                "report_path": report_path,
                "artifact_dir": artifact_dir,
            }
        )
    seeds = [int(candidate["seed"]) for candidate in candidates]
    if len(seeds) != len(set(seeds)) or set(seeds) != set(REQUIRED_SEEDS):
        raise SystemExit(f"후보 seed 집합은 {sorted(REQUIRED_SEEDS)}여야 합니다: {seeds}")
    signatures = {_candidate_protocol_signature(candidate["report"]) for candidate in candidates}
    if len(signatures) != 1:
        raise SystemExit("후보 간 데이터·학습 계약이 일치하지 않습니다.")
    partition_commitments = {
        _canonical_json_sha256(candidate["report"]["prepared_partition_commitments"])
        for candidate in candidates
    }
    if len(partition_commitments) != 1:
        raise SystemExit("후보 3개 seed의 비모델 준비 파티션이 다릅니다.")
    return candidates


def _validated_selection_score(report: dict[str, Any]) -> float:
    selection = report.get("candidate_selection")
    breakdown = report.get("selection_breakdown")
    if not isinstance(selection, dict) or not isinstance(breakdown, dict):
        raise SystemExit("후보 Selection 지표가 없습니다.")
    values: list[float] = []
    for partition in REQUIRED_SELECTION_PARTITIONS:
        metrics = breakdown.get(partition)
        if not isinstance(metrics, dict):
            raise SystemExit(f"후보 Selection 파티션이 없습니다: {partition}")
        sample_count = metrics.get("sample_count")
        macro_f1 = metrics.get("macro_f1")
        if (
            isinstance(sample_count, bool)
            or not isinstance(sample_count, int)
            or sample_count < 100
            or isinstance(macro_f1, bool)
            or not isinstance(macro_f1, int | float)
            or not math.isfinite(float(macro_f1))
            or not 0.0 <= float(macro_f1) <= 1.0
        ):
            raise SystemExit(f"후보 Selection 지표가 올바르지 않습니다: {partition}")
        values.append(float(macro_f1))
    declared = selection.get("selection_score")
    expected = min(values)
    if (
        isinstance(declared, bool)
        or not isinstance(declared, int | float)
        or not math.isfinite(float(declared))
        or not math.isclose(float(declared), expected, rel_tol=0.0, abs_tol=1e-12)
    ):
        raise SystemExit("후보 selection_score를 원천 지표에서 재현할 수 없습니다.")
    return expected


def _metadata_matches(metadata: dict[str, Any], report: dict[str, Any]) -> bool:
    try:
        metadata_biases = validated_sentiment_logit_biases(metadata.get("logit_bias_by_domain"))
        report_biases = validated_sentiment_logit_biases(report.get("logit_bias_by_domain"))
    except ValueError:
        return False
    return (
        metadata.get("schema_version") == "kf-deberta-sentiment-artifact/v2"
        and metadata.get("version") == report.get("version")
        and metadata.get("base_model") == BASE_MODEL
        and metadata.get("base_model_revision") == BASE_MODEL_REVISION
        and metadata.get("input_feature_version") == INPUT_FEATURE_VERSION
        and tuple(metadata.get("label_order", ())) == LABEL_ORDER
        and metadata.get("max_length") == report.get("max_length")
        and metadata.get("artifact_files") == report.get("artifact_files")
        and metadata_biases == report_biases
    )


def _validate_training_code(report: dict[str, Any]) -> None:
    code = report.get("training_code")
    expected = {
        "model_artifact_integrity": PROJECT_ROOT
        / "src/hannah_montana_ai/services/model_artifact_integrity.py",
        "sentiment_input": PROJECT_ROOT / "src/hannah_montana_ai/services/sentiment_input.py",
        "sentiment_protocol": PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_protocol.py",
        "sentiment_sampling": PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_sampling.py",
        "trainer": PROJECT_ROOT / "scripts/train_kf_deberta_sentiment_v2.py",
    }
    if not isinstance(code, dict) or set(code) != set(expected):
        raise SystemExit("후보 학습 코드 provenance가 없습니다.")
    for name, path in expected.items():
        details = code.get(name)
        if (
            not isinstance(details, dict)
            or details.get("sha256") != file_sha256(path)
            or details.get("bytes") != path.stat().st_size
        ):
            raise SystemExit(f"후보 학습 후 코드가 변경됐습니다: {name}")


def _validate_dependency_provenance(report: dict[str, Any]) -> None:
    dependencies = report.get("dependency_artifacts")
    expected = {
        "pyproject": PROJECT_ROOT / "pyproject.toml",
        "uv_lock": PROJECT_ROOT / "uv.lock",
    }
    if not isinstance(dependencies, dict) or set(dependencies) != set(expected):
        raise SystemExit("후보 dependency lock provenance가 없습니다.")
    for name, path in expected.items():
        details = dependencies.get(name)
        if (
            not isinstance(details, dict)
            or details.get("sha256") != file_sha256(path)
            or details.get("bytes") != path.stat().st_size
        ):
            raise SystemExit(f"후보 학습 후 dependency가 변경됐습니다: {name}")
    environment = report.get("training_environment")
    required_environment = {
        "python",
        "platform",
        "torch",
        "transformers",
        "peft",
        "numpy",
        "mps_available",
        "cuda_available",
        "trainer_device",
        "bitwise_deterministic_guaranteed",
        "reproducibility_limit",
    }
    if (
        not isinstance(environment, dict)
        or set(environment) != required_environment
        or any(
            not str(environment[name]).strip()
            for name in required_environment - {"mps_available", "cuda_available"}
        )
        or not isinstance(environment["mps_available"], bool)
        or not isinstance(environment["cuda_available"], bool)
        or not str(environment["trainer_device"]).strip()
        or environment["bitwise_deterministic_guaranteed"] is not False
        or not str(environment["reproducibility_limit"]).strip()
    ):
        raise SystemExit("후보 학습 환경 provenance가 올바르지 않습니다.")
    base = report.get("base_model_provenance")
    if (
        not isinstance(base, dict)
        or base.get("repository") != BASE_MODEL
        or base.get("revision") != BASE_MODEL_REVISION
        or base.get("source_weight_filename") != "pytorch_model.bin"
        or base.get("source_weights_format") != "pytorch_model.bin"
        or base.get("source_weight_sha256")
        != "3cd6cd7811b3c9190e97cae7eb41571c2bc0076431baae7d41d449a8c1c18c6c"
        or base.get("deserialization") != "torch_weights_only"
        or base.get("trust_remote_code") is not False
        or base.get("weights_only") is not True
    ):
        raise SystemExit("후보 base model provenance가 올바르지 않습니다.")


def _validate_training_inputs(report: dict[str, Any]) -> None:
    inputs = report.get("input_artifacts")
    if not isinstance(inputs, dict) or set(inputs) != set(REQUIRED_TRAINING_INPUTS):
        raise SystemExit("후보 학습 입력 provenance 집합이 올바르지 않습니다.")
    for name, record in inputs.items():
        if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
            raise SystemExit(f"후보 학습 입력 commitment가 올바르지 않습니다: {name}")
        path = _safe_project_path(record.get("path"), name)
        if record.get("bytes") != path.stat().st_size or record.get("sha256") != file_sha256(path):
            raise SystemExit(f"후보 학습 후 입력이 변경됐습니다: {name}")


def _validate_prepared_partition_commitments(raw: object) -> None:
    required = {
        "TRAIN",
        "CHECKPOINT",
        "CALIBRATION",
        "SELECTION",
        "NEWS_CONFIRMATORY_RESERVATION",
        "DISCLOSURE_CONFIRMATORY_RESERVATION",
    }
    if not isinstance(raw, dict) or set(raw) != required:
        raise SystemExit("후보 준비 파티션 commitment가 완전하지 않습니다.")
    for name, commitment in raw.items():
        if not isinstance(commitment, dict) or set(commitment) != {"row_count", "sha256"}:
            raise SystemExit(f"후보 {name} commitment가 올바르지 않습니다.")
        count = commitment.get("row_count")
        digest = commitment.get("sha256")
        if (
            isinstance(count, bool)
            or not isinstance(count, int)
            or count < 1
            or not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise SystemExit(f"후보 {name} commitment가 올바르지 않습니다.")


def _validate_training_runtime(raw: object) -> None:
    required = {
        "trainer_device",
        "global_step",
        "train_runtime",
        "train_samples_per_second",
        "train_steps_per_second",
    }
    if not isinstance(raw, dict) or set(raw) != required:
        raise SystemExit("후보 Trainer runtime provenance가 올바르지 않습니다.")
    step = raw.get("global_step")
    if isinstance(step, bool) or not isinstance(step, int) or step < 1:
        raise SystemExit("후보 Trainer global_step이 올바르지 않습니다.")
    if not str(raw.get("trainer_device", "")).strip():
        raise SystemExit("후보 Trainer device provenance가 없습니다.")
    for name in required - {"trainer_device", "global_step"}:
        value = raw.get(name)
        if (
            isinstance(value, bool)
            or not isinstance(value, int | float)
            or not math.isfinite(float(value))
            or float(value) < 0.0
        ):
            raise SystemExit(f"후보 Trainer runtime 지표가 올바르지 않습니다: {name}")


def _candidate_protocol_signature(report: dict[str, Any]) -> str:
    arguments = report.get("training_arguments")
    if not isinstance(arguments, dict) or arguments.get("max_train_rows") is not None:
        raise SystemExit("후보 학습 인자 provenance가 올바르지 않습니다.")
    common_arguments = {name: value for name, value in arguments.items() if name != "seed"}
    payload = {
        "dataset_revision": report.get("dataset_revision"),
        "public_dataset_revision": report.get("public_dataset_revision"),
        "base_model_provenance": report.get("base_model_provenance"),
        "input_artifacts": report.get("input_artifacts"),
        "training_code": report.get("training_code"),
        "dependency_artifacts": report.get("dependency_artifacts"),
        "training_environment": report.get("training_environment"),
        "training_arguments": common_arguments,
        "training_strategy": report.get("training_strategy"),
        "lora_layers": report.get("lora_layers"),
        "loss": report.get("loss", {}).get("method")
        if isinstance(report.get("loss"), dict)
        else None,
        "partition_count": report.get("partition_count"),
        "prepared_partition_commitments": report.get("prepared_partition_commitments"),
        "training_weight_audit": report.get("training_weight_audit"),
    }
    return sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _sealed_reservation_commitment(
    report: dict[str, Any],
    *,
    artifact_name: str,
    expected_partition: str,
    expected_source: str,
) -> tuple[dict[str, Any], set[tuple[str, str]]]:
    input_artifacts = report.get("input_artifacts")
    if not isinstance(input_artifacts, dict):
        raise SystemExit("후보 input artifact provenance가 없습니다.")
    details = input_artifacts.get(artifact_name)
    if not isinstance(details, dict):
        raise SystemExit(f"봉인 reservation provenance가 없습니다: {artifact_name}")
    path = _safe_project_path(details.get("path"), artifact_name)
    if details.get("sha256") != file_sha256(path) or details.get("bytes") != path.stat().st_size:
        raise SystemExit(f"봉인 reservation 파일이 학습 후 변경됐습니다: {path}")
    item_ids: list[str] = []
    source_record_hashes: list[dict[str, str]] = []
    identity_keys: set[tuple[str, str]] = set()
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if (
                not isinstance(row, dict)
                or row.get("schema_version") != "k-fnspid-sentiment-review-row/v1"
                or row.get("partition") != expected_partition
                or row.get("source_type") != expected_source
                or row.get("review_status") != "NEEDS_BLIND_REVIEW"
                or row.get("final_sentiment") not in {"", None}
            ):
                raise SystemExit(f"봉인 reservation 계약 위반: {path}:{line_number}")
            source_sha256 = _canonical_json_sha256(row)
            item_id = _review_item_id(row, source_sha256)
            item_ids.append(item_id)
            source_record_hashes.append({"item_id": item_id, "source_record_sha256": source_sha256})
            for field in ("content_hash", "event_cluster_id"):
                value = row.get(field)
                if isinstance(value, str) and value.strip():
                    identity_keys.add((field, value.strip()))
    if len(item_ids) < 500 or len(item_ids) != len(set(item_ids)):
        raise SystemExit(f"봉인 reservation 행 수 또는 item_id가 올바르지 않습니다: {path}")
    item_ids.sort()
    source_record_hashes.sort(key=lambda row: row["item_id"])
    return (
        {
            "path": str(path.relative_to(PROJECT_ROOT)),
            "sha256": file_sha256(path),
            "bytes": path.stat().st_size,
            "sample_count": len(item_ids),
            "partition": expected_partition,
            "source_type": expected_source,
            "item_id_set_sha256": _canonical_json_sha256(item_ids),
            "source_record_set_sha256": _canonical_json_sha256(source_record_hashes),
        },
        identity_keys,
    )


def _safe_project_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise SystemExit(f"{label} 경로가 없습니다.")
    candidate = (PROJECT_ROOT / value).resolve()
    try:
        candidate.relative_to(PROJECT_ROOT.resolve())
    except ValueError as exception:
        raise SystemExit(f"{label} 경로가 프로젝트 밖입니다.") from exception
    if candidate.is_symlink() or not candidate.is_file():
        raise SystemExit(f"{label} 파일이 없거나 symlink입니다: {candidate}")
    return candidate


def _review_item_id(row: dict[str, Any], source_sha256: str) -> str:
    for field in ("review_key", "annotation_id", "item_id"):
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    document_id = row.get("document_id")
    target = row.get("target_security") or row.get("stock_code")
    target_value = target.strip() if isinstance(target, str) else "UNSPECIFIED"
    if isinstance(document_id, str) and document_id.strip():
        return f"{document_id.strip()}::{target_value}"
    content_hash = row.get("content_hash")
    if isinstance(content_hash, str) and content_hash.strip():
        return f"{content_hash.strip()}::{target_value}"
    return source_sha256


def _canonical_json_sha256(payload: object) -> str:
    return sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _regular_file_commitment(path: Path) -> dict[str, int | str]:
    if path.is_symlink() or not path.is_file():
        raise SystemExit(f"provenance 파일이 없거나 symlink입니다: {path}")
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "bytes": path.stat().st_size,
        "sha256": file_sha256(path),
    }


def _recipe_commitments() -> dict[str, dict[str, int | str]]:
    names = [name for name, _ in RECIPE_RELATIVE_PATHS]
    if len(names) != len(set(names)):
        raise SystemExit("candidate recipe blob 이름이 중복됩니다.")
    return {
        name: _regular_file_commitment(PROJECT_ROOT / relative_path)
        for name, relative_path in RECIPE_RELATIVE_PATHS
    }


def select_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        candidates,
        key=lambda row: (
            float(row["selection_score"]),
            float(row["report"]["selection"]["macro_f1"]),
            -int(row["seed"]),
        ),
    )


def copy_locked_artifact(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise SystemExit(f"잠긴 artifact 목적지가 이미 존재합니다: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        destination.mkdir(mode=0o700)
        created = True
        for name in REQUIRED_ARTIFACTS:
            source_path = source / name
            if source_path.is_symlink() or not source_path.is_file():
                raise SystemExit(f"필수 artifact가 없습니다: {source_path}")
            destination_path = destination / name
            with (
                source_path.open("rb") as source_file,
                destination_path.open("xb") as destination_file,
            ):
                shutil.copyfileobj(source_file, destination_file)
                destination_file.flush()
                os.fsync(destination_file.fileno())
            shutil.copystat(source_path, destination_path, follow_symlinks=False)
        directory_fd = os.open(destination, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if created and set(path.name for path in destination.iterdir()) != set(REQUIRED_ARTIFACTS):
            shutil.rmtree(destination)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise SystemExit(f"후보 lock manifest가 이미 존재합니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o600)
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as exception:
            raise SystemExit(f"후보 lock manifest가 이미 존재합니다: {path}") from exception
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
