#!/bin/bash

# Test runner script to validate comprehensive pytest setup
# This script mimics what the CI will do

echo "🚀 Starting comprehensive pytest validation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Set test environment variables
export APP_ENV=testing
export DATABASE_URL=sqlite:///./test.db
export REDIS_URL=redis://localhost:6379/1
export JWT_SECRET_KEY=test-secret-key
export JWT_ALGORITHM=HS256
export JWT_EXPIRY_MINUTES=30

echo "🔧 Setting up test environment..."

# Install additional testing dependencies if needed
echo "📦 Installing testing dependencies..."
pip install pytest-cov pytest-mock pytest-xdist pytest-html coverage[toml] factory-boy
print_status $? "Testing dependencies installation"

# Run linting first
echo "🔍 Running code quality checks..."
ruff check app/ tests/ --output-format=text
print_status $? "Ruff linting"

ruff format --check app/ tests/
print_status $? "Code formatting check"

# Run tests with different configurations
echo "🧪 Running comprehensive tests..."

# 1. Basic test run with coverage
echo "📊 Running tests with coverage..."
pytest \
    --verbose \
    --tb=short \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --junit-xml=test-results.xml \
    --asyncio-mode=auto \
    --disable-warnings \
    tests/
BASIC_TEST_STATUS=$?
print_status $BASIC_TEST_STATUS "Basic test run with coverage"

# 2. Parallel test execution
echo "⚡ Running tests in parallel..."
pytest \
    -n auto \
    --verbose \
    --tb=line \
    tests/
PARALLEL_TEST_STATUS=$?
print_status $PARALLEL_TEST_STATUS "Parallel test execution"

# 3. Unit tests only
echo "🔬 Running unit tests..."
pytest \
    -m "unit" \
    --verbose \
    tests/
UNIT_TEST_STATUS=$?
print_status $UNIT_TEST_STATUS "Unit tests execution"

# 4. Integration tests (if any)
echo "🔗 Running integration tests..."
pytest \
    -m "integration" \
    --verbose \
    tests/
INTEGRATION_TEST_STATUS=$?
print_status $INTEGRATION_TEST_STATUS "Integration tests execution"

# 5. Async tests specifically
echo "⏰ Running async tests..."
pytest \
    -k "async" \
    --verbose \
    --asyncio-mode=auto \
    tests/
ASYNC_TEST_STATUS=$?
print_status $ASYNC_TEST_STATUS "Async tests execution"

# 6. API tests specifically
echo "🌐 Running API tests..."
pytest \
    -k "api or endpoint" \
    --verbose \
    tests/
API_TEST_STATUS=$?
print_status $API_TEST_STATUS "API tests execution"

# 7. Authentication tests
echo "🔐 Running authentication tests..."
pytest \
    tests/test_auth.py \
    --verbose \
    -v
AUTH_TEST_STATUS=$?
print_status $AUTH_TEST_STATUS "Authentication tests execution"

# 8. User service tests
echo "👤 Running user service tests..."
pytest \
    tests/test_users.py \
    --verbose \
    -v
USER_TEST_STATUS=$?
print_status $USER_TEST_STATUS "User service tests execution"

# 9. Test with different output formats
echo "📄 Running tests with different output formats..."
pytest \
    --verbose \
    --tb=long \
    --html=report.html \
    --self-contained-html \
    tests/
HTML_TEST_STATUS=$?
print_status $HTML_TEST_STATUS "HTML report generation"

# 10. Coverage check
echo "📈 Checking test coverage..."
coverage report --show-missing
COVERAGE_STATUS=$?
print_status $COVERAGE_STATUS "Coverage report"

# Generate coverage badge (if coverage-badge is available)
if command -v coverage-badge &> /dev/null; then
    coverage-badge -o coverage.svg
    print_status $? "Coverage badge generation"
fi

# Summary
echo ""
echo "📋 Test Summary:"
echo "==================="
echo -e "Basic Tests:        $([ $BASIC_TEST_STATUS -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"
echo -e "Parallel Tests:     $([ $PARALLEL_TEST_STATUS -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"
echo -e "Unit Tests:         $([ $UNIT_TEST_STATUS -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"
echo -e "Integration Tests:  $([ $INTEGRATION_TEST_STATUS -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"
echo -e "Async Tests:        $([ $ASYNC_TEST_STATUS -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"
echo -e "API Tests:          $([ $API_TEST_STATUS -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"
echo -e "Auth Tests:         $([ $AUTH_TEST_STATUS -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"
echo -e "User Tests:         $([ $USER_TEST_STATUS -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"

# Overall status
if [ $BASIC_TEST_STATUS -eq 0 ] && [ $USER_TEST_STATUS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All critical tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Check the output above.${NC}"
    exit 1
fi
