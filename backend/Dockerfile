FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    default-mysql-client \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY README.md ./

RUN pip install --upgrade pip \
    && pip install cryptography \
    && pip install -e .

COPY . .

EXPOSE 8000
