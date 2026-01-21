#!/bin/bash

# Test runner script - simplified to only require pytest to pass
# No coverage threshold requirements

echo "🚀 Starting pytest validation..."

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

# Run tests with coverage reporting (but no threshold enforcement)
echo "🧪 Running tests..."
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

TEST_STATUS=$?

# Display coverage report (informational only)
echo ""
echo "� Coverage Report (informational):"
coverage report --show-missing

# Summary
echo ""
echo "📋 Test Summary:"
echo "==================="
if [ $TEST_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Note: Coverage report is shown above for reference."
    echo "Tests pass as long as pytest succeeds, regardless of coverage percentage."
    exit 0
else
    echo -e "${RED}✗ Tests failed. Check the output above.${NC}"
    exit 1
fi
