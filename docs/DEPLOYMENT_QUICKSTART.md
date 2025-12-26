# HealthGuard Production Deployment - Quick Start

This is a condensed version of the full security deployment guide. For detailed information, see [SECURITY_DEPLOYMENT.md](./SECURITY_DEPLOYMENT.md).

---

## Prerequisites Checklist

Before deploying to production:

- [ ] GitHub repository is clean (no secrets in history)
- [ ] Dependabot is enabled
- [ ] Secret scanning is enabled
- [ ] Local testing completed with staging keys

---

## Step-by-Step Deployment

### 1. Generate Production API Keys (5 minutes)

```bash
# Run on your local machine
python3 -c "import secrets; print('FRONTEND_KEY:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('BACKEND_KEY_1:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('BACKEND_KEY_2:', secrets.token_urlsafe(32))"
```

**Save these keys in your password manager immediately!**

---

### 2. Deploy Backend to Render (10 minutes)

1. **Create Web Service** on [Render Dashboard](https://dashboard.render.com/)
   - Connect your GitHub repository
   - Select "Docker" environment
   - Region: Oregon (or closest to users)
   - Plan: Free (or Starter for production)

2. **Set Environment Variables**:
   ```
   ENVIRONMENT=production
   API_KEY_ENABLED=true
   API_KEYS=BACKEND_KEY_1,BACKEND_KEY_2
   CORS_ORIGINS=https://PLACEHOLDER.vercel.app
   DEBUG=false
   RATE_LIMIT_ENABLED=true
   RATE_LIMIT_REQUESTS=100
   LOG_LEVEL=INFO
   ```

   Mark `API_KEYS` as **Secret** ✅

3. **Deploy** and wait for completion (5-10 minutes)

4. **Save Backend URL**: `https://healthguard-api-xxx.onrender.com`

---

### 3. Deploy Frontend to Vercel (5 minutes)

1. **Import Project** on [Vercel](https://vercel.com/new)
   - Connect GitHub repository
   - Framework Preset: Vite
   - Root Directory: `frontend`

2. **Set Environment Variables**:
   ```
   VITE_API_URL=https://healthguard-api-xxx.onrender.com
   VITE_API_KEY=FRONTEND_KEY
   ```

   Environment: **Production**

3. **Deploy** and wait for completion (2-3 minutes)

4. **Save Frontend URL**: `https://healthguard.vercel.app`

---

### 4. Update CORS (Critical!)

Go back to Render dashboard:

1. Navigate to your backend service
2. Go to **Environment** tab
3. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://healthguard.vercel.app
   ```
4. **Save Changes** (auto-redeploys backend)

---

### 5. Verify Deployment (5 minutes)

**Test Backend Health**:
```bash
curl https://healthguard-api-xxx.onrender.com/
```

Expected response:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "api_version": "1.0.0"
}
```

**Test API Key Authentication**:
```bash
# Should fail (no key)
curl -X POST https://healthguard-api-xxx.onrender.com/api/predict \
  -H "Content-Type: application/json"

# Should succeed (with key)
curl -X POST https://healthguard-api-xxx.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: FRONTEND_KEY" \
  -d '{"age": 50, "sex": 1, "cp": 3, "trestbps": 130, "chol": 250, "fbs": 0, "restecg": 1, "thalach": 150, "exang": 0, "oldpeak": 2.0, "slope": 2, "ca": 0, "thal": 3}'
```

**Test Frontend**:
1. Visit your frontend URL
2. Try making a risk prediction
3. Check browser console for errors
4. Verify data loads correctly

---

## Security Verification Checklist

After deployment, verify these security measures:

- [ ] **API Keys**: Production keys are set and different from staging
- [ ] **CORS**: Only your frontend domain is allowed
- [ ] **Debug Mode**: `DEBUG=false` in production
- [ ] **Rate Limiting**: Enabled and configured
- [ ] **Environment Variables**: All set correctly in Render/Vercel
- [ ] **No Secrets**: No API keys in frontend source code
- [ ] **HTTPS**: Both frontend and backend use HTTPS
- [ ] **GitHub Security**: Review Security tab for alerts

---

## Common Issues & Solutions

### Issue: "CORS policy" error in browser

**Solution**: Update `CORS_ORIGINS` in Render dashboard with your exact frontend URL (including https://)

---

### Issue: "Invalid API key" error

**Solution**:
1. Verify frontend `VITE_API_KEY` matches one of the backend `API_KEYS`
2. Check for extra spaces or quotes
3. Redeploy frontend after updating environment variables

---

### Issue: Backend returns 429 "Too Many Requests"

**Solution**: This is expected behavior! Rate limiting is working.
- Increase `RATE_LIMIT_REQUESTS` if needed
- Or implement request caching in frontend

---

### Issue: Frontend can't connect to backend

**Solution**:
1. Check `VITE_API_URL` is correct in Vercel
2. Verify backend is running (check Render logs)
3. Check for CORS errors in browser console

---

## Ongoing Maintenance

### Weekly
- Review Dependabot PRs
- Check GitHub Security tab

### Monthly
- Review Render logs for errors
- Check for outdated dependencies

### Quarterly
- Rotate API keys
- Update all dependencies
- Review security best practices

---

## Key Resources

| Resource | Link |
|----------|------|
| Render Dashboard | https://dashboard.render.com/ |
| Vercel Dashboard | https://vercel.com/dashboard |
| GitHub Security | https://github.com/[your-repo]/security |
| Full Security Guide | [SECURITY_DEPLOYMENT.md](./SECURITY_DEPLOYMENT.md) |

---

## API Key Rotation (When Needed)

1. Generate new keys:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Add new keys to `API_KEYS` in Render (keep old keys):
   ```
   OLD_KEY_1,OLD_KEY_2,NEW_KEY_1,NEW_KEY_2
   ```

3. Update frontend to use new key in Vercel

4. Wait 24-48 hours for caches to clear

5. Remove old keys from `API_KEYS` in Render

---

## Emergency Contacts

If you discover a security issue:

1. **Immediate**: Rotate compromised keys
2. **Immediate**: Update all deployments
3. **Within 24h**: Review logs for unauthorized access
4. **Within 48h**: Document incident and update procedures

---

**Deployment Time**: ~30 minutes
**Last Updated**: 2025-12-26
**Version**: 1.0.0

Need help? See the full [SECURITY_DEPLOYMENT.md](./SECURITY_DEPLOYMENT.md) guide.
