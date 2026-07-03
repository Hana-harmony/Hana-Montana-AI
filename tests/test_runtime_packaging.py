from pathlib import Path


def test_runtime_docker_image_copies_reference_data() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert "COPY data/reference ./data/reference" in dockerfile
    assert "UV_COMPILE_BYTECODE=1" not in dockerfile
