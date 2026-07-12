from hanah_tax_ocr.ocr.engine import _TesseractOCR
from hanah_tax_ocr.parsers.withholding_tax_form import WithholdingTaxFormParser
from hanah_tax_ocr.schemas import OCRPage, OCRResult


def test_tesseract_language_accepts_native_composite_code() -> None:
    engine = object.__new__(_TesseractOCR)

    assert engine._tesseract_lang("kor+eng") == "kor+eng"


def test_withholding_form_extracts_birth_date_and_phone_regions() -> None:
    result = WithholdingTaxFormParser().parse(
        OCRResult(
            pages=[OCRPage(page_number=1, raw_text="국내원천소득 제한세율 적용신청서 비거주자용")],
            regions={
                "birth_date": OCRPage(page_number=1, raw_text="1985-06-15"),
                "phone_number": OCRPage(page_number=1, raw_text="+1-323-555-1234"),
            },
            template_id="withholding.non_resident_v1",
        ),
        "reduced-tax.png",
    )

    assert result.fields["birth_date"] == "1985-06-15"
    assert result.fields["phone_number"] == "+13235551234"
