# HealthGuard Deployment Guide

This guide walks you through deploying HealthGuard from local development to staging and production environments.

---

## Table of Contents

1. [Quick Start - Staging Environment](#quick-start---staging-environment)
2. [Environment Setup](#environment-setup)
3. [Free Hosting Options](#free-hosting-options)
4. [Production Deployment](#production-deployment)
5. [Testing Your Deployment](#testing-your-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start - Staging Environment

Get your staging environment running in 5 minutes:

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Copy staging configuration
cp .env.staging .env

# Start the backend server
python -m uvicorn api.main:app --reload
```

The backend will run on [http://localhost:8000](http://localhost:8000)

### Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Copy staging configuration
cp .env.staging .env

# Install dependencies (if not already done)
npm install

# Start the frontend dev server
npm run dev
```

The frontend will run on [http://localhost:5173](http://localhost:5173)

### Verify It Works

1. Open [http://localhost:5173](http://localhost:5173) in your browser
2. Enter patient data and submit
3. You should see risk predictions and recommendations
4. Check browser console - you should NOT see any CORS or API key errors

---

## Environment Setup

### Backend Configuration Files

We have three environment configurations:

| File | Purpose | API Auth | CORS | When to Use |
|------|---------|----------|------|-------------|
| `.env.example` | Template | Disabled | localhost | Reference only |
| `.env.staging` | Staging | **Enabled** | localhost | Local testing with security |
| `.env.production` | Production | **Enabled** | Your domain | Production deployment |

### Your API Keys

Two API keys have been generated for you:

```bash
# Frontend Key (use in .env)
xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw

# Backup Key (for testing/other clients)
lW_7ovNwk0U2uJSZxt5nLVM8fFHbJOjI2MLazoMxOF8
```

**IMPORTANT**: These keys are already configured in `.env.staging`. Keep them secure!

### Frontend Configuration

The frontend is already configured to include the API key automatically:

- [frontend/src/api/client.js:24](frontend/src/api/client.js#L24) - API key header automatically added
- [frontend/.env.staging:8](frontend/.env.staging#L8) - API key stored securely

---

## Free Hosting Options

You don't need to pay for hosting! Here are excellent free options:

### Backend Hosting

#### Option 1: Render.com (Recommended)

**Pros**: Easy setup, auto-deploys from GitHub, free SSL
**Cons**: Cold starts (spins down after inactivity)

**Setup Steps**:
1. Create account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new "Web Service"
4. Configure:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Select Python 3
5. Add environment variables from `.env.production`:
   - `ENVIRONMENT=production`
   - `API_KEY_ENABLED=true`
   - `API_KEYS=your_keys_here`
   - `CORS_ORIGINS=https://your-frontend-domain.com`

#### Option 2: Railway.app

**Pros**: Easy setup, generous free tier
**Cons**: Limited free hours per month

**Setup Steps**:
1. Create account at [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Railway auto-detects Python app
4. Add environment variables from `.env.production`

#### Option 3: Fly.io

**Pros**: Good performance, easy CLI
**Cons**: Requires credit card (but won't charge)

**Setup Steps**:
1. Install flyctl: `brew install flyctl` or see [fly.io/docs](https://fly.io/docs/hands-on/install-flyctl/)
2. `cd backend && fly launch`
3. Configure environment variables: `fly secrets set API_KEY_ENABLED=true ...`

### Frontend Hosting

#### Option 1: Vercel (Recommended)

**Pros**: Perfect for Vite/React, auto-deploys, free SSL
**Cons**: None for this use case

**Setup Steps**:
1. Create account at [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add environment variables:
   - `VITE_API_URL=https://your-backend-url.render.com`
   - `VITE_API_KEY=xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw`

#### Option 2: Netlify

**Pros**: Easy setup, good free tier
**Cons**: Similar to Vercel

**Setup Steps**:
1. Create account at [netlify.com](https://www.netlify.com)
2. Connect GitHub repository
3. Configure build settings (same as Vercel)
4. Add environment variables

#### Option 3: GitHub Pages (Static Only)

**Pros**: Free, integrated with GitHub
**Cons**: Requires manual deployment, environment variables need build-time setup

---

## Production Deployment

Once you have your hosting set up, follow this checklist:

### Pre-Deployment Checklist

- [ ] **Get Your Domain URLs**
  - [ ] Backend URL (e.g., `https://api-healthguard.render.com`)
  - [ ] Frontend URL (e.g., `https://healthguard.vercel.app`)

- [ ] **Update Backend `.env` (or hosting environment variables)**
  ```bash
  ENVIRONMENT=production
  API_KEY_ENABLED=true
  API_KEYS=xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw,lW_7ovNwk0U2uJSZxt5nLVM8fFHbJOjI2MLazoMxOF8
  CORS_ORIGINS=https://healthguard.vercel.app
  RATE_LIMIT_ENABLED=true
  RATE_LIMIT_REQUESTS=100
  LOG_LEVEL=INFO
  ```

- [ ] **Update Frontend `.env` (or hosting environment variables)**
  ```bash
  VITE_API_URL=https://api-healthguard.render.com
  VITE_API_KEY=xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw
  ```

- [ ] **Security Verification**
  - [ ] Verify API key authentication is working
  - [ ] Test CORS with your actual frontend domain
  - [ ] Verify rate limiting is enabled
  - [ ] Check that HTTPS is enabled (hosting platforms do this automatically)

- [ ] **Test All Features**
  - [ ] Health check endpoint: `GET /`
  - [ ] Risk prediction: `POST /api/predict`
  - [ ] Recommendations: `POST /api/recommend`
  - [ ] Simulation: `POST /api/simulate`

### Deployment Commands

Most hosting platforms auto-deploy when you push to GitHub. If doing manual deployment:

```bash
# Commit and push your changes
git add .
git commit -m "Configure for production deployment"
git push origin main

# Your hosting platform (Vercel/Render/etc.) will auto-deploy
```

---

## Testing Your Deployment

### 1. Test Backend Health

```bash
curl https://your-backend-url.render.com/
```

Expected response:
```json
{
  "message": "HealthGuard API is running",
  "models_loaded": {
    "risk_predictor": true,
    "intervention_agent": true
  }
}
```

### 2. Test API Key Authentication

```bash
# Should FAIL (no API key)
curl -X POST https://your-backend-url.render.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 63, "sex": 1, "cp": 3, ...}'

# Should SUCCEED (with API key)
curl -X POST https://your-backend-url.render.com/api/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw" \
  -d '{"age": 63, "sex": 1, "cp": 3, ...}'
```

### 3. Test CORS

Open your frontend URL in a browser and check:
- [ ] No CORS errors in browser console
- [ ] API requests succeed
- [ ] Risk predictions display correctly

### 4. Test Rate Limiting

```bash
# Send 101 requests quickly
for i in {1..101}; do
  curl -X POST https://your-backend-url.render.com/api/predict \
    -H "X-API-Key: your_key" \
    -H "Content-Type: application/json" \
    -d '{"age": 63, ...}' &
done
```

The 101st request should return `429 Too Many Requests`.

---

## Troubleshooting

### Issue: "Missing API key" error

**Cause**: Frontend not sending API key

**Solution**:
1. Verify `VITE_API_KEY` is set in frontend environment
2. Restart frontend dev server (Vite only loads env vars at startup)
3. Check browser network tab - `X-API-Key` header should be present

### Issue: CORS errors

**Cause**: Backend CORS configuration doesn't match frontend domain

**Solution**:
1. Get your exact frontend URL (including https://)
2. Update backend `CORS_ORIGINS` to match exactly
3. No trailing slashes!
4. Restart backend server

### Issue: "Model not found" error

**Cause**: ML models not uploaded to hosting platform

**Solution**:
1. Ensure `backend/models/` directory is committed to git
2. Check model files exist: `risk_predictor.pkl`, `intervention_agent.pkl`
3. Verify `backend/data/processed/scaler.pkl` exists

### Issue: Cold starts on Render.com

**Cause**: Free tier spins down after 15 minutes of inactivity

**Solution**:
- First request after inactivity may take 30-60 seconds
- Consider upgrading to paid tier for production
- Or use a service like UptimeRobot to ping your API every 10 minutes

### Issue: Environment variables not updating

**Cause**: Hosting platform needs rebuild

**Solution**:
- Redeploy on Vercel/Render after changing environment variables
- Or trigger manual deployment from dashboard

---

## Next Steps After Deployment

### Optional Improvements

1. **Custom Domain** (optional)
   - Buy a domain from Namecheap, Google Domains, etc.
   - Configure DNS in your hosting platform
   - Update CORS settings with new domain

2. **Monitoring** (recommended)
   - Set up [UptimeRobot](https://uptimerobot.com/) for uptime monitoring
   - Configure alerts for downtime
   - Monitor error logs in hosting dashboard

3. **Analytics** (optional)
   - Add Google Analytics to frontend
   - Track API usage and errors
   - Monitor user behavior

4. **Performance** (optional)
   - Implement caching for frequently requested predictions
   - Optimize model loading
   - Add CDN for frontend assets

5. **User Authentication** (future phase)
   - Implement user accounts
   - Store patient data securely
   - Add role-based access control

---

## Security Best Practices

- ✅ **API Keys**: Rotate every 90 days
- ✅ **HTTPS**: Always use HTTPS in production (hosting platforms provide free SSL)
- ✅ **CORS**: Never use wildcards in production
- ✅ **Secrets**: Never commit `.env` files to git
- ✅ **Rate Limiting**: Monitor and adjust based on usage
- ✅ **Logging**: Review logs regularly for suspicious activity
- ✅ **Updates**: Keep dependencies updated (run `npm audit` and `pip audit` regularly)

---

## Support

- **Documentation**: [SECURITY_SETUP.md](SECURITY_SETUP.md)
- **GitHub Issues**: Report bugs and issues
- **Email**: [Your support email]

---

## Summary

You're all set! Here's what we configured:

1. ✅ Generated secure API keys
2. ✅ Created `.env.staging` for local testing with security enabled
3. ✅ Updated frontend to automatically include API key
4. ✅ Configured CORS for security
5. ✅ Enabled rate limiting

**To deploy:**
1. Choose hosting platforms (Render + Vercel recommended)
2. Update environment variables with your deployment URLs
3. Push to GitHub - auto-deployment handles the rest!

**Your next immediate steps:**
1. Test staging locally: `cp .env.staging .env` in both backend and frontend
2. Choose hosting platforms from the options above
3. Deploy and test in production
4. Share your app with the world!
