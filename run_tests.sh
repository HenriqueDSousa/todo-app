#!/bin/bash

# Test runner script for the Django Todo App
# This script runs all tests and generates coverage reports

set -e  # Exit on any error

echo "🧪 Django Todo App Test Runner"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "todoapp/manage.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Move to Django project directory
cd todoapp

print_status "Setting up environment..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not detected. Consider activating it."
fi

# Install/upgrade required packages for testing
print_status "Installing test dependencies..."
pip install coverage pytest-django --quiet

# Check for migrations
print_status "Checking for pending migrations..."
python manage.py makemigrations --dry-run --verbosity=0 | grep -q "No changes detected" || {
    print_status "Creating new migrations..."
    python manage.py makemigrations
}

# Apply migrations
print_status "Applying database migrations..."
python manage.py migrate --verbosity=0

# Run Django's built-in checks
print_status "Running Django system checks..."
python manage.py check

# Run all tests with coverage
print_status "Running all tests with coverage..."
coverage run --source='.' manage.py test --verbosity=2

# Generate coverage report
print_status "Generating coverage report..."
coverage report --show-missing

# Generate HTML coverage report
print_status "Generating HTML coverage report..."
coverage html

# Generate XML coverage report (for CI)
coverage xml

# Run custom registration tests
print_status "Running custom registration tests..."
python test_registration.py

# Run additional security checks if bandit is available
if command -v bandit &> /dev/null; then
    print_status "Running security checks with bandit..."
    bandit -r . -x "*/tests.py,*/test_*.py" --quiet || true
fi

# Run code quality checks if available
if command -v flake8 &> /dev/null; then
    print_status "Running code quality checks..."
    flake8 . --max-line-length=88 --extend-ignore=E203,W503 --exclude=migrations,venv || true
fi

# Check test coverage threshold
COVERAGE_THRESHOLD=80
COVERAGE_PERCENTAGE=$(coverage report | tail -1 | awk '{print $4}' | sed 's/%//')

if [ -n "$COVERAGE_PERCENTAGE" ]; then
    if (( $(echo "$COVERAGE_PERCENTAGE >= $COVERAGE_THRESHOLD" | bc -l) )); then
        print_success "Coverage is ${COVERAGE_PERCENTAGE}% (above ${COVERAGE_THRESHOLD}% threshold)"
    else
        print_warning "Coverage is ${COVERAGE_PERCENTAGE}% (below ${COVERAGE_THRESHOLD}% threshold)"
    fi
fi

print_success "All tests completed successfully!"
print_status "Coverage reports generated:"
print_status "  - Terminal: coverage report"
print_status "  - HTML: htmlcov/index.html"
print_status "  - XML: coverage.xml"

echo ""
echo "🎉 Test run completed! Check the reports above for detailed results."