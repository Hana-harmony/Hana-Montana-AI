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
COPY releases ./releases
COPY scripts/train_kf_deberta_sentiment_v2.py ./scripts/train_kf_deberta_sentiment_v2.py
COPY scripts/train_kf_deberta_sentiment_v6.py ./scripts/train_kf_deberta_sentiment_v6.py
COPY scripts/train_kf_deberta_sentiment_v6_ablation.py ./scripts/train_kf_deberta_sentiment_v6_ablation.py
COPY scripts/train_kr_finbert_sc_sentiment_v6.py ./scripts/train_kr_finbert_sc_sentiment_v6.py
COPY scripts/lock_kf_deberta_sentiment_candidate.py ./scripts/lock_kf_deberta_sentiment_candidate.py
COPY scripts/evaluate_locked_kf_deberta_sentiment.py ./scripts/evaluate_locked_kf_deberta_sentiment.py
COPY scripts/promote_kf_deberta_sentiment_deployment.py ./scripts/promote_kf_deberta_sentiment_deployment.py
COPY scripts/attest_sentiment_candidate_git_commit.py ./scripts/attest_sentiment_candidate_git_commit.py
COPY scripts/generate_sentiment_cpu_runtime_parity.py ./scripts/generate_sentiment_cpu_runtime_parity.py
COPY scripts/verify_sentiment_release.py ./scripts/verify_sentiment_release.py
COPY scripts/activate_signed_sentiment_release.py ./scripts/activate_signed_sentiment_release.py
COPY data/reference ./data/reference
COPY reports/k-fnspid-impact-news-training-report.json ./reports/k-fnspid-impact-news-training-report.json
COPY reports/k-fnspid-impact-disclosure-training-report.json ./reports/k-fnspid-impact-disclosure-training-report.json
COPY reports/kf-deberta-sentiment-training-report.json ./reports/kf-deberta-sentiment-training-report.json
COPY reports/korean-finance-sentiment-benchmark.json ./reports/korean-finance-sentiment-benchmark.json
COPY reports/sentiment-stacker-training-report.json ./reports/sentiment-stacker-training-report.json
COPY reports/disclosure-importance-training-report.json ./reports/disclosure-importance-training-report.json
COPY reports/k-fnspid-impact-news-transformer-training-report.json ./reports/k-fnspid-impact-news-transformer-training-report.json
COPY reports/k-fnspid-impact-disclosure-transformer-training-report.json ./reports/k-fnspid-impact-disclosure-transformer-training-report.json

RUN find /app/src -type f \( -name '*.joblib' -o -name '*.safetensors' \) \
        -exec chmod 0444 {} + \
    && find /app/reports -type f -exec chmod 0444 {} + \
    && find /app/releases /app/scripts -type f -exec chmod 0444 {} + \
    && chmod 0444 /app/reports/k-fnspid-impact-*-training-report.json \
    && chmod -R a+rX,go-w /app/src /app/reports /app/data/reference \
    && chmod -R a+rX,go-w /app/releases /app/scripts

RUN uv sync --frozen --no-dev --extra transformer
RUN python -c "from transformers import AutoModel; from transformers import AutoTokenizer; model=AutoModel.from_pretrained('kakaobank/kf-deberta-base', revision='363b171d71443b0874b0bf9cea053eb5b1650633', trust_remote_code=False); tokenizer=AutoTokenizer.from_pretrained('kakaobank/kf-deberta-base', revision='363b171d71443b0874b0bf9cea053eb5b1650633', trust_remote_code=False); model.save_pretrained('/app/models/kf-deberta-base', safe_serialization=True); tokenizer.save_pretrained('/app/models/kf-deberta-base')"
RUN mkdir -p /app/.cache/.tesseract \
    && chown -R 65532:65532 /app/.cache \
    && chmod -R a+rX,go-w /app/models

ENV HOME=/app/.cache
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV TOKENIZERS_PARALLELISM=false
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

USER 65532:65532

EXPOSE 8000

CMD ["uvicorn", "hannah_montana_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
