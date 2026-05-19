# Use high-performance slim Python build
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PORT=8000
# Production database path inside the Docker volume
ENV DATABASE_URL=sqlite+aiosqlite:////app/backend/data/awash_tracker.db

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install backend dependencies first (cached layer)
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend & frontend source files
COPY backend /app/backend
COPY frontend /app/frontend

# Copy and configure entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create persistent data and uploads directories
RUN mkdir -p /app/backend/data /app/uploads

# Health check — GH Actions deploy job uses this to verify startup
HEALTHCHECK --interval=15s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose server port
EXPOSE 8000

# Use entrypoint to seed DB then start server
ENTRYPOINT ["/entrypoint.sh"]
