# ==============================================
# OPTIMIZED SINGLE-STAGE DOCKERFILE
# Reduces build time from 70+ min to 10-15 min
# ==============================================

FROM python:3.11-slim

# Build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install ONLY essential system dependencies (lightweight)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools (minimal)
    gcc \
    # Database
    libpq-dev \
    libpq5 \
    # Tesseract OCR (sin OpenCV pesado)
    tesseract-ocr \
    libtesseract-dev \
    # PDF processing
    poppler-utils \
    # Utilities
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create user and directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/chroma_db /app/uploads /app/logs && \
    chown -R appuser:appuser /app

WORKDIR /app

# Upgrade pip and install wheel for faster builds
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy and install Python dependencies
# This layer is cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]