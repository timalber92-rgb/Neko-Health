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
