#!/bin/bash
set -euo pipefail

echo "🚀 Starting backend service..."

echo "⏳ Waiting for database..."
python -c "
import time
import psycopg2
from urllib.parse import urlparse
import os
import sys

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print('❌ DATABASE_URL not set')
    sys.exit(1)

result = urlparse(db_url)

max_attempts = 30
for attempt in range(max_attempts):
    try:
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        conn.close()
        print('✅ Database is ready!')
        break
    except psycopg2.OperationalError:
        if attempt == max_attempts - 1:
            print('❌ Database connection failed after 30 attempts')
            sys.exit(1)
        print(f'Attempt {attempt + 1}/{max_attempts}: Database not ready, waiting...')
        time.sleep(1)
"

echo "📦 Running database migrations..."
alembic upgrade head || echo "⚠️ Migrations failed or not configured"

echo "✅ Starting Uvicorn server..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --loop uvloop \
    --log-level info \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips='*'
