FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 libgomp1 libxcb1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY data/reference ./data/reference

RUN uv sync --frozen --no-dev
RUN mkdir -p /app/.cache/.paddleocr \
    && chown -R 65532:65532 /app/.cache

ENV HOME=/app/.cache
ENV PADDLEOCR_HOME=/app/.cache/.paddleocr

USER 65532:65532

EXPOSE 8000

CMD ["uvicorn", "hannah_montana_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
