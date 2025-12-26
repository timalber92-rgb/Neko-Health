# API Module

FastAPI application for the HealthGuard cardiovascular disease risk prediction API.

## Structure

- `main.py` - Main FastAPI application, routes, and endpoints
- `models.py` - Pydantic models for request/response validation
- `config.py` - Configuration management using pydantic-settings
- `auth.py` - API key authentication middleware
- `rate_limit.py` - Rate limiting middleware

## Running the API

```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

See `.env.example` in the backend directory for required configuration.

## API Documentation

When the API is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
