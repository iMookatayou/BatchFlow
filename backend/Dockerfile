FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  bash curl \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml

RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir .

COPY . /app

RUN chmod +x /app/scripts/*.sh

EXPOSE 8000
