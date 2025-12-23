# HealthGuard Security Configuration Guide

This guide covers the security features implemented in HealthGuard and how to configure them for production deployment.

---

## Table of Contents

1. [Overview](#overview)
2. [Configuration System](#configuration-system)
3. [API Key Authentication](#api-key-authentication)
4. [CORS Configuration](#cors-configuration)
5. [Rate Limiting](#rate-limiting)
6. [Production Deployment Checklist](#production-deployment-checklist)
7. [Testing Security Features](#testing-security-features)
8. [Troubleshooting](#troubleshooting)

---

## Overview

HealthGuard implements multiple security layers to protect patient data and prevent unauthorized access:

- **Environment-based Configuration**: Centralized, validated configuration using pydantic-settings
- **API Key Authentication**: Optional authentication for all prediction endpoints
- **CORS Protection**: Environment-specific origin validation
- **Rate Limiting**: In-memory rate limiting to prevent DoS attacks
- **Input Validation**: Pydantic models validate all API inputs

---

## Configuration System

HealthGuard uses **pydantic-settings** for type-safe, validated configuration management.

### Configuration Files

- **`.env.example`**: Template with all available settings (safe to commit)
- **`.env`**: Local development configuration (DO NOT commit)
- **`.env.production`**: Production configuration template (DO NOT commit with secrets)

### Loading Configuration

Configuration is loaded from environment variables or `.env` file:

```python
from api.config import get_settings

settings = get_settings()
print(f"Environment: {settings.environment}")
print(f"CORS Origins: {settings.cors_origins_list}")
```

### Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment mode (development/staging/production) |
| `API_KEY_ENABLED` | `false` | Enable API key authentication |
| `CORS_ORIGINS` | `localhost:3000,localhost:5173` | Comma-separated allowed origins |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | `100` | Max requests per minute per IP |

---

## API Key Authentication

### Overview

API key authentication protects prediction endpoints from unauthorized access. When enabled, all requests to `/api/predict`, `/api/recommend`, and `/api/simulate` must include a valid API key.

### Enabling Authentication

1. **Generate Secure API Keys**:

```bash
# Generate a secure 32-character API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Configure in `.env`**:

```bash
API_KEY_ENABLED=true
API_KEYS=key1_here,key2_here,key3_here
```

3. **Restart the API**

### Making Authenticated Requests

Include the API key in the `X-API-Key` header:

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"age": 63, "sex": 1, ...}'
```

### Response Codes

- **200 OK**: Request authenticated and successful
- **401 Unauthorized**: Missing or invalid API key
- **429 Too Many Requests**: Rate limit exceeded

### Multiple API Keys

You can configure multiple API keys for different clients:

```bash
API_KEYS=frontend_key_abc123,mobile_key_def456,partner_key_ghi789
```

### Best Practices

- ✅ Use keys with at least 32 characters
- ✅ Generate keys using cryptographically secure random generators
- ✅ Rotate keys regularly (every 90 days recommended)
- ✅ Use different keys for different environments
- ✅ Store keys securely (environment variables, secrets manager)
- ❌ Never hardcode keys in source code
- ❌ Never commit keys to version control
- ❌ Never share keys in plain text (email, Slack, etc.)

---

## CORS Configuration

### Overview

Cross-Origin Resource Sharing (CORS) controls which frontend domains can access the API. Proper CORS configuration is **critical** for security.

### Development Configuration

For local development, allow localhost origins:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Production Configuration

**CRITICAL**: Never use wildcards (`*`) in production!

```bash
# ✅ CORRECT - Specific origins
CORS_ORIGINS=https://healthguard.example.com,https://app.healthguard.com

# ❌ WRONG - Allows any origin (security risk!)
CORS_ORIGINS=*
```

### Advanced CORS Settings

```bash
CORS_ORIGINS=https://healthguard.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,X-API-Key
```

### Testing CORS

To test CORS in production:

```bash
curl -X OPTIONS http://your-api.com/api/predict \
  -H "Origin: https://your-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

Check for `Access-Control-Allow-Origin` in the response headers.

---

## Rate Limiting

### Overview

Rate limiting prevents abuse and DoS attacks by limiting requests per IP address.

### Configuration

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100  # requests per minute per IP
```

### How It Works

- Tracks requests per IP address
- 60-second sliding window
- Returns `429 Too Many Requests` when limit exceeded
- Includes rate limit headers in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `Retry-After`: Seconds until limit resets

### Response Example

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
Retry-After: 60

{
  "detail": "Rate limit exceeded. Maximum 100 requests per minute."
}
```

### Production Considerations

The current implementation uses **in-memory** rate limiting, which works well for single instances. For production with multiple instances, consider:

- **Redis-based rate limiting** (recommended for multi-instance deployments)
- **API Gateway rate limiting** (AWS API Gateway, Kong, etc.)
- **CDN rate limiting** (Cloudflare, etc.)

### Adjusting Rate Limits

Adjust based on your use case:

```bash
# High traffic application
RATE_LIMIT_REQUESTS=500

# Low traffic / strict limits
RATE_LIMIT_REQUESTS=20

# Disable for testing
RATE_LIMIT_ENABLED=false
```

---

## Production Deployment Checklist

Before deploying to production, verify all security settings:

### ✅ Pre-Deployment Checklist

- [ ] **Environment Configuration**
  - [ ] Set `ENVIRONMENT=production`
  - [ ] Create `.env` file from `.env.production` template
  - [ ] Verify `.env` is in `.gitignore`

- [ ] **CORS Configuration**
  - [ ] Replace `CORS_ORIGINS` with actual frontend domain(s)
  - [ ] Remove localhost origins
  - [ ] Verify no wildcards (`*`) in production

- [ ] **API Key Authentication**
  - [ ] Set `API_KEY_ENABLED=true`
  - [ ] Generate secure API keys (minimum 32 characters)
  - [ ] Configure keys in `API_KEYS`
  - [ ] Distribute keys securely to clients
  - [ ] Document key rotation procedures

- [ ] **Rate Limiting**
  - [ ] Enable rate limiting: `RATE_LIMIT_ENABLED=true`
  - [ ] Set appropriate `RATE_LIMIT_REQUESTS` for your traffic
  - [ ] Consider Redis-backed rate limiting for multi-instance

- [ ] **HTTPS Configuration**
  - [ ] Ensure API is served over HTTPS
  - [ ] Configure SSL/TLS certificates
  - [ ] Redirect HTTP to HTTPS

- [ ] **Logging & Monitoring**
  - [ ] Set `LOG_LEVEL=INFO` or `WARNING`
  - [ ] Configure log aggregation (CloudWatch, DataDog, etc.)
  - [ ] Set up monitoring and alerts
  - [ ] Verify no sensitive data in logs

- [ ] **Testing**
  - [ ] Run full test suite: `pytest tests/`
  - [ ] Test API key authentication manually
  - [ ] Test CORS with actual frontend
  - [ ] Test rate limiting behavior
  - [ ] Verify all endpoints require authentication

---

## Testing Security Features

### Unit Tests

Run the test suite:

```bash
cd backend
pytest tests/ -v
```

Tests cover:
- Configuration loading
- API key validation
- Rate limiting logic
- All API endpoints

### Manual Testing

#### Test API Key Authentication

```bash
# Should fail (no API key)
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 63, ...}'

# Should succeed (with API key)
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key_here" \
  -d '{"age": 63, ...}'
```

#### Test Rate Limiting

```bash
# Send 101 requests quickly
for i in {1..101}; do
  curl -X POST http://localhost:8000/api/predict \
    -H "Content-Type: application/json" \
    -H "X-API-Key: your_key_here" \
    -d '{"age": 63, ...}' &
done
```

The 101st request should return `429 Too Many Requests`.

#### Test CORS

```bash
# From browser console on your frontend
fetch('http://your-api.com/api/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your_key_here'
  },
  body: JSON.stringify({age: 63, ...})
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

---

## Troubleshooting

### Common Issues

#### "Missing API key" error

**Problem**: API returns 401 with "Missing API key"

**Solution**:
1. Verify `API_KEY_ENABLED=true` in `.env`
2. Ensure `X-API-Key` header is included in request
3. Check API key is not empty or whitespace

#### "Invalid API key" error

**Problem**: API returns 401 with "Invalid API key"

**Solution**:
1. Verify API key matches one in `API_KEYS` setting
2. Check for extra spaces in API key
3. Verify `.env` file is loaded correctly
4. Restart API server after changing keys

#### CORS errors in browser

**Problem**: Browser console shows CORS error

**Solution**:
1. Verify frontend origin is in `CORS_ORIGINS`
2. Check for protocol mismatch (http vs https)
3. Verify no trailing slashes in origin URLs
4. Test with curl to isolate browser vs server issue

#### Rate limit exceeded immediately

**Problem**: First request returns 429

**Solution**:
1. Check if multiple API instances are running
2. Verify IP address detection (check `X-Forwarded-For` headers)
3. Clear rate limit by restarting server
4. Adjust `RATE_LIMIT_REQUESTS` if needed

#### Configuration not loading

**Problem**: Changes to `.env` not taking effect

**Solution**:
1. Restart the API server (settings loaded at startup)
2. Verify `.env` file is in correct directory
3. Check for syntax errors in `.env`
4. Use absolute paths if needed

---

## Security Best Practices

### General

- ✅ Always use HTTPS in production
- ✅ Keep pydantic-settings up to date
- ✅ Monitor authentication failures
- ✅ Implement logging and alerting
- ✅ Regular security audits
- ✅ Follow principle of least privilege

### API Keys

- ✅ Rotate keys every 90 days
- ✅ Use different keys per environment
- ✅ Revoke compromised keys immediately
- ✅ Monitor key usage patterns

### CORS

- ✅ Specify exact origins (no wildcards)
- ✅ Use HTTPS origins in production
- ✅ Review CORS configuration regularly

### Rate Limiting

- ✅ Monitor rate limit hits
- ✅ Adjust limits based on legitimate usage
- ✅ Consider per-user rate limits (not just per-IP)

---

## Additional Resources

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [pydantic-settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

## Support

For security issues, please contact: [security contact information]

For questions about configuration, see the main README or open an issue.
