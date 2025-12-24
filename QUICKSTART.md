# HealthGuard Quick Start

Get HealthGuard running locally in 5 minutes.

---

## 🚀 Local Development Setup

### 1. Start Backend

```bash
cd backend
python -m uvicorn api.main:app --reload
```

Backend runs at: [http://localhost:8000](http://localhost:8000)

### 2. Start Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

Frontend runs at: [http://localhost:5173](http://localhost:5173)

### 3. Test It!

Open [http://localhost:5173](http://localhost:5173) and:
- Enter patient data
- Click "Analyze Risk"
- View predictions and recommendations

**No CORS errors or authentication errors should appear!**

---

## 🧪 Test API Authentication

Run the automated test script:

```bash
./test_staging.sh
```

This tests:
- ✓ Health check endpoint
- ✓ Authentication rejection (no API key)
- ✓ Authentication success (valid API key)
- ✓ Authentication rejection (invalid API key)

Or test manually with curl:

```bash
# Should FAIL (no API key)
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233, "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1}'

# Should SUCCEED (with API key)
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw" \
  -d '{"age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233, "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1}'
```

---

## 🔑 Your API Keys

Two keys have been generated for you:

```bash
# Frontend Key (already configured in .env)
xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw

# Backup Key
lW_7ovNwk0U2uJSZxt5nLVM8fFHbJOjI2MLazoMxOF8
```

**These are already configured in your `.env` files. No action needed!**

---

## 🌍 Production Deployment

For production deployment instructions, see [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md).

**Free hosting options**:
- **Backend**: Render.com
- **Frontend**: Vercel

---

## 📁 Current Configuration

Your project is configured with **three environments**:

| File | Environment | API Auth | Use For |
|------|-------------|----------|---------|
| `.env` (current) | Staging | ✅ Enabled | Local testing with security |
| `.env.staging` | Staging | ✅ Enabled | Template for staging |
| `.env.production` | Production | ✅ Enabled | Template for production |

**Currently active**: Staging environment (`.env`)

---

## 🔐 Security Features Active

✅ **API Key Authentication** - All prediction endpoints require valid API key
✅ **CORS Protection** - Only localhost origins allowed (update for production)
✅ **Rate Limiting** - 100 requests per minute per IP
✅ **Input Validation** - Pydantic models validate all inputs
✅ **Environment-based Config** - Separate configs for dev/staging/production

---

## 📚 More Documentation

- [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Production deployment
- [docs/SECURITY_SETUP.md](docs/SECURITY_SETUP.md) - Security configuration
- [README.md](README.md) - Full project documentation

---

## 🆘 Troubleshooting

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check `VITE_API_URL` in [frontend/.env:6](frontend/.env#L6)
- Open browser console for error details

### "Missing API key" error
- Verify `VITE_API_KEY` is set in [frontend/.env:10](frontend/.env#L10)
- Restart frontend dev server (Vite loads env vars at startup)
- Check network tab - `X-API-Key` header should be present

### CORS errors
- Verify backend CORS_ORIGINS includes `http://localhost:5173`
- Check [backend/.env:15](backend/.env#L15)
- Restart backend server after changing .env

### Models not loading
- Ensure you're in the backend directory when starting
- Verify model files exist in [backend/models/](backend/models/)
- Check [backend/data/processed/scaler.pkl](backend/data/processed/scaler.pkl) exists

---

## ✅ What's Already Done

You don't need to do any setup! Everything is ready:

- ✅ Secure API keys generated
- ✅ Staging environment configured
- ✅ Frontend updated to use API keys
- ✅ CORS configured for localhost
- ✅ Rate limiting enabled
- ✅ All security features active

Just run the commands above and you're good to go!

---

**Ready to deploy?** See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for production deployment instructions.
