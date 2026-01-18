# Makefile for TaskMind Backend Testing

.PHONY: help test test-unit test-integration test-cov test-html test-parallel clean lint format install

help:					## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:				## Install dependencies
	pip install -r requirements.txt

test:					## Run all tests
	pytest tests/ -v

test-unit:				## Run unit tests only
	pytest tests/ -v -m "unit"

test-integration:		## Run integration tests only
	pytest tests/ -v -m "integration"

test-cov:				## Run tests with coverage
	pytest tests/ -v --cov=app --cov-report=term-missing

test-html:				## Run tests with HTML coverage report
	pytest tests/ -v --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

test-parallel:			## Run tests in parallel
	pytest tests/ -v -n auto

test-watch:				## Run tests in watch mode (requires pytest-watch)
	pytest-watch -- tests/ -v

test-fast:				## Run tests quickly (no coverage, parallel)
	pytest tests/ -v -n auto --tb=short -x

test-slow:				## Run only slow tests
	pytest tests/ -v -m "slow"

test-auth:				## Run authentication tests
	pytest tests/test_auth.py -v

test-users:				## Run user service tests
	pytest tests/test_users.py -v

test-api:				## Run API tests
	pytest tests/ -v -k "api or endpoint"

test-db:				## Run database-related tests
	pytest tests/ -v -m "db"

test-comprehensive:		## Run comprehensive test suite
	./test_runner.sh

lint:					## Run linting
	ruff check app/ tests/

format:					## Format code
	ruff format app/ tests/

format-check:			## Check code formatting
	ruff format --check app/ tests/

clean:					## Clean up test artifacts
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f coverage.xml
	rm -f test-results.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

ci-test:				## Run tests as CI would
	pytest tests/ -v \
		--tb=short \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=xml \
		--junit-xml=test-results.xml \
		--asyncio-mode=auto \
		--disable-warnings

docker-test:			## Run tests in Docker environment
	docker-compose -f docker-compose.yml run --rm api pytest tests/ -v

setup-test-env:			## Setup test environment
	export APP_ENV=testing
	export DATABASE_URL=sqlite+aiosqlite:///./test.db
	export REDIS_URL=redis://localhost:6379/1
	export JWT_SECRET_KEY=test-secret-key

benchmark:				## Run performance benchmarks (if available)
	pytest tests/ -v -m "benchmark" --benchmark-only

security-test:			## Run security tests
	bandit -r app/
	safety check

all-checks:				## Run all quality checks
	make lint
	make format-check
	make test-cov
	make security-test

# Development helpers
dev-setup:				## Setup development environment
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install

update-deps:			## Update dependencies
	pip list --outdated
	pip install -r requirements.txt --upgrade

test-debug:				## Run tests with debugging
	pytest tests/ -v -s --pdb

test-verbose:			## Run tests with maximum verbosity
	pytest tests/ -vvv --tb=long

test-quiet:				## Run tests quietly
	pytest tests/ -q

test-last-failed:		## Run only last failed tests
	pytest tests/ --lf

test-new:				## Run tests for new/modified code
	pytest tests/ --co -q | grep "test session starts" -A 100
