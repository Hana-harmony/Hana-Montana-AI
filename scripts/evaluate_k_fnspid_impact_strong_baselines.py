from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

try:
    from scripts.evaluate_k_fnspid_research import (
        align_predictions,
        evaluate_research,
        load_predictions,
    )
    from scripts.train_k_fnspid_transformer import MODEL_PRESETS
except ModuleNotFoundError:  # 직접 실행 시 프로젝트 루트를 모듈 경로로 사용한다.
    from evaluate_k_fnspid_research import (
        align_predictions,
        evaluate_research,
        load_predictions,
    )
    from train_k_fnspid_transformer import MODEL_PRESETS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "reports/k-fnspid-impact-strong-baseline-matrix.json"
COMPARISON_MODEL_PRESETS = ("KR_FINBERT_SC", "KLUE_ROBERTA_LARGE")
SOURCES = ("NEWS", "DISCLOSURE")
CANDIDATE_NEWS_REPORT = (
    PROJECT_ROOT / "reports/k-fnspid-impact-news-transformer-training-report.json"
)
CANDIDATE_DISCLOSURE_AGGREGATE = (
    PROJECT_ROOT / "reports/k-fnspid-impact-disclosure-transformer-multiseed-report.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="K-FNSPID 시장영향 모델과 강한 공개 비교군을 동일 Test에서 평가한다."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-samples", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=20260718)
    parser.add_argument(
        "--model-preset",
        action="append",
        choices=COMPARISON_MODEL_PRESETS,
        dest="model_presets",
        help="비교할 공개 모델을 지정한다. 생략하면 잠긴 전체 모델을 평가한다.",
    )
    args = parser.parse_args()
    model_presets = tuple(args.model_presets or COMPARISON_MODEL_PRESETS)

    comparisons: list[dict[str, Any]] = []
    for source in SOURCES:
        candidate_selection_path, candidate_predictions = _candidate_selection(source)
        for model_preset in model_presets:
            baseline_selection_path, baseline_predictions = _baseline_selection(
                model_preset,
                source,
            )
            aligned = align_predictions(
                load_predictions(baseline_predictions),
                load_predictions(candidate_predictions),
            )
            if {str(row["source_type"]) for row in aligned} != {source}:
                raise ValueError(f"{model_preset}/{source} 예측 출처가 평가 계약과 다릅니다.")
            evaluation = evaluate_research(
                aligned,
                bootstrap_samples=args.bootstrap_samples,
                seed=args.seed,
            )
            comparisons.append(
                {
                    "model_preset": model_preset,
                    "source_type": source,
                    "candidate_selection": _manifest(candidate_selection_path),
                    "baseline_selection": _manifest(baseline_selection_path),
                    "candidate_predictions": _manifest(candidate_predictions),
                    "baseline_predictions": _manifest(baseline_predictions),
                    "evaluation": evaluation,
                }
            )

    _apply_holm_mcnemar(comparisons)
    report = {
        "schema_version": "k-fnspid-impact-strong-baseline-matrix/v1",
        "task": "K-FNSPID market-impact LOW/MEDIUM/HIGH/CRITICAL classification",
        "claim_scope": (
            "same K-FNSPID temporal Test and named public strong baselines; "
            "not a global SOTA leaderboard"
        ),
        "bootstrap_samples": args.bootstrap_samples,
        "bootstrap_seed": args.seed,
        "holm_family": (
            f"{len(comparisons)} source-by-public-baseline paired accuracy hypotheses"
        ),
        "comparisons": comparisons,
        "all_primary_gates_passed": all(
            bool(item["strong_baseline_superiority_gate"]["passed"])
            for item in comparisons
        ),
    }
    output = _project_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def _apply_holm_mcnemar(comparisons: list[dict[str, Any]]) -> None:
    ordered = sorted(
        enumerate(comparisons),
        key=lambda pair: float(pair[1]["evaluation"]["mcnemar_exact"]["p_value"]),
    )
    running = 0.0
    adjusted: dict[int, float] = {}
    family_size = len(ordered)
    for rank, (index, item) in enumerate(ordered):
        raw = float(item["evaluation"]["mcnemar_exact"]["p_value"])
        running = max(running, min(1.0, raw * (family_size - rank)))
        adjusted[index] = running

    for index, item in enumerate(comparisons):
        evaluation = item["evaluation"]
        macro_interval = evaluation["clustered_bootstrap"]["macro_f1_difference"]
        kappa_interval = evaluation["clustered_bootstrap"]["quadratic_kappa_difference"]
        adjusted_p = adjusted[index]
        gate = {
            "trade_date_clustered_macro_f1_ci_low_above_zero": (
                float(macro_interval["low"]) > 0.0
            ),
            "trade_date_clustered_quadratic_kappa_ci_low_not_below_zero": (
                float(kappa_interval["low"]) >= 0.0
            ),
            "holm_adjusted_mcnemar_p_below_0_05": adjusted_p < 0.05,
        }
        item["holm_adjusted_mcnemar_p_value"] = adjusted_p
        item["strong_baseline_superiority_gate"] = {
            **gate,
            "passed": all(gate.values()),
        }


def _candidate_selection(source: str) -> tuple[Path, Path]:
    if source == "NEWS":
        report = _read_json(CANDIDATE_NEWS_REPORT)
        _validate_candidate_news_report(report)
        return CANDIDATE_NEWS_REPORT, _report_prediction_path(report)
    aggregate = _read_json(CANDIDATE_DISCLOSURE_AGGREGATE)
    _validate_candidate_aggregate(aggregate, source="DISCLOSURE")
    return CANDIDATE_DISCLOSURE_AGGREGATE, _prediction_path(aggregate)


def _baseline_selection(model_preset: str, source: str) -> tuple[Path, Path]:
    model_slug = _baseline_model_slug(model_preset)
    if source == "NEWS":
        path = (
            PROJECT_ROOT
            / f"reports/strong_baselines/impact/{model_slug}/news/seed73.json"
        )
        report = _read_json(path)
        _validate_baseline_news_report(report, model_preset=model_preset)
        return path, _report_prediction_path(report)
    path = (
        PROJECT_ROOT
        / f"reports/strong_baselines/impact/{model_slug}/disclosure/multiseed.json"
    )
    aggregate = _read_json(path)
    _validate_baseline_aggregate(
        aggregate,
        model_preset=model_preset,
        source="DISCLOSURE",
    )
    return path, _prediction_path(aggregate)


def _prediction_path(aggregate: dict[str, Any]) -> Path:
    selected = _project_path(Path(str(aggregate["selected_predictions_path"])))
    selected_seed = int(aggregate["selected_seed_by_validation"])
    run = next(
        (item for item in aggregate["runs"] if int(item["seed"]) == selected_seed),
        None,
    )
    if run is None:
        raise ValueError("선택 seed에 해당하는 집계 run이 없습니다.")
    prediction_manifest = run.get("predictions")
    if prediction_manifest is not None:
        if str(prediction_manifest["path"]) != str(
            selected.relative_to(PROJECT_ROOT)
        ):
            raise ValueError("선택 예측 경로와 집계 run 경로가 다릅니다.")
        _verify_file_manifest(selected, prediction_manifest)
    return selected


def _report_prediction_path(report: dict[str, Any]) -> Path:
    manifest = report.get("test_predictions")
    if not isinstance(manifest, dict):
        raise ValueError("학습 보고서의 Test 예측 manifest가 없습니다.")
    path = _project_path(Path(str(manifest["path"])))
    _verify_file_manifest(path, manifest)
    return path


def _validate_candidate_aggregate(aggregate: dict[str, Any], *, source: str) -> None:
    _validate_multiseed_shape(aggregate, source=source)
    version = str(aggregate["selected_version"]).casefold()
    if "kf-deberta" not in version and "kfd" not in version:
        raise ValueError(f"{source} 후보가 Hana KF-DeBERTa 계열이 아닙니다.")


def _validate_candidate_news_report(report: dict[str, Any]) -> None:
    expected = {
        "schema_version": "k-fnspid-transformer-training/v1",
        "base_model": "kakaobank/kf-deberta-base",
        "base_model_revision": "363b171d71443b0874b0bf9cea053eb5b1650633",
        "source_type": "NEWS",
        "seed": 73,
    }
    for field, value in expected.items():
        if report.get(field) != value:
            raise ValueError(f"NEWS 후보 보고서의 {field} 계약이 다릅니다.")
    if report.get("training_state", {}).get("evaluation_only") is not True:
        raise ValueError("NEWS 후보는 동결된 통합 adapter 평가 보고서여야 합니다.")
    initial_path = report.get("training_hyperparameters", {}).get("lora", {}).get(
        "initial_adapter_path"
    )
    if initial_path != "src/hannah_montana_ai/model_store/k_fnspid_impact_transformer":
        raise ValueError("NEWS 후보의 통합 seed 42 adapter 경로가 다릅니다.")


def _validate_baseline_news_report(
    report: dict[str, Any],
    *,
    model_preset: str,
) -> None:
    preset = MODEL_PRESETS[model_preset]
    expected = {
        "schema_version": "k-fnspid-impact-strong-baseline-training/v1",
        "model_preset": model_preset,
        "base_model": preset.model_id,
        "base_model_revision": preset.revision,
        "base_model_safetensors_sha256": preset.model_safetensors_sha256,
        "comparison_only": True,
        "source_type": "NEWS",
        "seed": 73,
    }
    for field, value in expected.items():
        if report.get(field) != value:
            raise ValueError(f"{model_preset}/NEWS 보고서의 {field} 계약이 다릅니다.")
    if report.get("training_state", {}).get("evaluation_only") is not True:
        raise ValueError(f"{model_preset}/NEWS가 동결 통합 adapter 평가가 아닙니다.")
    model_slug = _baseline_model_slug(model_preset)
    expected_initial = (
        f"artifacts/impact/strong-baselines/{model_slug}/shared/seed42"
    )
    initial_path = report.get("training_hyperparameters", {}).get("lora", {}).get(
        "initial_adapter_path"
    )
    if initial_path != expected_initial:
        raise ValueError(f"{model_preset}/NEWS 통합 seed 42 adapter가 다릅니다.")


def _baseline_model_slug(model_preset: str) -> str:
    return model_preset.casefold().replace("_", "-", 1)


def _validate_baseline_aggregate(
    aggregate: dict[str, Any],
    *,
    model_preset: str,
    source: str,
) -> None:
    _validate_multiseed_shape(aggregate, source=source)
    preset = MODEL_PRESETS[model_preset]
    selected_seed = int(aggregate["selected_seed_by_validation"])
    selected_report = _selected_report(aggregate, selected_seed=selected_seed)
    if selected_report.get("schema_version") != (
        "k-fnspid-impact-strong-baseline-training/v1"
    ):
        raise ValueError(f"{model_preset}/{source} 비교 보고서 스키마가 다릅니다.")
    expected = {
        "model_preset": model_preset,
        "base_model": preset.model_id,
        "base_model_revision": preset.revision,
        "source_type": source,
        "seed": selected_seed,
        "comparison_only": True,
    }
    for field, value in expected.items():
        if selected_report.get(field) != value:
            raise ValueError(
                f"{model_preset}/{source} 선택 보고서의 {field} 계약이 다릅니다."
            )


def _validate_multiseed_shape(aggregate: dict[str, Any], *, source: str) -> None:
    seeds = sorted(int(seed) for seed in aggregate.get("seeds", []))
    if seeds != [17, 42, 73] or int(aggregate.get("run_count", 3)) != 3:
        raise ValueError(f"{source} 비교는 고정된 3개 seed 실험이어야 합니다.")
    aggregate_source = aggregate.get("source_type")
    if aggregate_source not in (None, source):
        raise ValueError(f"{source} 집계의 source_type이 다릅니다.")
    if aggregate_source is None and source != "NEWS":
        raise ValueError("source_type 없는 구형 집계는 기존 NEWS 후보에만 허용됩니다.")
    if not str(aggregate.get("selection_protocol", "")).startswith(
        "validation macro F1 only"
    ):
        raise ValueError(f"{source} seed 선택이 Validation 전용 계약이 아닙니다.")
    if len(aggregate.get("runs", [])) != 3:
        raise ValueError(f"{source} 집계 run 수가 3이 아닙니다.")
    _verify_report_manifests(aggregate)


def _verify_report_manifests(aggregate: dict[str, Any]) -> None:
    hashes = aggregate.get("report_sha256")
    if hashes is None:
        # 구형 NEWS 후보 집계는 최초 생성 당시 보고서 해시 필드가 없었다.
        return
    report_paths = [str(path) for path in aggregate.get("report_paths", [])]
    if set(report_paths) != set(hashes):
        raise ValueError("집계 보고서 경로와 SHA-256 목록이 다릅니다.")
    for display_path in report_paths:
        path = _project_path(Path(display_path))
        actual = sha256(path.read_bytes()).hexdigest()
        if actual != str(hashes[display_path]):
            raise ValueError(f"집계 입력 보고서 SHA-256이 다릅니다: {display_path}")


def _selected_report(
    aggregate: dict[str, Any],
    *,
    selected_seed: int,
) -> dict[str, Any]:
    for display_path in aggregate.get("report_paths", []):
        report = _read_json(_project_path(Path(str(display_path))))
        if int(report.get("seed", -1)) == selected_seed:
            return report
    raise ValueError("선택 seed의 원본 학습 보고서를 찾을 수 없습니다.")


def _verify_file_manifest(path: Path, manifest: dict[str, Any]) -> None:
    if path.stat().st_size != int(manifest["bytes"]):
        raise ValueError(f"파일 크기가 manifest와 다릅니다: {path}")
    if sha256(path.read_bytes()).hexdigest() != str(manifest["sha256"]):
        raise ValueError(f"파일 SHA-256이 manifest와 다릅니다: {path}")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 객체가 아닙니다: {path}")
    return value


def _manifest(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _project_path(path: Path) -> Path:
    resolved = path.resolve() if path.is_absolute() else (PROJECT_ROOT / path).resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError(f"프로젝트 밖의 경로는 사용할 수 없습니다: {path}")
    return resolved


if __name__ == "__main__":
    main()
