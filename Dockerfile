FROM python:3.12-slim

WORKDIR /app

# Системные зависимости (для сборки некоторых wheel'ов, если понадобится)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install --no-cache-dir poetry

# Сначала зависимости (чтобы работал docker cache)
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

# Потом код
COPY . /app

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "delivery_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
