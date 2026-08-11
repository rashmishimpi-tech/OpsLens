FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

CMD ["uv", "run", "uvicorn", "opslens.main:app", "--host", "0.0.0.0", "--port", "8000"]