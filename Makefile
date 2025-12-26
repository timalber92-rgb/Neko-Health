.PHONY: help install install-dev clean test lint format docker-build docker-up docker-down

help:
	@echo "HealthGuard Development Commands"
	@echo "================================="
	@echo "install          Install backend dependencies"
	@echo "install-dev      Install backend dev dependencies"
	@echo "clean            Clean build artifacts and caches"
	@echo "test             Run backend tests"
	@echo "test-cov         Run tests with coverage report"
	@echo "lint             Run linters (black, isort, flake8)"
	@echo "format           Auto-format code (black, isort)"
	@echo "docker-build     Build Docker images"
	@echo "docker-up        Start Docker containers"
	@echo "docker-down      Stop Docker containers"
	@echo "frontend-install Install frontend dependencies"
	@echo "frontend-dev     Start frontend dev server"

install:
	cd backend && pip install -r requirements.txt

install-dev:
	cd backend && pip install -r requirements-dev.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	rm -rf backend/dist backend/build backend/*.egg-info
	rm -rf frontend/dist frontend/build

test:
	cd backend && pytest

test-cov:
	cd backend && pytest --cov=. --cov-report=html --cov-report=term

lint:
	cd backend && black --check .
	cd backend && isort --check .
	cd backend && flake8 .

format:
	cd backend && black .
	cd backend && isort .

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

backend-dev:
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
