# HealthGuard Security Deployment Guide

## Overview
This guide covers the implementation of security recommendations from the security review. Follow these steps to ensure a secure production deployment.

---

## 1. Production CORS Configuration

### Current Status
- Backend CORS is set to placeholder values in `backend/.env.production`
- Must be updated before deploying to production

### Implementation Steps

#### Step 1: Deploy Frontend First
1. Deploy your frontend to Vercel/Netlify/other hosting
2. Note the production domain (e.g., `https://healthguard.vercel.app`)

#### Step 2: Update Backend CORS Settings
Edit `backend/.env.production` or set in Render dashboard:

```bash
# Single domain
CORS_ORIGINS=https://healthguard.vercel.app

# Multiple domains (production + staging)
CORS_ORIGINS=https://healthguard.vercel.app,https://staging.healthguard.vercel.app
```

#### Step 3: Render Dashboard Configuration
In Render dashboard for your backend service:
1. Go to **Environment** tab
2. Add/Update environment variable:
   - **Key**: `CORS_ORIGINS`
   - **Value**: Your actual frontend URL(s)
3. Click **Save Changes** (service will auto-redeploy)

### Verification
Test CORS configuration:
```bash
# Should succeed
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://your-api.onrender.com/api/predict

# Should fail (wrong origin)
curl -H "Origin: https://malicious-site.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://your-api.onrender.com/api/predict
```

---

## 2. API Key Management for Production

### Current Status
- API keys are placeholders in `.env.production`
- Staging keys exist in `.env.staging` (for local testing)
- Production keys must be set via Render dashboard

### Implementation Steps

#### Step 1: Generate Secure API Keys
On your local machine:
```bash
# Generate 3 production API keys
python3 -c "import secrets; print('KEY1:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('KEY2:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('KEY3:', secrets.token_urlsafe(32))"
```

**IMPORTANT**: Save these keys in a password manager (1Password, LastPass, etc.)

#### Step 2: Set Keys in Render Dashboard
1. Go to Render dashboard → Your backend service
2. Navigate to **Environment** tab
3. Add environment variable:
   - **Key**: `API_KEYS`
   - **Value**: `KEY1,KEY2,KEY3` (comma-separated, no spaces)
   - **Secret**: Check this box to hide the value
4. Click **Save Changes**

#### Step 3: Configure Frontend
1. In Vercel/Netlify dashboard:
2. Go to **Environment Variables**
3. Add variable:
   - **Key**: `VITE_API_KEY`
   - **Value**: One of your production API keys (KEY1)
   - **Environment**: Production
4. Redeploy frontend

### Key Rotation Strategy
- Maintain 2-3 active keys at all times
- To rotate keys:
  1. Generate new key
  2. Add to `API_KEYS` list (keep old keys)
  3. Update frontend to use new key
  4. Wait 24-48 hours for frontend caches to clear
  5. Remove old key from `API_KEYS` list

---

## 3. Deployment Checklist

### Pre-Deployment
- [ ] Frontend deployed and URL obtained
- [ ] Production API keys generated and stored securely
- [ ] CORS_ORIGINS updated with actual frontend domain
- [ ] API_KEY_ENABLED=true in production environment
- [ ] DEBUG=false in production environment
- [ ] Rate limiting configured (RATE_LIMIT_ENABLED=true)

### Render Backend Deployment
1. Connect GitHub repository to Render
2. Create new Web Service
3. Configure environment variables (see next section)
4. Deploy service
5. Verify health endpoint: `https://your-api.onrender.com/`

### Environment Variables for Render
Set these in Render dashboard:

| Variable | Value | Secret |
|----------|-------|--------|
| ENVIRONMENT | production | No |
| API_KEY_ENABLED | true | No |
| API_KEYS | [generated keys] | **Yes** |
| CORS_ORIGINS | https://your-frontend.com | No |
| DEBUG | false | No |
| RATE_LIMIT_ENABLED | true | No |
| RATE_LIMIT_REQUESTS | 100 | No |
| LOG_LEVEL | INFO | No |

### Frontend Environment Variables (Vercel/Netlify)

| Variable | Value | Environment |
|----------|-------|-------------|
| VITE_API_URL | https://your-api.onrender.com | Production |
| VITE_API_KEY | [one of your API keys] | Production |

---

## 4. Branch Protection (Optional but Recommended)

### GitHub Repository Settings
1. Go to repository **Settings** → **Branches**
2. Click **Add rule** for `main` branch
3. Configure protection rules:
   - [x] Require a pull request before merging
   - [x] Require approvals (1)
   - [x] Require status checks to pass before merging
   - [x] Require branches to be up to date before merging
   - [x] Do not allow bypassing the above settings

### Status Checks (after CI/CD setup)
- [ ] Backend tests passing
- [ ] Frontend build successful
- [ ] Dependency security check
- [ ] Code linting passing

---

## 5. Dependency Updates & Security Monitoring

### Automated Dependency Updates
GitHub Dependabot is already enabled and configured via `.github/dependabot.yml`.

**Current Configuration:**
- Checks for updates weekly
- Creates automatic PRs for security updates
- Monitors both Python and npm dependencies

### Manual Dependency Review
Check for outdated packages:

**Frontend:**
```bash
cd frontend
npm outdated
```

**Backend:**
```bash
cd backend
pip list --outdated
```

### Security Vulnerability Scanning
GitHub automatically scans for vulnerabilities via:
- Dependabot alerts (enabled)
- Secret scanning (enabled)
- Code scanning (optional - requires GitHub Actions)

**To view security alerts:**
1. Go to repository **Security** tab
2. Review **Dependabot alerts**
3. Review **Secret scanning alerts**
4. Review **Code scanning alerts** (if enabled)

---

## 6. Security Monitoring Checklist

### Weekly
- [ ] Review GitHub Security tab for new alerts
- [ ] Check Dependabot PRs and merge/test
- [ ] Review Render logs for suspicious activity
- [ ] Verify API rate limiting is working

### Monthly
- [ ] Review and update dependencies
- [ ] Audit API key usage
- [ ] Review CORS configuration
- [ ] Check for new security best practices

### Quarterly
- [ ] Rotate API keys
- [ ] Security audit of codebase
- [ ] Review and update security documentation
- [ ] Penetration testing (optional)

---

## 7. Local Development with Staging Keys

The staging environment files (`.env.staging`) contain test API keys for local development.

**Backend (.env.staging):**
```bash
cd backend
cp .env.staging .env
uvicorn api.main:app --reload
```

**Frontend (.env.staging):**
```bash
cd frontend
cp .env.staging .env.local
npm run dev
```

**IMPORTANT**:
- Never commit `.env` files to git
- Staging keys are for development/testing only
- Use production keys only in production environment

---

## 8. Incident Response

### If API Keys are Compromised
1. **Immediate**: Generate new keys
2. **Immediate**: Update Render dashboard with new keys
3. **Immediate**: Update frontend with new keys
4. **Immediate**: Remove compromised keys from `API_KEYS`
5. Review Render logs for unauthorized usage
6. Document incident and lessons learned

### If Secrets are Committed to Git
1. **Immediate**: Rotate all affected secrets
2. **Immediate**: Update all deployments
3. Use BFG Repo-Cleaner to remove from git history
4. Force push cleaned history (requires team coordination)
5. Notify team members to re-clone repository

---

## 9. Testing Production Security

### API Key Authentication Test
```bash
# Should fail (no API key)
curl -X POST https://your-api.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 50, "sex": 1, ...}'

# Should succeed (with valid key)
curl -X POST https://your-api.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_PRODUCTION_KEY" \
  -d '{"age": 50, "sex": 1, ...}'
```

### CORS Test
```bash
# Test from browser console on your frontend domain
fetch('https://your-api.onrender.com/api/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_KEY'
  },
  body: JSON.stringify({...})
}).then(r => r.json()).then(console.log)
```

### Rate Limiting Test
```bash
# Send 101 requests rapidly (100 is the limit)
for i in {1..101}; do
  curl -X GET https://your-api.onrender.com/ \
    -H "X-API-Key: YOUR_KEY"
done
# Request #101 should return 429 Too Many Requests
```

---

## 10. Compliance & Best Practices

### OWASP Top 10 Coverage
- [x] A01:2021 – Broken Access Control (API keys implemented)
- [x] A02:2021 – Cryptographic Failures (secrets in env vars)
- [x] A03:2021 – Injection (Pydantic validation)
- [x] A05:2021 – Security Misconfiguration (proper CORS)
- [x] A07:2021 – Identification and Authentication Failures (API key auth)
- [x] A09:2021 – Security Logging and Monitoring Failures (logging configured)

### HIPAA Considerations (if applicable)
This application processes health data. If deploying for real medical use:
- [ ] Ensure Render has BAA (Business Associate Agreement)
- [ ] Enable encryption at rest
- [ ] Implement audit logging
- [ ] Add user authentication (OAuth2/OIDC)
- [ ] Implement data retention policies
- [ ] Add data encryption for sensitive fields

**Note**: Current implementation is for demonstration/research purposes only.

---

## Support & Resources

### Documentation
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [OWASP Top 10](https://owasp.org/Top10/)

### Monitoring Tools
- [GitHub Security Advisories](https://github.com/advisories)
- [npm audit](https://docs.npmjs.com/cli/v10/commands/npm-audit)
- [pip-audit](https://pypi.org/project/pip-audit/)
- [Snyk](https://snyk.io/) (optional third-party)

### Contact
For security concerns, create an issue in the GitHub repository with the `security` label.

---

**Last Updated**: 2025-12-26
**Version**: 1.0.0
