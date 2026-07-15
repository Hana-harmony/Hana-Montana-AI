from pathlib import Path


def test_runtime_docker_image_copies_reference_data() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert "COPY data/reference ./data/reference" in dockerfile
    for source_type in ("news", "disclosure"):
        assert (
            f"COPY reports/k-fnspid-impact-{source_type}-training-report.json "
            f"./reports/k-fnspid-impact-{source_type}-training-report.json"
        ) in dockerfile
        assert (
            f"COPY reports/k-fnspid-impact-{source_type}-transformer-training-report.json "
            f"./reports/k-fnspid-impact-{source_type}-transformer-training-report.json"
        ) in dockerfile
    assert "chmod 0444 /app/reports/k-fnspid-impact-*-training-report.json" in dockerfile
    assert "chmod -R a+rX,go-w /app/src /app/reports /app/data/reference" in dockerfile
    assert "UV_COMPILE_BYTECODE=1" not in dockerfile
