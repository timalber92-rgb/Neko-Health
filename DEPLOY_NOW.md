# 🚀 Deploy HealthGuard Now - Step-by-Step Guide

Your GitHub repository is connected to both Render.com and Vercel. Follow these exact steps to deploy:

---

## 📋 Pre-Deployment Information

**Your API Keys** (keep these secure!):
- Frontend Key: `xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw`
- Backup Key: `lW_7ovNwk0U2uJSZxt5nLVM8fFHbJOjI2MLazoMxOF8`

**GitHub Repository**: `https://github.com/TimAlbert92/Neko-Health.git`

---

## Part 1: Deploy Backend to Render.com (15 minutes)

### Step 1: Create New Web Service

1. Go to [https://dashboard.render.com/](https://dashboard.render.com/)
2. Click **"New +"** button → Select **"Web Service"**
3. Find your repository: **TimAlbert92/Neko-Health**
4. Click **"Connect"**

### Step 2: Configure the Service

Fill in these **exact** settings:

| Field | Value |
|-------|-------|
| **Name** | `healthguard-api` (or any name you prefer) |
| **Region** | Oregon (US West) - or closest to you |
| **Branch** | `main` |
| **Root Directory** | Leave empty |
| **Runtime** | `Python 3` |
| **Build Command** | `cd backend && pip install -r requirements.txt` |
| **Start Command** | `cd backend && python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

### Step 3: Add Environment Variables

Click **"Advanced"** → Scroll to **"Environment Variables"** → Add these **one by one**:

```bash
ENVIRONMENT=production
API_KEY_ENABLED=true
API_KEYS=xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw,lW_7ovNwk0U2uJSZxt5nLVM8fFHbJOjI2MLazoMxOF8
CORS_ORIGINS=http://localhost:5173
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
LOG_LEVEL=INFO
DEBUG=false
API_HOST=0.0.0.0
```

**IMPORTANT**: We'll update `CORS_ORIGINS` later with your actual Vercel URL!

### Step 4: Deploy!

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for the build to complete
3. Once done, you'll see your backend URL like: `https://healthguard-api-xxxx.onrender.com`

### Step 5: Save Your Backend URL

**📝 WRITE DOWN YOUR BACKEND URL**: `https://__________________.onrender.com`

You'll need this for the frontend!

### Step 6: Test the Backend

Open this URL in your browser:
```
https://YOUR-BACKEND-URL.onrender.com/
```

You should see:
```json
{
  "message": "HealthGuard API is running",
  "models_loaded": {
    "risk_predictor": true,
    "intervention_agent": true
  }
}
```

✅ **Backend deployed successfully!**

---

## Part 2: Deploy Frontend to Vercel (10 minutes)

### Step 1: Import Project

1. Go to [https://vercel.com/new](https://vercel.com/new)
2. Find your repository: **TimAlbert92/Neko-Health**
3. Click **"Import"**

### Step 2: Configure Build Settings

Fill in these settings:

| Field | Value |
|-------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` ← **Click "Edit" and set this!** |
| **Build Command** | `npm run build` (should auto-detect) |
| **Output Directory** | `dist` (should auto-detect) |
| **Install Command** | `npm install` (should auto-detect) |

### Step 3: Add Environment Variables

Click **"Environment Variables"** → Add these:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://YOUR-BACKEND-URL.onrender.com` ← **Use your actual Render URL!** |
| `VITE_API_KEY` | `xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw` |

**CRITICAL**: Replace `YOUR-BACKEND-URL` with your actual Render URL from Part 1!

### Step 4: Deploy!

1. Click **"Deploy"**
2. Wait 2-3 minutes for the build
3. You'll get a URL like: `https://neko-health-xxxx.vercel.app`

### Step 5: Save Your Frontend URL

**📝 WRITE DOWN YOUR FRONTEND URL**: `https://__________________.vercel.app`

✅ **Frontend deployed successfully!**

---

## Part 3: Update CORS Configuration (5 minutes)

Now that you have your frontend URL, you need to update the backend's CORS settings.

### Step 1: Go Back to Render

1. Go to [https://dashboard.render.com/](https://dashboard.render.com/)
2. Click on your **healthguard-api** service
3. Go to **"Environment"** tab

### Step 2: Update CORS_ORIGINS

1. Find the `CORS_ORIGINS` variable
2. Click **"Edit"**
3. Change the value to your Vercel URL:
   ```
   https://your-actual-frontend-url.vercel.app
   ```
4. Click **"Save Changes"**

### Step 3: Wait for Redeploy

Render will automatically redeploy with the new settings (takes ~3-5 minutes).

✅ **CORS configured!**

---

## Part 4: Test Everything (5 minutes)

### Test 1: Health Check

Open your frontend URL: `https://your-frontend.vercel.app`

You should see the HealthGuard application!

### Test 2: Submit Test Data

Fill in the form with test patient data:
- Age: 63
- Sex: Male
- Chest Pain Type: Typical Angina
- Resting BP: 145
- Cholesterol: 233
- Fasting Blood Sugar: Yes
- Rest ECG: Normal
- Max Heart Rate: 150
- Exercise Angina: No
- ST Depression: 2.3
- ST Slope: Downsloping
- Vessels Colored: 0
- Thalassemia: Normal

Click **"Predict Risk"**

### Test 3: Verify Results

You should see:
- ✅ Risk prediction (High/Low)
- ✅ Risk percentage
- ✅ Personalized recommendations
- ✅ Simulated intervention outcomes
- ✅ **NO ERRORS in browser console** (check with F12)

### Test 4: Check API Key Authentication

Open browser console (F12) → Network tab → Find the `/api/predict` request → Check headers:
- ✅ `X-API-Key` header should be present
- ✅ Response should be 200 OK (not 403)

---

## 🎉 SUCCESS! Your App is Live!

If all tests pass, you're done! Here's what you have:

✅ **Backend**: `https://your-backend.onrender.com`
✅ **Frontend**: `https://your-frontend.vercel.app`
✅ **API Authentication**: Enabled with secure keys
✅ **CORS**: Configured correctly
✅ **Rate Limiting**: 100 requests/minute
✅ **HTTPS**: Automatic SSL certificates
✅ **Auto-Deploy**: Push to GitHub → auto-redeploys

---

## 🛠️ Quick Reference Commands

### View Deployment Logs

**Render (Backend)**:
1. Go to dashboard → Your service → "Logs" tab

**Vercel (Frontend)**:
1. Go to dashboard → Your project → Click on deployment → "Building" tab

### Redeploy

**Render**: Dashboard → Service → "Manual Deploy" → "Deploy latest commit"
**Vercel**: Dashboard → Project → Deployments → Click "..." → "Redeploy"

### Update Environment Variables

**Render**: Dashboard → Service → "Environment" tab → Edit variables → Save
**Vercel**: Dashboard → Project → "Settings" → "Environment Variables"

**NOTE**: After changing env vars, you need to redeploy!

---

## 🚨 Troubleshooting

### Frontend shows "Network Error"

**Cause**: Backend not running or CORS issue

**Fix**:
1. Check backend is running: Visit `https://your-backend.onrender.com/`
2. Verify `CORS_ORIGINS` in Render matches your Vercel URL exactly (no trailing slash!)
3. Check browser console for specific error

### "Missing API key" error

**Cause**: Frontend environment variable not set

**Fix**:
1. Go to Vercel → Settings → Environment Variables
2. Verify `VITE_API_KEY` is set correctly
3. Redeploy the frontend

### Backend takes forever to load first time

**Cause**: Render free tier spins down after 15 min inactivity

**Fix**: This is normal! First request after inactivity takes 30-60 seconds. Subsequent requests are fast.

### Build fails on Render

**Cause**: Missing dependencies or wrong Python version

**Fix**:
1. Check logs in Render dashboard
2. Verify [requirements.txt](backend/requirements.txt) is committed
3. Check [backend/models/](backend/models/) directory exists

### Build fails on Vercel

**Cause**: Wrong root directory or missing dependencies

**Fix**:
1. Verify Root Directory is set to `frontend`
2. Check [package.json](frontend/package.json) is committed
3. Check build logs for specific error

---

## 📊 Monitor Your Deployment

### Backend Status
- **URL**: `https://your-backend.onrender.com/`
- **Logs**: Render Dashboard → Your Service → Logs

### Frontend Status
- **URL**: `https://your-frontend.vercel.app/`
- **Logs**: Vercel Dashboard → Your Project → Deployments

### Uptime Monitoring (Optional)

Set up free monitoring with [UptimeRobot](https://uptimerobot.com/):
1. Create free account
2. Add monitor for your backend URL
3. Get alerts if your API goes down

---

## 🔄 Future Updates

Whenever you push code to GitHub:
- ✅ Render auto-deploys backend (takes ~5-10 min)
- ✅ Vercel auto-deploys frontend (takes ~2-3 min)

You can watch the deployments in each dashboard!

---

## 🎯 Next Steps (Optional)

1. **Custom Domain** ($10-15/year)
   - Buy domain from Namecheap/Google Domains
   - Add to Vercel/Render in settings
   - Update CORS_ORIGINS

2. **Monitoring**
   - Set up UptimeRobot for uptime monitoring
   - Enable error tracking with Sentry

3. **Performance**
   - Monitor with Vercel Analytics
   - Optimize images and assets

4. **User Feedback**
   - Add Google Analytics
   - Add feedback form

---

## 📝 Your Deployment URLs

Fill these in as you deploy:

```
Backend (Render):  https://______________________
Frontend (Vercel): https://______________________
Deployed on:       ______________________
```

---

**Need help?** Check the full [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed troubleshooting!
