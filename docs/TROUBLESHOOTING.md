# Troubleshooting Guide

## Common Issues and Solutions

### Frontend Infinite Loading Loop (December 2025)

**Symptom**: The frontend at localhost:3000 shows an endless loading spinner or blank page, browser console may show CSS @import errors from browser extensions.

**Root Cause**: The `useEffect` hook in App.jsx was making an API health check on component mount. In the devcontainer environment, this was causing an infinite re-render loop, likely due to:
1. WebSocket HMR (Hot Module Replacement) connection issues in containerized environments
2. API health check failing or timing out
3. State updates triggering re-renders in a loop

**Solution Applied**:

1. **Removed API Health Check**: Removed the `useEffect` hook that called `checkHealth()` on component mount. The health check was non-essential for core functionality and was causing the render loop.

2. **Updated Vite Configuration** (`vite.config.js`):
   ```javascript
   server: {
     port: 3000,
     host: true,              // Expose to network (required for devcontainer)
     strictPort: true,         // Fail if port is already in use
     hmr: {
       clientPort: 3000,       // Explicit HMR port for container networking
     },
     // ... proxy config
   }
   ```

3. **Simplified App.jsx**: Removed the following from the original App component:
   - `apiHealth` state
   - `useEffect` for health check
   - API status indicator in header
   - Backend unavailable warning banner

**Files Modified**:
- `/workspace/frontend/src/App.jsx` - Removed health check logic
- `/workspace/frontend/vite.config.js` - Added `host: true` and HMR config

**Prevention**:
- Avoid `useEffect` hooks that make API calls on mount without proper error boundaries
- In devcontainer environments, always configure Vite with `host: true`
- Test frontend independently from backend before integrating API calls
- Use error boundaries to catch and handle component errors gracefully

**Backup**: The original App.jsx with health check is saved as `/workspace/frontend/src/App-original.jsx` for reference.

---

## DevContainer Networking

When running in a devcontainer:

1. **Frontend Server**: Must use `host: true` in vite.config.js to expose to network
2. **Port Forwarding**: VSCode automatically forwards ports, check the "Ports" panel
3. **Network URL**: Vite will show both localhost and network URLs (e.g., http://172.18.0.2:3000/)
4. **HMR WebSocket**: May need explicit `clientPort` configuration for hot reload to work

---

## Starting the Application

### Frontend (Port 3000)
```bash
cd /workspace/frontend
npm run dev
```

### Backend (Port 8000)
```bash
cd /workspace/backend
/workspace/backend/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
# OR if venv is activated:
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Accessing the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## CSS @import Errors from Browser Extensions

**Error**: "Define @import rules at the top of the stylesheet" from sources like "one-google-bar"

**Cause**: Browser extensions (Google toolbar, etc.) injecting their own stylesheets

**Solution**: This is a false positive and does not affect the application. Can be ignored or disable browser extensions temporarily to verify.

---

## Git Push Authentication Issues

**Symptom**: `git push` fails with "Repository not found" error even though the repository exists on GitHub.

**Error Message**:
```
remote: Repository not found.
fatal: repository 'https://github.com/timalber92-rgb/Neko-Health.git/' not found
```

**Root Cause**: The devcontainer environment doesn't have GitHub credentials configured. GitHub requires authentication to push to repositories, especially for private repos.

**Solutions**:

### Option 1: Use GitHub CLI (Recommended)
```bash
# Install GitHub CLI if not available
gh auth login
# Follow the prompts to authenticate
git push origin main
```

### Option 2: Use Personal Access Token (PAT)
1. Create a Personal Access Token on GitHub:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Copy the token

2. Configure Git credentials:
   ```bash
   git config --global credential.helper store
   git push origin main
   # When prompted, use your GitHub username and the PAT as password
   ```

### Option 3: Use SSH Keys (Working Solution for Private Repos)

This is the verified solution that works in the devcontainer environment:

1. **Generate SSH key** (if not already exists):
   ```bash
   ssh-keygen -t ed25519 -C "neko-health-devcontainer" -f ~/.ssh/id_ed25519 -N ""
   ```

2. **Start SSH agent and add the key**:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

3. **Display your public key**:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   Copy the entire output (starts with `ssh-ed25519`)

4. **Add the public key to GitHub**:
   - Go to: https://github.com/settings/ssh/new
   - Title: `Neko-Health DevContainer` (or any name)
   - Paste the public key into the "Key" field
   - Click "Add SSH key"

5. **Update remote URL to use SSH**:
   ```bash
   git remote set-url origin git@github.com:timalber92-rgb/Neko-Health.git
   git remote -v  # Verify the remote is set correctly
   ```

6. **Clear old SSH keys and ensure the new key is loaded**:
   ```bash
   ssh-add -D  # Remove all keys
   ssh-add ~/.ssh/id_ed25519  # Add the new key
   ssh-add -l  # Verify the correct key is loaded
   ```

7. **Push to GitHub**:
   ```bash
   git push origin main
   ```

### Troubleshooting SSH Key Issues

**Problem**: Push fails even after adding SSH key to GitHub

**Cause**: Multiple SSH keys in the agent, and Git is using the wrong one

**Solution**:
```bash
# Clear all SSH keys from the agent
ssh-add -D

# Add only the correct key
ssh-add ~/.ssh/id_ed25519

# Verify the correct key is loaded
ssh-add -l

# Should show: 256 SHA256:... neko-health-devcontainer (ED25519)

# Test GitHub connection
ssh -T git@github.com
# Should show: Hi timalber92-rgb/... You've successfully authenticated

# Now push
git push origin main
```

### Reconnecting Git Remote

If the remote connection is lost:
```bash
git remote remove origin
git remote add origin git@github.com:timalber92-rgb/Neko-Health.git
git remote -v  # Verify the remote is set correctly
```

**Repository URL**:
- HTTPS: https://github.com/timalber92-rgb/Neko-Health.git
- SSH: git@github.com:timalber92-rgb/Neko-Health.git (recommended)

**Note**: After authenticating and pushing successfully, Vercel will automatically detect the new commits and trigger a deployment to https://neko-health.vercel.app/

### Deployment Workflow

1. Make code changes locally
2. Commit changes: `git commit -am "your message"`
3. Push to GitHub: `git push origin main`
4. Vercel automatically detects the push and deploys (1-3 minutes)
5. Check deployment at https://neko-health.vercel.app/
