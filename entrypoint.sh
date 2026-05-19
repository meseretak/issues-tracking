#!/bin/bash
# Awash Bank Issue Tracker — Docker Entrypoint
# Seeds the database if needed, then starts the server

set -e

echo "============================================"
echo "  Awash Bank Issue Tracker — Startup"
echo "============================================"

cd /app/backend

# Ensure data directory exists
mkdir -p /app/backend/data

# Run DB init + seed (idempotent — won't duplicate data on restart)
echo "[1/2] Initializing and seeding database..."
PYTHONIOENCODING=utf-8 python -c "
import asyncio, sys
sys.path.insert(0, '/app/backend')
from app.database import engine, Base
from app.seed import seed_database

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_database()

asyncio.run(init())
print('Database ready!')
" 2>&1 || echo "DB seed skipped (already seeded or seed not available)"

echo "[2/2] Starting Uvicorn server..."
exec python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --access-log \
    --log-level info
