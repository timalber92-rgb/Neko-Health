# 📋 HealthGuard Deployment Checklist

Use this checklist to track your deployment progress. Check off each item as you complete it.

---

## ✅ Pre-Deployment (Already Done!)

- [x] GitHub repository created and synced
- [x] Render.com account connected to GitHub
- [x] Vercel account connected to GitHub
- [x] API keys generated
- [x] Staging environment configured and tested
- [x] All code committed and pushed to GitHub

---

## 🔧 Backend Deployment (Render.com)

### Setup Web Service

- [ ] Go to https://dashboard.render.com/
- [ ] Click "New +" → "Web Service"
- [ ] Select repository: `TimAlbert92/Neko-Health`
- [ ] Click "Connect"

### Configure Service

- [ ] Name: `healthguard-api` (or your choice)
- [ ] Region: Oregon (US West) or closest to you
- [ ] Branch: `main`
- [ ] Runtime: `Python 3`
- [ ] Build Command: `cd backend && pip install -r requirements.txt`
- [ ] Start Command: `cd backend && python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- [ ] Plan: `Free`

### Add Environment Variables

Click "Advanced" → "Environment Variables" → Add each:

- [ ] `ENVIRONMENT=production`
- [ ] `API_KEY_ENABLED=true`
- [ ] `API_KEYS=xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw,lW_7ovNwk0U2uJSZxt5nLVM8fFHbJOjI2MLazoMxOF8`
- [ ] `CORS_ORIGINS=http://localhost:5173` (temporary - will update later)
- [ ] `RATE_LIMIT_ENABLED=true`
- [ ] `RATE_LIMIT_REQUESTS=100`
- [ ] `LOG_LEVEL=INFO`
- [ ] `DEBUG=false`
- [ ] `API_HOST=0.0.0.0`

### Deploy & Verify

- [ ] Click "Create Web Service"
- [ ] Wait for build to complete (5-10 minutes)
- [ ] **Write down backend URL**: `https://__________________.onrender.com`
- [ ] Test health endpoint: Visit `https://YOUR-URL.onrender.com/`
- [ ] Verify you see JSON response with `"message": "HealthGuard API is running"`

---

## 🎨 Frontend Deployment (Vercel)

### Import Project

- [ ] Go to https://vercel.com/new
- [ ] Select repository: `TimAlbert92/Neko-Health`
- [ ] Click "Import"

### Configure Build Settings

- [ ] Framework Preset: `Vite`
- [ ] Root Directory: `frontend` ← **IMPORTANT: Click Edit and set this!**
- [ ] Build Command: `npm run build` (auto-detected)
- [ ] Output Directory: `dist` (auto-detected)
- [ ] Install Command: `npm install` (auto-detected)

### Add Environment Variables

Click "Environment Variables" → Add:

- [ ] `VITE_API_URL` = `https://YOUR-BACKEND-URL.onrender.com` ← **Use your actual Render URL!**
- [ ] `VITE_API_KEY` = `xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw`

### Deploy & Verify

- [ ] Click "Deploy"
- [ ] Wait for build to complete (2-3 minutes)
- [ ] **Write down frontend URL**: `https://__________________.vercel.app`
- [ ] Visit your frontend URL
- [ ] Verify the HealthGuard UI loads

---

## 🔄 Update CORS Configuration

### Update Backend CORS

- [ ] Go back to Render Dashboard
- [ ] Click on your `healthguard-api` service
- [ ] Go to "Environment" tab
- [ ] Find `CORS_ORIGINS` variable
- [ ] Click "Edit"
- [ ] Update to: `https://your-actual-frontend-url.vercel.app`
- [ ] Click "Save Changes"
- [ ] Wait for automatic redeploy (3-5 minutes)

---

## 🧪 Testing

### Test 1: Health Check

- [ ] Visit `https://your-backend.onrender.com/`
- [ ] Verify JSON response shows models loaded

### Test 2: Frontend Loads

- [ ] Visit `https://your-frontend.vercel.app/`
- [ ] Verify HealthGuard UI appears
- [ ] Open browser console (F12)
- [ ] Verify no CORS errors

### Test 3: API Authentication

- [ ] Fill in patient data form
- [ ] Click "Predict Risk"
- [ ] Open Network tab (F12 → Network)
- [ ] Find `/api/predict` request
- [ ] Verify `X-API-Key` header is present
- [ ] Verify response is 200 OK

### Test 4: Full Workflow

Enter this test data:

- [ ] Age: 63
- [ ] Sex: Male
- [ ] Chest Pain: Typical Angina
- [ ] Resting BP: 145
- [ ] Cholesterol: 233
- [ ] Fasting Blood Sugar: Yes
- [ ] Rest ECG: Normal
- [ ] Max Heart Rate: 150
- [ ] Exercise Angina: No
- [ ] ST Depression: 2.3
- [ ] ST Slope: Downsloping
- [ ] Vessels Colored: 0
- [ ] Thalassemia: Normal

Click "Predict Risk" and verify:

- [ ] Risk prediction displays (High/Low)
- [ ] Risk percentage shows
- [ ] Recommendations appear
- [ ] Simulated outcomes display
- [ ] No errors in console

### Test 5: Rate Limiting (Optional)

- [ ] Run test script with your production URL
- [ ] Verify 101st request gets 429 error

---

## 📝 Record Your Deployment

Fill in these details:

```
Backend URL:  https://________________________________
Frontend URL: https://________________________________
Deployed on:  ______________________ (date)

API Keys:
- Frontend: xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw
- Backup:   lW_7ovNwk0U2uJSZxt5nLVM8fFHbJOjI2MLazoMxOF8
```

---

## 🎉 Post-Deployment

### Share Your App

- [ ] Share frontend URL with users
- [ ] Add URL to README
- [ ] Update GitHub repository description

### Monitor (Optional)

- [ ] Set up UptimeRobot monitoring
- [ ] Enable Vercel Analytics
- [ ] Review logs regularly

### Security Review

- [ ] Verify HTTPS is enabled (automatic with Render/Vercel)
- [ ] Confirm API keys are not exposed in frontend code
- [ ] Check CORS is restricted to your domain only
- [ ] Verify rate limiting is working

---

## 🆘 Troubleshooting

If anything doesn't work, check:

1. **CORS Errors**
   - [ ] Verify `CORS_ORIGINS` in Render matches Vercel URL exactly
   - [ ] No trailing slash in URL
   - [ ] Check backend logs in Render

2. **API Key Errors**
   - [ ] Verify `VITE_API_KEY` is set in Vercel
   - [ ] Check Network tab shows `X-API-Key` header
   - [ ] Redeploy frontend after adding env vars

3. **Build Failures**
   - [ ] Check build logs in Render/Vercel
   - [ ] Verify all files committed to GitHub
   - [ ] Check Root Directory is set to `frontend` in Vercel

4. **Model Not Found**
   - [ ] Verify `backend/models/` folder is in GitHub
   - [ ] Check `risk_predictor.pkl` exists
   - [ ] Check `intervention_agent.pkl` exists

See [DEPLOY_NOW.md](DEPLOY_NOW.md) for detailed troubleshooting!

---

## ✅ Deployment Complete!

When all items are checked, your deployment is complete! 🎉

**Your app is now live and accessible to the world!**

Next steps:
- Share your app
- Monitor usage
- Collect feedback
- Plan future enhancements

---

**Estimated Time**: 30-45 minutes total
**Cost**: $0 (completely free!)
