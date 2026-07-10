from hanah_tax_ocr.ocr.engine import _TesseractOCR


def test_tesseract_language_accepts_native_composite_code() -> None:
    engine = object.__new__(_TesseractOCR)

    assert engine._tesseract_lang("kor+eng") == "kor+eng"
