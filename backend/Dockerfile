# syntax=docker/dockerfile:1.4

FROM python:3.11-slim AS builder

LABEL maintainer="security@saascafeterias.com"
LABEL version="1.0.0"
LABEL description="Backend API - FastAPI Production Build"

ARG PYTHON_VERSION=3.11
ARG PIP_NO_CACHE_DIR=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 builder \
    && useradd --uid 1000 --gid builder --shell /bin/bash --create-home builder

WORKDIR /build

COPY --chown=builder:builder requirements.txt .

USER builder
RUN pip install --user --no-cache-dir --no-warn-script-location \
    -r requirements.txt

FROM python:3.11-slim AS runtime

LABEL maintainer="security@saascafeterias.com"
LABEL version="1.0.0"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN groupadd --gid 1000 saas \
    && useradd --uid 1000 --gid saas --shell /bin/bash --create-home saas

COPY --from=builder --chown=saas:saas /home/builder/.local /home/saas/.local

ENV PATH=/home/saas/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1

WORKDIR /app

COPY --chown=saas:saas ./app /app/app
COPY --chown=saas:saas ./alembic /app/alembic
COPY --chown=saas:saas ./alembic.ini /app/
COPY --chown=saas:saas ./prestart.sh /app/

RUN chmod +x /app/prestart.sh

USER saas

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["/app/prestart.sh"]