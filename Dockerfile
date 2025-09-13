FROM python:3.12-slim

WORKDIR /app

# Устанавливаем uv
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./


RUN uv sync --frozen --no-dev

COPY . .


