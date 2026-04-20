# OS-APOW Workflow Orchestration Queue
# Production Dockerfile for FastAPI service

# Build stage
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system --no-cache -e .

# Production stage
FROM python:3.12-slim AS production

# Create non-root user
RUN groupadd -r woq && useradd -r -g woq woq

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=woq:woq src/ ./src/
COPY --chown=woq:woq pyproject.toml ./

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Switch to non-root user
USER woq

# Expose port
EXPOSE 8000

# Health check using Python stdlib
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "workflow_orchestration_queue.main:app", "--host", "0.0.0.0", "--port", "8000"]
