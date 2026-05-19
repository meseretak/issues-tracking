# Use high-performance slim Python build
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install backend dependencies first (cached layer)
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend & frontend source files
COPY backend /app/backend
COPY frontend /app/frontend

# Create directory for file uploads
RUN mkdir -p /app/uploads

# Expose server port
EXPOSE 8000

# Run FastAPI using high-performance Uvicorn configuration
WORKDIR /app/backend
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
