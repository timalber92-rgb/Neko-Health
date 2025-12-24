FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create directory for models if needed
RUN mkdir -p models data/processed

# Expose port
EXPOSE 8000

# Run application with PORT environment variable support
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
