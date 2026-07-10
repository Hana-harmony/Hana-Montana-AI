from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from hanah_tax_ocr.ocr import TesseractOCREngine
from hanah_tax_ocr.pipeline import TaxDocumentPipeline
from hanah_tax_ocr.review import TaxDocumentReviewer
from hanah_tax_ocr.schemas import (
    DocumentType,
    ExtractedDocument,
    OCRResult,
    ReviewResult,
    ReviewStatus,
)


class CaseDocument(BaseModel):
    document_type: DocumentType
    source_path: str
    ocr_lang: str | None = None
    ocr_result: OCRResult | None = None


class HarnessRunResult(BaseModel):
    case_id: str
    extracted_documents: list[ExtractedDocument] = Field(default_factory=list)
    review_result: ReviewResult
    queued_review_path: str | None = None


class HarnessRunner:
    def __init__(
        self,
        *,
        reviewer: TaxDocumentReviewer | None = None,
        ocr_engine: TesseractOCREngine | None = None,
        review_queue_dir: str | Path = "data/review_queue/index",
        blur_threshold: float = 100.0,
        min_ocr_confidence: float = 0.75,
    ) -> None:
        self._reviewer = reviewer or TaxDocumentReviewer()
        self._ocr_engine = ocr_engine
        self._review_queue_dir = Path(review_queue_dir)
        self._blur_threshold = blur_threshold
        self._min_ocr_confidence = min_ocr_confidence

    def run_case(
        self,
        case_id: str,
        documents: list[CaseDocument],
    ) -> HarnessRunResult:
        extracted_documents: list[ExtractedDocument] = []

        for document in documents:
            pipeline_result = TaxDocumentPipeline(
                ocr_engine=self._ocr_engine,
                blur_threshold=self._blur_threshold,
                min_ocr_confidence=self._min_ocr_confidence,
            ).process(
                document.document_type,
                document.source_path,
                ocr_result=document.ocr_result,
            )
            extracted_documents.append(pipeline_result.extracted_document)

        review_result = self._reviewer.review(extracted_documents)
        queued_review_path = None
        if self._should_queue_review(review_result, extracted_documents):
            queued_review_path = self._write_review_queue(
                case_id,
                extracted_documents,
                review_result,
            )

        return HarnessRunResult(
            case_id=case_id,
            extracted_documents=extracted_documents,
            review_result=review_result,
            queued_review_path=queued_review_path,
        )

    def write_run_result(self, run_result: HarnessRunResult, output_path: str | Path) -> None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(run_result.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _should_queue_review(
        self,
        review_result: ReviewResult,
        documents: list[ExtractedDocument],
    ) -> bool:
        if review_result.status != ReviewStatus.PASS:
            return True
        for document in documents:
            if document.quality_checks.get("blurry") is True:
                return True
            if document.quality_checks.get("low_ocr_confidence") is True:
                return True
        return False

    def _write_review_queue(
        self,
        case_id: str,
        documents: list[ExtractedDocument],
        review_result: ReviewResult,
    ) -> str:
        payload: dict[str, Any] = {
            "case_id": case_id,
            "review_result": review_result.model_dump(mode="json"),
            "documents": [document.model_dump(mode="json") for document in documents],
        }
        self._review_queue_dir.mkdir(parents=True, exist_ok=True)
        output_path = self._review_queue_dir / f"{case_id}.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return str(output_path)
