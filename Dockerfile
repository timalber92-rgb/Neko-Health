# Dockerfile for Render deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend directory
COPY backend/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Render will override this with $PORT)
EXPOSE 8000

# Start command
CMD python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
