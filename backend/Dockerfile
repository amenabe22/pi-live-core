# syntax=docker/dockerfile:1

# ---- Builder stage ----
FROM python:3.12.10-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    librdkafka-dev \
    cargo \
    rustc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN python3 -m venv /venv \
 && /venv/bin/pip install --upgrade pip wheel setuptools \
 && /venv/bin/pip install --no-cache-dir -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12.10-slim

WORKDIR /app
ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment from builder
COPY --from=builder /venv /venv

# Copy application source code
COPY src ./src

# Expose FastAPI port
EXPOSE 10000

# SSL-enabled Uvicorn command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--app-dir", "src", \
     "--ssl-keyfile", "/app/certs/broker.key", "--ssl-certfile", "/app/certs/broker.crt"]
