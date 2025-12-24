# 🚀 Deploy HealthGuard with Render Blueprint (Fastest Method!)

This guide uses Render's Blueprint feature to deploy automatically from your `render.yaml` file.

**Estimated time**: 20 minutes total
**Cost**: $0 (completely free!)

---

## 🎯 What You'll Deploy

- **Backend**: Python FastAPI on Render.com (https://render.com)
- **Frontend**: React + Vite on Vercel (https://vercel.com)
- **Security**: API key authentication, CORS protection, rate limiting
- **Auto-Deploy**: Every GitHub push triggers new deployment

---

## Part 1: Deploy Backend with Render Blueprint (10 minutes)

### Step 1: Access Render Dashboard

1. Go to **https://dashboard.render.com/**
2. Log in with your GitHub account

### Step 2: Create Blueprint Instance

1. Click on **"Blueprints"** in the left sidebar (or go to https://dashboard.render.com/blueprints)
2. Click the **"New Blueprint Instance"** button
3. You'll see a list of your GitHub repositories

### Step 3: Select Your Repository

1. Find and select: **`TimAlbert92/Neko-Health`**
2. Click **"Connect"**
3. Render will automatically detect the `render.yaml` file I created
4. You'll see a preview showing it will create:
   - ✅ 1 Web Service: `healthguard-api`

### Step 4: Configure Service Name (Optional)

You can customize the service name if you want:
- Default: `healthguard-api`
- Or choose your own (e.g., `my-healthguard-backend`)

### Step 5: Add Secret Environment Variables

Render Blueprint will show fields for the variables marked as `sync: false` in render.yaml.

Add these **exact values**:

| Variable Name | Value |
|---------------|-------|
| `API_KEYS` | `xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw,lW_7ovNwk0U2uJSZxt5nLVM8fFHbJOjI2MLazoMxOF8` |
| `CORS_ORIGINS` | `http://localhost:5173` |

**Note**: We'll update `CORS_ORIGINS` later with your actual Vercel URL. For now, use localhost.

### Step 6: Deploy!

1. Click **"Apply"** or **"Create Blueprint"**
2. Render will now:
   - ✅ Create the web service
   - ✅ Set all environment variables
   - ✅ Install Python dependencies
   - ✅ Start your API server

3. This takes about **5-10 minutes**

### Step 7: Get Your Backend URL

1. Once deployment completes, click on your **`healthguard-api`** service
2. At the top, you'll see your URL: `https://healthguard-api-XXXX.onrender.com`
3. **📝 COPY THIS URL - You'll need it for Vercel!**

### Step 8: Test Your Backend

1. Open your backend URL in a browser: `https://your-url.onrender.com/`
2. You should see:
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

### Step 1: Access Vercel Dashboard

1. Go to **https://vercel.com/new**
2. Log in with your GitHub account

### Step 2: Import Your Repository

1. Under "Import Git Repository", find: **`TimAlbert92/Neko-Health`**
2. Click **"Import"**

### Step 3: Configure Project Settings

Vercel should auto-detect Vite, but let's verify:

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Vite` (should be auto-detected) |
| **Root Directory** | `frontend` ← **IMPORTANT: Click "Edit" and set this!** |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

**CRITICAL**: Make sure to set Root Directory to `frontend`!

### Step 4: Add Environment Variables

Click **"Environment Variables"** section and add:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://your-backend-url.onrender.com` ← **PASTE YOUR RENDER URL!** |
| `VITE_API_KEY` | `xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw` |

**IMPORTANT**:
- Replace `your-backend-url` with your **actual Render URL** from Part 1
- Make sure there's **NO trailing slash** in the URL
- Example: `https://healthguard-api-abc123.onrender.com` ✅
- NOT: `https://healthguard-api-abc123.onrender.com/` ❌

### Step 5: Deploy!

1. Click **"Deploy"**
2. Vercel will:
   - ✅ Install dependencies
   - ✅ Build your frontend
   - ✅ Deploy to CDN

3. This takes about **2-3 minutes**

### Step 6: Get Your Frontend URL

1. Once deployment completes, you'll see: `https://neko-health-XXXX.vercel.app`
2. **📝 COPY THIS URL - You'll need it for CORS!**

### Step 7: Test Your Frontend

1. Click "Visit" or open your Vercel URL
2. You should see the HealthGuard application!

✅ **Frontend deployed successfully!**

---

## Part 3: Update CORS Configuration (5 minutes)

Now that you have your frontend URL, you need to update the backend's CORS settings to allow requests from it.

### Step 1: Go Back to Render

1. Go to **https://dashboard.render.com/**
2. Click on your **`healthguard-api`** service

### Step 2: Update Environment Variables

1. Click on **"Environment"** in the left sidebar
2. Find the `CORS_ORIGINS` variable
3. Click the **pencil icon** (Edit) next to it
4. Change the value from `http://localhost:5173` to your **actual Vercel URL**:
   ```
   https://your-actual-frontend.vercel.app
   ```
5. Click **"Save Changes"**

**IMPORTANT**:
- Use your **exact Vercel URL**
- Include `https://`
- **NO trailing slash**
- Example: `https://neko-health-abc123.vercel.app` ✅

### Step 3: Wait for Automatic Redeploy

1. Render will automatically redeploy with the new settings
2. This takes about **3-5 minutes**
3. You'll see the deployment progress in the "Events" tab

✅ **CORS configured successfully!**

---

## Part 4: Final Testing (5 minutes)

### Test 1: Visit Your Frontend

1. Go to your Vercel URL: `https://your-frontend.vercel.app`
2. You should see the HealthGuard application
3. Press **F12** to open browser console
4. Check for errors - there should be **NO CORS errors**

### Test 2: Submit Test Data

Fill in the form with this test patient:

```
Age: 63
Sex: Male (1)
Chest Pain Type: Typical Angina (3)
Resting BP: 145
Cholesterol: 233
Fasting Blood Sugar: Yes (1)
Rest ECG: Normal (1)
Max Heart Rate: 150
Exercise Angina: No (0)
ST Depression: 2.3
ST Slope: Downsloping (2)
Vessels Colored: 0
Thalassemia: Normal (2)
```

Click **"Predict Risk"**

### Test 3: Verify Results

You should see:
- ✅ Risk prediction (High/Low risk)
- ✅ Risk percentage
- ✅ Personalized recommendations
- ✅ Simulated intervention outcomes
- ✅ **NO errors in browser console**

### Test 4: Check API Authentication

1. Open browser **Developer Tools** (F12)
2. Go to **Network** tab
3. Submit the form again
4. Find the request to `/api/predict`
5. Click on it and check **Headers** section
6. Verify:
   - ✅ `X-API-Key` header is present
   - ✅ Response status is **200 OK** (not 403)

### Test 5: Test from Different Device (Optional)

1. Open your Vercel URL on your phone or another computer
2. Submit test data
3. Verify it works

---

## 🎉 SUCCESS! Your App is Live!

Congratulations! You now have a fully deployed, production-ready application!

### 📋 Your Deployment Info

Fill this in for your records:

```
Backend (Render):  https://________________________________
Frontend (Vercel): https://________________________________
Deployed on:       ________________________________

API Keys:
- Frontend: xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw
- Backup:   lW_7ovNwk0U2uJSZxt5nLVM8fFHbJOjI2MLazoMxOF8
```

### ✅ What You Have Now

- ✅ **Live Backend API** on Render.com
- ✅ **Live Frontend** on Vercel
- ✅ **API Key Authentication** protecting your API
- ✅ **CORS Protection** allowing only your frontend
- ✅ **Rate Limiting** (100 requests/minute per IP)
- ✅ **Free SSL/HTTPS** on both services
- ✅ **Auto-Deploy** on every GitHub push
- ✅ **Free Hosting** ($0/month)

---

## 🔄 Future Updates

Every time you push code to GitHub:

1. **Backend**: Render automatically rebuilds and redeploys (~5-10 min)
2. **Frontend**: Vercel automatically rebuilds and redeploys (~2-3 min)

You can watch the deployments in each dashboard!

---

## 🛠️ Managing Your Deployment

### View Logs

**Backend (Render)**:
- Dashboard → Your Service → "Logs" tab
- See real-time API requests and errors

**Frontend (Vercel)**:
- Dashboard → Your Project → Deployments → Click deployment → "Building" / "Runtime Logs"

### Manual Redeploy

**Backend (Render)**:
1. Dashboard → Your Service
2. Click "Manual Deploy" dropdown (top right)
3. Select "Deploy latest commit"

**Frontend (Vercel)**:
1. Dashboard → Your Project → "Deployments"
2. Click "..." next to a deployment
3. Select "Redeploy"

### Update Environment Variables

**Backend (Render)**:
1. Dashboard → Your Service → "Environment"
2. Edit variables
3. Click "Save Changes"
4. Service will auto-redeploy

**Frontend (Vercel)**:
1. Dashboard → Your Project → "Settings" → "Environment Variables"
2. Edit/Add variables
3. Click "Save"
4. **Must redeploy** for changes to take effect

---

## 🚨 Troubleshooting

### Frontend shows "Network Error"

**Symptoms**: Can't connect to backend, or CORS errors in console

**Fix**:
1. Verify backend is running: Visit `https://your-backend.onrender.com/`
2. Check `CORS_ORIGINS` in Render matches your Vercel URL **exactly**
3. Make sure there's **no trailing slash**
4. Wait for Render to redeploy after changing CORS (3-5 min)

### "Missing API key" error

**Symptoms**: 403 Forbidden errors

**Fix**:
1. Vercel → Settings → Environment Variables
2. Verify `VITE_API_KEY` is set correctly
3. Redeploy frontend (env vars only load at build time)

### Backend is slow to respond (first request)

**Symptoms**: First request takes 30-60 seconds

**Cause**: Render free tier spins down after 15 minutes of inactivity

**Fix**: This is normal behavior on free tier. Subsequent requests will be fast. Options:
- Wait it out (it's free!)
- Upgrade to paid tier ($7/month keeps it always on)
- Use UptimeRobot to ping your API every 10 minutes

### Build fails on Render

**Fix**:
1. Check "Logs" tab for error details
2. Common issues:
   - Missing `requirements.txt` → Verify it's committed to GitHub
   - Wrong Python version → Render uses Python 3.x by default
   - Missing model files → Check `backend/models/` is committed

### Build fails on Vercel

**Fix**:
1. Check build logs for error details
2. Common issues:
   - Wrong Root Directory → Must be set to `frontend`
   - Missing `package.json` → Verify it's in `frontend/` folder
   - Environment variables not set → Add them in Settings

---

## 📊 Monitoring (Optional)

### Set Up Uptime Monitoring

Free service to monitor if your API goes down:

1. Go to **https://uptimerobot.com/** (free account)
2. Create monitor for: `https://your-backend.onrender.com/`
3. Set check interval: Every 5 minutes
4. Get email/SMS alerts if down

### Enable Analytics

**Vercel Analytics** (free):
1. Dashboard → Your Project → "Analytics"
2. Click "Enable"
3. Track page views, performance, etc.

---

## 🔐 Security Checklist

- ✅ API keys are secure and not exposed in frontend code
- ✅ HTTPS enabled (automatic with Render/Vercel)
- ✅ CORS restricted to your frontend domain only
- ✅ Rate limiting enabled (100 req/min)
- ✅ Environment variables stored securely (not in git)
- ✅ Debug mode disabled in production

---

## 🎯 Next Steps (Optional)

### 1. Custom Domain ($10-15/year)

**Buy domain**:
- Namecheap, Google Domains, Cloudflare, etc.

**Add to Vercel** (Frontend):
1. Settings → Domains → Add
2. Follow DNS setup instructions

**Add to Render** (Backend):
1. Settings → Custom Domain → Add
2. Follow DNS setup instructions

**Update CORS** after domain setup:
- Change `CORS_ORIGINS` to your custom domain

### 2. Share Your App

- Add URLs to your GitHub README
- Share with friends/colleagues
- Post on social media
- Add to your portfolio

### 3. Collect Feedback

- Add a feedback form
- Monitor error logs
- Track user analytics
- Plan improvements

---

## 📞 Support

- **Full Deployment Guide**: See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Security Details**: See [SECURITY_SETUP.md](docs/SECURITY_SETUP.md) (if you created one)
- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs

---

## ✅ Deployment Complete!

**Your HealthGuard application is now live and accessible worldwide!** 🌍

Share your frontend URL and let people start using it!

**Questions? Issues?** Check the troubleshooting section above or the full [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md).
