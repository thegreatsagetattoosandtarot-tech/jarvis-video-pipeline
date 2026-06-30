# J.A.R.V.I.S. OS - Dockerfile for Fly.io
# Multi-stage build for smaller production image

# =========================================================================
# BASE STAGE - System dependencies
# =========================================================================
FROM python:3.13-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Audio for voice pipeline
    portaudio19-dev \
    libasound2-dev \
    libsndfile1 \
    ffmpeg \
    # Build tools
    build-essential \
    git \
    curl \
    # SSL for certs
    ca-certificates \
    && rm -rf /var/lib/apt/lists/lists/*

# Create non-root user
RUN groupadd -r jarvis && useradd -r -g jarvis -d /home/jarvis -m jarvis

# =========================================================================
# BUILD STAGE - Install Python dependencies
# =========================================================================
FROM base AS builder

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /opt/data/JARVIS_OS

# Copy dependency files first (for cache)
COPY pyproject.toml setup.py requirements*.txt ./

# Install Python dependencies
RUN uv pip install --system --no-cache -r requirements.txt 2>/dev/null || \
    uv pip install --system --no-cache -e . 2>/dev/null || \
    pip install --no-cache-dir -r requirements.txt 2>/dev/null || \
    pip install --no-cache-dir -e .

# =========================================================================
# RUNTIME STAGE - Final image
# =========================================================================
FROM base AS runtime

WORKDIR /opt/data/JARVIS_OS

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=jarvis:jarvis . .

# Create required directories
RUN mkdir -p \
    logs \
    backups \
    vector_db/chroma_db \
    voice/models/porcupine \
    voice/models/whisper \
    voice/models/piper \
    voice/models/rvc \
    brains/obsidian/raw_data \
    brains/obsidian/clients \
    brains/obsidian/preferences \
    brains/holographic/case_studies \
    brains/holographic/scenarios \
    brains/holographic/historical_tasks \
    brains/holographic/outcomes \
    brains/holographic/applied_knowledge \
    config/ssh \
    && chown -R jarvis:jarvis /opt/data/JARVIS_OS

# Switch to non-root user
USER jarvis

# Expose ports
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command - starts all services via init script
CMD ["./scripts/startup/init_jarvis.sh", "start"]