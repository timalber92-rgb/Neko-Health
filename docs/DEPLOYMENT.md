# HealthGuard Deployment Guide

This guide covers deployment strategies for the HealthGuard application, from local development to production deployment.

---

## Table of Contents

- [Development Environment](#development-environment)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## Development Environment

### Using DevContainer (Recommended)

The easiest way to get started is using the provided DevContainer configuration:

1. **Prerequisites**:
   - Docker Desktop installed and running
   - VSCode with Remote - Containers extension

2. **Setup**:
   ```bash
   # Open project in VSCode
   code healthguard/

   # Press F1 and select "Dev Containers: Reopen in Container"
   # Wait for container to build (first time only, ~2-3 minutes)
   ```

3. **Verify Setup**:
   ```bash
   # In VSCode terminal
   python --version  # Should show Python 3.11+
   node --version    # Should show Node.js 18+
   ```

### Manual Setup

If you prefer not to use DevContainer:

#### Backend Setup

```bash
# Navigate to backend
cd healthguard/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development/testing

# Verify installation
python -c "import fastapi; print('FastAPI installed')"
```

#### Frontend Setup

```bash
# Navigate to frontend
cd healthguard/frontend

# Install dependencies
npm install

# Verify installation
npm list react
```

---

## Testing

### Running Tests

```bash
# Navigate to backend
cd healthguard/backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run all tests
pytest

# Run with coverage report
pytest --cov

# Run specific test file
pytest tests/test_risk_predictor.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test Coverage

```bash
# Generate HTML coverage report
pytest --cov --cov-report=html

# Open report in browser
open htmlcov/index.html  # On macOS
# Or navigate to htmlcov/index.html in file browser
```

### Continuous Integration

The project includes a basic test configuration. For CI/CD with GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        cd backend
        pytest --cov

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Docker Deployment

### Docker Compose (Local/Development)

Create `docker-compose.yml` in the project root:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./backend:/app
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host
```

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for models
RUN mkdir -p models data/processed

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files first (for layer caching)
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run development server
CMD ["npm", "run", "dev", "--", "--host"]
```

### Running with Docker Compose

```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose up --build backend
```

---

## Production Deployment

### Backend Production Setup

#### 1. Production Dockerfile

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/')"

# Run with gunicorn for production
CMD ["gunicorn", "api.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

Add `gunicorn` to `requirements.txt`:
```
gunicorn==21.2.0
```

#### 2. Frontend Production Build

Create `frontend/Dockerfile.prod`:

```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

Create `frontend/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        # Enable gzip compression
        gzip on;
        gzip_vary on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

        # Cache static assets
        location /assets {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # SPA routing - serve index.html for all routes
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Proxy API requests to backend
        location /api {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    environment:
      - LOG_LEVEL=info
      - WORKERS=4
    volumes:
      - ./backend/models:/app/models:ro
      - ./backend/data/processed:/app/data/processed:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 3s
      retries: 3
    networks:
      - healthguard-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - healthguard-network

networks:
  healthguard-network:
    driver: bridge
```

### Deploying to Cloud Platforms

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p docker healthguard

# Create environment and deploy
eb create healthguard-prod

# Deploy updates
eb deploy
```

#### Google Cloud Run

```bash
# Build and push backend image
gcloud builds submit --tag gcr.io/PROJECT_ID/healthguard-backend ./backend

# Deploy backend
gcloud run deploy healthguard-backend \
  --image gcr.io/PROJECT_ID/healthguard-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Build and push frontend image
gcloud builds submit --tag gcr.io/PROJECT_ID/healthguard-frontend ./frontend

# Deploy frontend
gcloud run deploy healthguard-frontend \
  --image gcr.io/PROJECT_ID/healthguard-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Heroku

```bash
# Login to Heroku
heroku login

# Create apps
heroku create healthguard-backend
heroku create healthguard-frontend

# Deploy backend
cd backend
git push heroku main

# Deploy frontend
cd ../frontend
git push heroku main
```

---

## Environment Variables

### Backend Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Application Settings
APP_NAME=HealthGuard
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=info

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4

# CORS Settings (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Model Settings
MODEL_DIR=./models
DATA_DIR=./data

# Security
SECRET_KEY=your-secret-key-here  # Change in production!
```

### Frontend Environment Variables

Create `.env` file in `frontend/` directory:

```bash
# API URL
VITE_API_URL=http://localhost:8000

# Production
# VITE_API_URL=https://api.yourdomain.com
```

---

## Monitoring and Logging

### Application Logging

The backend uses Python's logging module. Configure in `api/main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('healthguard.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks

The API includes a health check endpoint at `GET /`. Monitor it:

```bash
# Simple monitoring script
while true; do
  curl -f http://localhost:8000/ || echo "API is down!"
  sleep 60
done
```

### Performance Monitoring

For production, consider adding monitoring tools:

- **Prometheus + Grafana**: Metrics collection and visualization
- **Sentry**: Error tracking and reporting
- **New Relic** or **DataDog**: Application performance monitoring

Example Prometheus metrics endpoint:

```python
# In api/main.py
from prometheus_client import Counter, Histogram, make_asgi_app

# Metrics
prediction_counter = Counter('predictions_total', 'Total predictions made')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## Security Considerations

### 1. API Security

```python
# In api/main.py

# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/predict")
@limiter.limit("10/minute")
async def predict_risk(request: Request, patient: PatientInput):
    ...
```

### 2. HTTPS/TLS

Use a reverse proxy (nginx, Caddy) for TLS termination:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Secrets Management

Never commit secrets to Git. Use environment variables or secret management services:

- **AWS Secrets Manager**
- **Google Cloud Secret Manager**
- **HashiCorp Vault**
- **Azure Key Vault**

### 4. Input Validation

All inputs are validated via Pydantic models. Ensure models are comprehensive.

### 5. CORS Configuration

In production, restrict CORS to specific origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Common Issues

#### 1. Models Not Loading

**Symptom**: API returns 503 errors, logs show "Model not found"

**Solution**:
```bash
# Train models
cd backend
python -m ml.risk_predictor
python -m ml.rl_agent

# Verify models exist
ls models/
# Should show: risk_predictor.pkl, intervention_agent.pkl
```

#### 2. Import Errors

**Symptom**: `ModuleNotFoundError` when running tests or API

**Solution**:
```bash
# Ensure you're in the backend directory and venv is activated
cd backend
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. CORS Errors in Frontend

**Symptom**: Browser console shows CORS errors when calling API

**Solution**:
```python
# In api/main.py, ensure CORS middleware is configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. Port Already in Use

**Symptom**: `Address already in use` when starting server

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn api.main:app --port 8001
```

#### 5. Frontend Not Connecting to API

**Symptom**: Frontend shows "Network Error" or "Failed to fetch"

**Solution**:
```bash
# Check API is running
curl http://localhost:8000/

# Verify API URL in frontend
# In frontend/.env
VITE_API_URL=http://localhost:8000

# Restart frontend
npm run dev
```

### Debugging

#### Enable Debug Mode

```python
# In api/main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with auto-reload
uvicorn api.main:app --reload --log-level debug
```

#### Check Logs

```bash
# View backend logs
tail -f backend/healthguard.log

# View Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## Backup and Recovery

### Backing Up Models

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup trained models
cp backend/models/*.pkl backups/$(date +%Y%m%d)/

# Backup with versioning
tar -czf backups/models-$(date +%Y%m%d-%H%M%S).tar.gz backend/models/
```

### Model Versioning

Consider using MLflow or DVC for model versioning:

```bash
# Install DVC
pip install dvc

# Track models
dvc add backend/models/risk_predictor.pkl
dvc add backend/models/intervention_agent.pkl

# Commit to Git
git add backend/models/*.pkl.dvc .dvc/
git commit -m "Update models"
```

---

## Performance Optimization

### Backend Optimization

1. **Use Production ASGI Server**:
   ```bash
   # Instead of uvicorn directly, use gunicorn
   gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

2. **Enable Caching**:
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def cached_prediction(patient_hash):
       # Cache predictions for repeated queries
       pass
   ```

3. **Connection Pooling**: Use connection pools for database connections (if added later)

### Frontend Optimization

1. **Build Optimization**:
   ```bash
   npm run build -- --mode production
   ```

2. **Enable Compression** in nginx (already in production nginx.conf)

3. **CDN**: Serve static assets from CDN in production

---

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use nginx or AWS ALB to distribute traffic
2. **Multiple Instances**: Run multiple backend replicas
3. **Database**: Add PostgreSQL for user data and prediction history
4. **Cache Layer**: Add Redis for frequently accessed data

### Vertical Scaling

1. **Increase Resources**: More CPU/RAM for model inference
2. **GPU Support**: For larger models, use GPU-enabled instances
3. **Model Optimization**: Quantization, pruning for faster inference

---

**For questions or issues, please refer to the main [README.md](../README.md) or open an issue on GitHub.**
