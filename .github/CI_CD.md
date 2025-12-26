# CI/CD Pipeline Documentation

This document explains the GitHub Actions workflows and automated processes for HealthGuard.

## Overview

HealthGuard uses GitHub Actions for continuous integration and deployment. Every push and pull request triggers automated tests and quality checks.

## Workflows

### 1. Backend Tests ([backend-tests.yml](workflows/backend-tests.yml))

**Triggers:**
- Push to `main` or `develop` branches (when backend files change)
- Pull requests to `main` or `develop` (when backend files change)

**Jobs:**

**Test Job:**
- Runs on: Ubuntu Latest
- Python versions: 3.11, 3.12
- Steps:
  1. Checkout code
  2. Set up Python
  3. Install dependencies
  4. Run pytest with coverage
  5. Upload coverage to Codecov
  6. Verify 70% minimum coverage

**Lint Job:**
- Runs on: Ubuntu Latest
- Steps:
  1. Checkout code
  2. Set up Python 3.11
  3. Run flake8 for syntax errors
  4. Check code formatting with black
  5. Type check with mypy

**Status:** ✅ Must pass before merging

---

### 2. Frontend Tests ([frontend-tests.yml](workflows/frontend-tests.yml))

**Triggers:**
- Push to `main` or `develop` branches (when frontend files change)
- Pull requests to `main` or `develop` (when frontend files change)

**Jobs:**

**Test Job:**
- Runs on: Ubuntu Latest
- Node versions: 18.x, 20.x
- Steps:
  1. Checkout code
  2. Set up Node.js
  3. Install dependencies
  4. Run tests with coverage
  5. Build application
  6. Upload build artifacts

**Lint Job:**
- Runs on: Ubuntu Latest
- Steps:
  1. Checkout code
  2. Set up Node.js 20.x
  3. Run ESLint
  4. Check formatting with Prettier

**Status:** ✅ Must pass before merging

---

### 3. CI/CD Pipeline ([ci.yml](workflows/ci.yml))

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch

**Jobs:**

1. **Check:** Validates all tests pass
2. **Integration:** Runs end-to-end integration tests
   - Starts backend server
   - Tests health endpoint
   - Builds frontend with API connection
   - Tests API endpoints
3. **Deploy Ready:** Notifies when ready for deployment (main branch only)

**Status:** ✅ Required for production deployment

---

### 4. CodeQL Security Analysis ([codeql.yml](workflows/codeql.yml))

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Weekly on Mondays (scheduled)

**Languages Analyzed:**
- JavaScript/TypeScript
- Python

**Purpose:** Identifies security vulnerabilities and code quality issues

**Status:** ⚠️ Warning only (doesn't block merging)

---

## Dependabot Configuration

Location: [.github/dependabot.yml](dependabot.yml)

**Updates:**

1. **Python Dependencies** (backend)
   - Schedule: Weekly on Mondays
   - Max open PRs: 5
   - Labels: `dependencies`, `backend`

2. **npm Dependencies** (frontend)
   - Schedule: Weekly on Mondays
   - Max open PRs: 5
   - Labels: `dependencies`, `frontend`
   - Ignores: Major version updates

3. **GitHub Actions**
   - Schedule: Weekly on Mondays
   - Max open PRs: 3
   - Labels: `dependencies`, `github-actions`

---

## Pull Request Process

When you create a PR:

1. **Automated Checks Run:**
   - ✅ Backend tests (Python 3.11 & 3.12)
   - ✅ Frontend tests (Node 18.x & 20.x)
   - ✅ Code linting and formatting
   - ✅ Security scanning (CodeQL)

2. **Review Required:**
   - All checks must pass
   - Code review approval needed
   - No merge conflicts

3. **Merge:**
   - Squash and merge recommended
   - Auto-deployment triggers on merge to `main`

---

## Status Badges

Add to README:

```markdown
[![Backend Tests](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/backend-tests.yml)
[![Frontend Tests](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/frontend-tests.yml/badge.svg)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/frontend-tests.yml)
[![CI/CD Pipeline](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/ci.yml/badge.svg)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/ci.yml)
[![CodeQL](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/codeql.yml/badge.svg)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/codeql.yml)
```

---

## Local Testing Before Push

Run these commands before pushing to ensure CI passes:

### Backend
```bash
cd backend

# Run tests
pytest

# Check coverage
pytest --cov --cov-report=term-missing

# Lint
flake8 .

# Format check
black --check .

# Type check
mypy api/ ml/
```

### Frontend
```bash
cd frontend

# Run tests
npm test

# Lint
npm run lint

# Build
npm run build
```

---

## Deployment Flow

```
Developer Push to main
        ↓
GitHub Actions Runs
        ↓
All Tests Pass? ─── NO ──→ Block Merge
        ↓ YES
Merge to main
        ↓
   ┌────┴────┐
   ↓         ↓
Render    Vercel
(Backend) (Frontend)
   ↓         ↓
Production Deployment
```

---

## Environment Variables for CI

GitHub Actions automatically provides:
- `GITHUB_TOKEN` - For GitHub API access
- `GITHUB_WORKSPACE` - Repository root path

Custom secrets (if needed):
- Go to Settings → Secrets and variables → Actions
- Add repository secrets for sensitive data

---

## Troubleshooting

### Tests Fail in CI but Pass Locally

**Common causes:**
1. Different Python/Node versions
2. Missing environment variables
3. Path differences (use absolute paths)
4. Cached dependencies

**Solution:**
```bash
# Match CI environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

### Workflow Not Triggering

**Check:**
1. File paths in workflow triggers
2. Branch protection rules
3. Workflow permissions in repo settings

### Coverage Threshold Fails

**Solution:**
```bash
# Check current coverage
pytest --cov --cov-report=term-missing

# Add tests for uncovered code
# Current threshold: 70%
```

---

## Branch Protection Rules

Recommended settings for `main` branch:

- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
  - backend-tests
  - frontend-tests
  - integration
- ✅ Require branches to be up to date before merging
- ✅ Include administrators
- ✅ Restrict who can push to matching branches

**To configure:**
1. Go to Settings → Branches
2. Add branch protection rule for `main`
3. Enable above options

---

## Future Enhancements

- [ ] Automated deployment previews for PRs
- [ ] Performance benchmarking in CI
- [ ] Visual regression testing
- [ ] Automatic changelog generation
- [ ] Release automation
- [ ] Docker image building and publishing
- [ ] E2E testing with Playwright

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot)
- [CodeQL Documentation](https://codeql.github.com/docs/)
