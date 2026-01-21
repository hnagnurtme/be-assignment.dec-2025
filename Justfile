# Justfile for Task Management API
# Run `just --list` to see all available commands

# Default recipe to display help
default:
    @just --list

# ============================================================
# Development Commands
# ============================================================

# Install all dependencies
install:
    pip install -r requirements.txt

# Install development dependencies
install-dev:
    pip install -r requirements.txt
    pip install ruff black isort mypy

# Run the development server
dev:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run the development server with debug logging
dev-debug:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# ============================================================
# Database Commands
# ============================================================

# Create a new migration
migrate-create message:
    alembic revision --autogenerate -m "{{message}}"

# Apply all pending migrations
migrate-up:
    alembic upgrade head

# Rollback one migration
migrate-down:
    alembic downgrade -1

# Show current migration status
migrate-status:
    alembic current

# Show migration history
migrate-history:
    alembic history

# Reset database (drop all tables and re-migrate)
db-reset:
    alembic downgrade base
    alembic upgrade head

# ============================================================
# Testing Commands
# ============================================================

# Run all tests
test:
    pytest tests/ -v

# Run tests with coverage
test-cov:
    pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Run tests in parallel
test-parallel:
    pytest tests/ -n auto -v

# Run specific test file
test-file file:
    pytest tests/{{file}} -v

# Run tests matching a pattern
test-match pattern:
    pytest tests/ -k "{{pattern}}" -v

# Run the test runner script
test-runner:
    ./test_runner.sh

# Watch tests (requires pytest-watch)
test-watch:
    ptw tests/ -- -v

# ============================================================
# Code Quality Commands
# ============================================================

# Run all linting checks
lint:
    ruff check app/ tests/

# Run linting and auto-fix issues
lint-fix:
    ruff check app/ tests/ --fix

# Format code with ruff
format:
    ruff format app/ tests/

# Check code formatting
format-check:
    ruff format --check app/ tests/

# Run type checking
typecheck:
    mypy app/

# Run all quality checks (lint + format + type)
check: lint format-check typecheck

# Fix all auto-fixable issues
fix: lint-fix format

# ============================================================
# Docker Commands
# ============================================================

# Build docker images
docker-build:
    docker-compose build

# Start all services
docker-up:
    docker-compose up -d

# Stop all services
docker-down:
    docker-compose down

# View logs
docker-logs:
    docker-compose logs -f

# Restart all services
docker-restart:
    docker-compose restart

# Remove all containers and volumes
docker-clean:
    docker-compose down -v

# Build and start services
docker-start: docker-build docker-up

# ============================================================
# Production Commands
# ============================================================

# Build production docker image
prod-build:
    docker-compose -f docker-compose.prod.yml build

# Start production services
prod-up:
    docker-compose -f docker-compose.prod.yml up -d

# Stop production services
prod-down:
    docker-compose -f docker-compose.prod.yml down

# View production logs
prod-logs:
    docker-compose -f docker-compose.prod.yml logs -f

# ============================================================
# Utility Commands
# ============================================================

# Clean up Python cache files
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    rm -rf htmlcov/ .coverage coverage.xml test-results.xml

# Generate OpenAPI schema
openapi:
    python -c "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json

# Count lines of code
loc:
    @echo "Lines of code:"
    @find app -name "*.py" | xargs wc -l | tail -1
    @echo "\nTest lines:"
    @find tests -name "*.py" | xargs wc -l | tail -1

# Show project structure
tree:
    tree -I '__pycache__|*.pyc|.git|.pytest_cache|htmlcov|.ruff_cache|*.egg-info' -L 3

# ============================================================
# CI/CD Commands
# ============================================================

# Run CI checks locally
ci: check test-cov

# Prepare for commit (format, lint, test)
pre-commit: fix test

# ============================================================
# Documentation Commands
# ============================================================

# Open API documentation in browser
docs:
    open http://localhost:8000/docs

# Open ReDoc documentation in browser
redoc:
    open http://localhost:8000/redoc

# ============================================================
# Quick Commands
# ============================================================

# Quick start: install deps and run dev server
start: install dev

# Full reset: clean, install, migrate, and run
reset: clean install migrate-up dev
