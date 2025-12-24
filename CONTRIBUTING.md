# Contributing to HealthGuard

Thank you for your interest in contributing to HealthGuard!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/TimAlbert92/Neko-Health.git
   cd Neko-Health
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For testing
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Run Tests**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

## Project Structure

```
healthguard/
├── backend/          # Python FastAPI backend
│   ├── api/         # API endpoints and models
│   ├── ml/          # Machine learning models
│   ├── data/        # Data processing
│   └── tests/       # Backend tests
├── frontend/         # React + Vite frontend
│   └── src/
│       ├── components/  # React components
│       └── api/         # API client
├── docs/             # Documentation
└── .devcontainer/    # VSCode DevContainer config
```

## Code Style

**Python**: Follow PEP 8
- Use `black` for formatting
- Use `pylint` for linting

**JavaScript**: Follow Standard JS
- Use ESLint with provided config
- Use Prettier for formatting

## Testing

- Write tests for all new features
- Maintain > 80% code coverage
- Run tests before submitting PR

## Pull Request Process

1. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear, focused commits

3. **Add/update tests** to maintain coverage

4. **Run tests locally** before pushing
   ```bash
   # Backend
   cd backend && pytest --cov

   # Frontend
   cd frontend && npm test
   ```

5. **Format and lint your code**
   ```bash
   # Backend
   cd backend
   black .
   flake8 .

   # Frontend
   cd frontend
   npm run lint
   ```

6. **Push and create PR**
   - Use the PR template
   - Link related issues
   - Add clear description

7. **Wait for CI/CD checks** to pass
   - Backend tests (Python 3.11 & 3.12)
   - Frontend tests (Node 18.x & 20.x)
   - Code quality checks
   - Security scanning (CodeQL)

8. **Address review feedback** if needed

9. **Merge** after approval

See [.github/CI_CD.md](.github/CI_CD.md) for detailed CI/CD documentation.

## Documentation

Update documentation when:
- Adding new features
- Changing APIs
- Modifying configuration
- Updating dependencies

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions
