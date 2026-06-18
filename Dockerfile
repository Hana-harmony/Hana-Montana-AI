FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:${PATH}"

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN uv sync --frozen --no-dev

USER 65532:65532

EXPOSE 8000

CMD ["uvicorn", "hannah_montana_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
