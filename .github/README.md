# HealthGuard GitHub Configuration

This directory contains all GitHub-specific configuration files for the HealthGuard project.

## 📁 Contents

### Workflows (`.github/workflows/`)

Automated CI/CD pipelines that run on every push and pull request:

- **[backend-tests.yml](workflows/backend-tests.yml)** - Backend testing & linting
  - Pytest with coverage (70% minimum)
  - Flake8 linting
  - Black formatting check
  - MyPy type checking
  - Runs on Python 3.11 & 3.12

- **[frontend-tests.yml](workflows/frontend-tests.yml)** - Frontend testing & linting
  - npm test with coverage
  - ESLint checking
  - Prettier formatting check
  - Build verification
  - Runs on Node 18.x & 20.x

- **[ci.yml](workflows/ci.yml)** - Main CI/CD pipeline
  - Integration testing
  - End-to-end API tests
  - Deployment readiness checks

- **[codeql.yml](workflows/codeql.yml)** - Security scanning
  - Automated security vulnerability detection
  - Python & JavaScript code analysis
  - Runs weekly + on push/PR

### Issue Templates (`ISSUE_TEMPLATE/`)

Standardized templates for GitHub issues:

- **[bug_report.md](ISSUE_TEMPLATE/bug_report.md)** - Bug report template
- **[feature_request.md](ISSUE_TEMPLATE/feature_request.md)** - Feature request template
- **[config.yml](ISSUE_TEMPLATE/config.yml)** - Issue template configuration

### Pull Requests

- **[PULL_REQUEST_TEMPLATE.md](PULL_REQUEST_TEMPLATE.md)** - PR template with checklist

### Dependency Management

- **[dependabot.yml](dependabot.yml)** - Automated dependency updates
  - Python (pip) - Weekly updates
  - JavaScript (npm) - Weekly updates
  - GitHub Actions - Weekly updates

### Documentation

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Complete project organization guide
- **[CI_CD.md](CI_CD.md)** - CI/CD pipeline documentation

## 🚀 Quick Links

- [View Workflows](https://github.com/TimAlbert92/Neko-Health/actions)
- [Create Issue](https://github.com/TimAlbert92/Neko-Health/issues/new/choose)
- [Create Pull Request](https://github.com/TimAlbert92/Neko-Health/compare)
- [Security Advisories](https://github.com/TimAlbert92/Neko-Health/security)

## 📊 Status Badges

Current build status:

[![Backend Tests](https://github.com/TimAlbert92/Neko-Health/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/TimAlbert92/Neko-Health/actions/workflows/backend-tests.yml)
[![Frontend Tests](https://github.com/TimAlbert92/Neko-Health/actions/workflows/frontend-tests.yml/badge.svg)](https://github.com/TimAlbert92/Neko-Health/actions/workflows/frontend-tests.yml)
[![CI/CD Pipeline](https://github.com/TimAlbert92/Neko-Health/actions/workflows/ci.yml/badge.svg)](https://github.com/TimAlbert92/Neko-Health/actions/workflows/ci.yml)
[![CodeQL](https://github.com/TimAlbert92/Neko-Health/actions/workflows/codeql.yml/badge.svg)](https://github.com/TimAlbert92/Neko-Health/actions/workflows/codeql.yml)

## 🔧 How It Works

### On Every Push/PR:

1. **Code Quality Checks**
   - Linting (flake8, ESLint)
   - Formatting (black, Prettier)
   - Type checking (mypy)

2. **Automated Testing**
   - Unit tests (pytest, Jest)
   - Integration tests
   - Coverage reporting

3. **Security Scanning**
   - CodeQL analysis
   - Dependency vulnerability checks

### On Merge to Main:

1. **All checks must pass**
2. **Automatic deployment** (if configured)
   - Backend → Render.com
   - Frontend → Vercel

## 📝 Contributing

Before submitting a PR:

1. Create a feature branch
2. Make your changes
3. Run tests locally
4. Ensure all checks pass
5. Submit PR using the template

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## 🔐 Security

- **Dependabot** monitors dependencies weekly
- **CodeQL** scans for vulnerabilities
- **Private security advisories** available

Report security issues: [Create Security Advisory](https://github.com/TimAlbert92/Neko-Health/security/advisories/new)

## 📖 More Information

- Main README: [../README.md](../README.md)
- Quick Start: [../QUICKSTART.md](../QUICKSTART.md)
- CI/CD Details: [CI_CD.md](CI_CD.md)
- Project Structure: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
