# AI Career Assistant - Makefile
# Development, testing, and deployment commands

.PHONY: help dev dev-backend dev-frontend test test-backend test-frontend \
        coverage coverage-backend coverage-frontend lint lint-backend lint-frontend \
        build install install-backend install-frontend clean format typecheck

# Default target
help:
	@echo "AI Career Assistant - Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start both backend and frontend in dev mode"
	@echo "  make dev-backend      - Start backend API server"
	@echo "  make dev-frontend     - Start frontend dev server"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests (backend + frontend)"
	@echo "  make test-backend     - Run backend tests only"
	@echo "  make test-frontend    - Run frontend tests only"
	@echo ""
	@echo "Coverage:"
	@echo "  make coverage         - Run tests with coverage reports"
	@echo "  make coverage-backend - Backend coverage report"
	@echo "  make coverage-frontend- Frontend coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Run all linters"
	@echo "  make lint-backend     - Run Python linters (ruff)"
	@echo "  make lint-frontend    - Run ESLint"
	@echo "  make format           - Format all code"
	@echo "  make typecheck        - Run type checking"
	@echo ""
	@echo "Build:"
	@echo "  make build            - Build frontend for production"
	@echo "  make install          - Install all dependencies"
	@echo "  make clean            - Clean build artifacts"

# =============================================================================
# Development
# =============================================================================

dev: dev-backend dev-frontend

dev-backend:
	@echo "Starting backend API server..."
	python api_bridge.py

dev-frontend:
	@echo "Starting frontend dev server..."
	cd frontend && npm run dev

# =============================================================================
# Testing
# =============================================================================

test: test-backend test-frontend
	@echo "All tests completed!"

test-backend:
	@echo "Running backend tests..."
	pytest tests/ -v --tb=short

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm run test:run

# Watch mode for development
test-watch-backend:
	pytest tests/ -v --tb=short -f

test-watch-frontend:
	cd frontend && npm run test

# =============================================================================
# Coverage
# =============================================================================

coverage: coverage-backend coverage-frontend
	@echo "Coverage reports generated!"
	@echo "Backend: htmlcov/index.html"
	@echo "Frontend: frontend/coverage/index.html"

coverage-backend:
	@echo "Running backend tests with coverage..."
	pytest tests/ -v --cov=modules --cov=api_bridge --cov-report=html --cov-report=term-missing
	@echo "Coverage report: htmlcov/index.html"

coverage-frontend:
	@echo "Running frontend tests with coverage..."
	cd frontend && npm run test:coverage
	@echo "Coverage report: frontend/coverage/index.html"

# =============================================================================
# Linting
# =============================================================================

lint: lint-backend lint-frontend
	@echo "All linting completed!"

lint-backend:
	@echo "Running Python linters..."
	ruff check .
	ruff format --check .

lint-frontend:
	@echo "Running ESLint..."
	cd frontend && npm run lint

# =============================================================================
# Formatting
# =============================================================================

format: format-backend format-frontend
	@echo "All code formatted!"

format-backend:
	@echo "Formatting Python code..."
	ruff format .
	ruff check --fix .

format-frontend:
	@echo "Formatting frontend code..."
	cd frontend && npx prettier --write "src/**/*.{ts,tsx,css}"

# =============================================================================
# Type Checking
# =============================================================================

typecheck: typecheck-backend typecheck-frontend
	@echo "Type checking completed!"

typecheck-backend:
	@echo "Type checking Python code..."
	mypy modules/ --ignore-missing-imports || true

typecheck-frontend:
	@echo "Type checking frontend code..."
	cd frontend && npm run typecheck

# =============================================================================
# Build
# =============================================================================

build: build-frontend
	@echo "Build completed!"

build-frontend:
	@echo "Building frontend for production..."
	cd frontend && npm run build

# =============================================================================
# Installation
# =============================================================================

install: install-backend install-frontend
	@echo "All dependencies installed!"

install-backend:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development dependencies
install-dev: install
	@echo "Installing development dependencies..."
	pip install ruff mypy pytest pytest-asyncio pytest-cov pytest-mock httpx
	pip install pre-commit
	pre-commit install

# =============================================================================
# Clean
# =============================================================================

clean:
	@echo "Cleaning build artifacts..."
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf frontend/coverage/
	rm -rf frontend/dist/
	rm -rf frontend/node_modules/.vite/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean completed!"

# =============================================================================
# Database
# =============================================================================

db-init:
	@echo "Initializing database..."
	python -c "from modules.user_database import init_database; init_database()"

db-reset:
	@echo "Resetting database..."
	rm -f data/career_assistant.db
	$(MAKE) db-init

# =============================================================================
# Docker (optional)
# =============================================================================

docker-build:
	@echo "Building Docker image..."
	docker build -t ai-career-assistant .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8001:8001 -p 8080:8080 ai-career-assistant

# =============================================================================
# Pre-commit
# =============================================================================

pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files
