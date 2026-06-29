from __future__ import annotations

import csv
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from threading import Lock

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import (
    ForeignOwnershipQuantityRetrainRequest,
    ForeignOwnershipQuantityRetrainResponse,
)
from hannah_montana_ai.training.foreign_ownership_quantity_trainer import (
    train_foreign_ownership_quantity_model,
)

_TRAINING_LOCK = Lock()


@dataclass(frozen=True)
class ForeignOwnershipModelMaintenancePaths:
    training_data_path: Path
    restricted_codes_path: Path
    model_path: Path
    report_path: Path
    candidate_report_path: Path


class ForeignOwnershipModelMaintenanceService:
    def __init__(
        self,
        paths: ForeignOwnershipModelMaintenancePaths | None = None,
    ) -> None:
        settings = get_settings()
        self._paths = paths or ForeignOwnershipModelMaintenancePaths(
            training_data_path=settings.foreign_ownership_quantity_training_data_path,
            restricted_codes_path=settings.foreign_ownership_quantity_restricted_codes_path,
            model_path=settings.foreign_ownership_quantity_model_path,
            report_path=settings.foreign_ownership_quantity_training_report_path,
            candidate_report_path=settings.foreign_ownership_quantity_candidate_report_path,
        )

    def retrain(
        self,
        request: ForeignOwnershipQuantityRetrainRequest,
        *,
        reload_model: bool,
    ) -> ForeignOwnershipQuantityRetrainResponse:
        with _TRAINING_LOCK:
            return self._retrain_locked(request, reload_model=reload_model)

    def _retrain_locked(
        self,
        request: ForeignOwnershipQuantityRetrainRequest,
        *,
        reload_model: bool,
    ) -> ForeignOwnershipQuantityRetrainResponse:
        _validate_restricted_stock_codes(request.restricted_stock_codes)
        self._paths.training_data_path.parent.mkdir(parents=True, exist_ok=True)
        self._paths.restricted_codes_path.parent.mkdir(parents=True, exist_ok=True)
        self._paths.model_path.parent.mkdir(parents=True, exist_ok=True)
        self._paths.report_path.parent.mkdir(parents=True, exist_ok=True)
        self._paths.candidate_report_path.parent.mkdir(parents=True, exist_ok=True)

        temp_dir = Path(tempfile.mkdtemp(prefix="foreign-ownership-retrain-"))
        temp_training_data_path = temp_dir / "foreign_ownership_quantity_history.csv"
        temp_restricted_codes_path = temp_dir / "foreign_ownership_restricted_stock_codes.csv"
        temp_model_path = temp_dir / "foreign_ownership_quantity_ml.joblib"
        temp_report_path = temp_dir / "foreign-ownership-quantity-training-report.json"

        try:
            _write_training_data(temp_training_data_path, request)
            _write_restricted_codes(temp_restricted_codes_path, request.restricted_stock_codes)
            report = train_foreign_ownership_quantity_model(
                temp_training_data_path,
                temp_model_path,
                restricted_stock_codes_path=temp_restricted_codes_path,
                minimum_promotable_stock_count=request.minimum_promotable_stock_count,
                minimum_promotable_history_days=request.minimum_promotable_history_days,
                minimum_promotable_observations=request.minimum_promotable_observations,
                max_model_training_samples=request.max_model_training_samples,
            )
            _write_report(temp_report_path, report.to_dict())

            if report.release_status == "promoted":
                os.replace(temp_training_data_path, self._paths.training_data_path)
                os.replace(temp_restricted_codes_path, self._paths.restricted_codes_path)
                os.replace(temp_model_path, self._paths.model_path)
                os.replace(temp_report_path, self._paths.report_path)
                model_reloaded = reload_model
                candidate_report_path: str | None = None
            else:
                os.replace(temp_report_path, self._paths.candidate_report_path)
                model_reloaded = False
                candidate_report_path = str(self._paths.candidate_report_path)

            return ForeignOwnershipQuantityRetrainResponse(
                promoted=report.release_status == "promoted",
                release_status=report.release_status,
                model_reloaded=model_reloaded,
                observation_count=report.observation_count,
                stock_count=report.stock_count,
                sample_count=report.sample_count,
                train_date_min=date.fromisoformat(report.train_date_min),
                train_date_max=date.fromisoformat(report.train_date_max),
                selected_model=report.selected_model,
                baseline_metrics=report.baseline_metrics,
                guarded_runtime_metrics=report.guarded_runtime_metrics,
                guarded_improvement_over_baseline=report.guarded_improvement_over_baseline,
                quality_gates=report.quality_gates,
                model_path=str(self._paths.model_path),
                report_path=str(self._paths.report_path),
                candidate_report_path=candidate_report_path,
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def _write_training_data(
    path: Path,
    request: ForeignOwnershipQuantityRetrainRequest,
) -> None:
    sorted_rows = sorted(
        request.history,
        key=lambda point: (point.stock_code, point.base_date),
    )
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "stock_code",
                "base_date",
                "foreign_owned_quantity",
                "foreign_limit_quantity",
            ],
        )
        writer.writeheader()
        for point in sorted_rows:
            writer.writerow(
                {
                    "stock_code": point.stock_code,
                    "base_date": point.base_date.isoformat(),
                    "foreign_owned_quantity": point.foreign_owned_quantity,
                    "foreign_limit_quantity": point.foreign_limit_quantity,
                }
            )


def _write_restricted_codes(path: Path, stock_codes: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["stock_code"])
        writer.writeheader()
        for stock_code in sorted(set(stock_codes)):
            writer.writerow({"stock_code": stock_code})


def _write_report(path: Path, report: dict[str, object]) -> None:
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _validate_restricted_stock_codes(stock_codes: list[str]) -> None:
    invalid_codes = sorted(
        {
            stock_code
            for stock_code in stock_codes
            if not stock_code.isdigit() or len(stock_code) != 6
        }
    )
    if invalid_codes:
        joined_codes = ", ".join(invalid_codes)
        raise ValueError(f"Invalid restricted stock codes: {joined_codes}")
