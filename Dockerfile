FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgl1 \
        libgomp1 \
        libxcb1 \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-kor \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY data/reference ./data/reference
COPY reports/k-fnspid-impact-training-report.json ./reports/k-fnspid-impact-training-report.json
COPY reports/kf-deberta-sentiment-training-report.json ./reports/kf-deberta-sentiment-training-report.json
COPY reports/korean-finance-sentiment-benchmark.json ./reports/korean-finance-sentiment-benchmark.json
COPY reports/sentiment-stacker-training-report.json ./reports/sentiment-stacker-training-report.json
COPY reports/disclosure-importance-training-report.json ./reports/disclosure-importance-training-report.json
COPY reports/k-fnspid-transformer-training-report.json ./reports/k-fnspid-transformer-training-report.json

RUN find /app/src -type f \( -name '*.joblib' -o -name '*.safetensors' \) \
        -exec chmod 0444 {} + \
    && find /app/reports -type f -exec chmod 0444 {} + \
    && chmod 0444 /app/reports/k-fnspid-impact-training-report.json \
    && chmod -R a+rX,go-w /app/src /app/reports /app/data/reference

RUN uv sync --frozen --no-dev --extra transformer
RUN python -c "from transformers import AutoModel; from transformers import AutoTokenizer; model=AutoModel.from_pretrained('kakaobank/kf-deberta-base', revision='363b171d71443b0874b0bf9cea053eb5b1650633', trust_remote_code=False); tokenizer=AutoTokenizer.from_pretrained('kakaobank/kf-deberta-base', revision='363b171d71443b0874b0bf9cea053eb5b1650633', trust_remote_code=False); model.save_pretrained('/app/models/kf-deberta-base', safe_serialization=True); tokenizer.save_pretrained('/app/models/kf-deberta-base')"
RUN mkdir -p /app/.cache/.tesseract \
    && chown -R 65532:65532 /app/.cache \
    && chmod -R a+rX,go-w /app/models

ENV HOME=/app/.cache
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

USER 65532:65532

EXPOSE 8000

CMD ["uvicorn", "hannah_montana_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
