# Testing Guide

This document explains how to run tests for the Django Todo App project.

## 🚀 Quick Start

### Run All Tests (Recommended)
```bash
# Using the automated test runner
./run_tests.sh

# Or manually with Django
cd todoapp
python manage.py test
```

### Run Specific Test Categories
```bash
# Registration tests only
cd todoapp
python test_registration.py

# Specific test class
python manage.py test accounts.tests.UserRegistrationTestCase

# With coverage
coverage run --source='.' manage.py test
coverage report
```

## 🧪 Test Structure

### Test Files
- `accounts/tests.py` - Main test suite for authentication
- `test_registration.py` - Custom registration test runner
- `run_tests.sh` - Comprehensive test runner script

### Test Categories
1. **UserRegistrationTestCase** - Core registration functionality
2. **UserProfileCreationTestCase** - Profile creation and signals
3. **RegistrationURLTestCase** - URL routing tests
4. **RegistrationIntegrationTestCase** - End-to-end flows
5. **RegistrationSecurityTestCase** - Security validations

## 🔧 Test Configuration

### Coverage Settings
- Minimum coverage: 80%
- Reports: Terminal, HTML, XML
- Configuration: `.coveragerc`

### Pytest Settings
- Configuration: `pytest.ini`
- Django integration enabled
- Coverage reporting enabled

## 🚀 GitHub Actions CI/CD

### Workflows
1. **`tests.yml`** - Simple test runner (recommended)
2. **`django-ci.yml`** - Full CI/CD pipeline with matrix testing

### Triggers
- Push to `main`, `develop` branches
- Pull requests to `main`, `develop`
- Manual workflow dispatch

### Matrix Testing
- Python versions: 3.10, 3.11
- Django versions: 4.2, 5.0, 5.1
- Multiple OS support (Ubuntu focus)

## 📊 Coverage Reports

### Local Reports
```bash
# Generate HTML report
coverage html
open htmlcov/index.html

# Terminal report
coverage report --show-missing

# XML report (for CI)
coverage xml
```

### CI Reports
- Uploaded to Codecov
- Available as GitHub Actions artifacts
- Coverage badges in README

## 🛡️ Security Testing

### Tools Used
- **Bandit** - Security linter for Python
- **Safety** - Known vulnerability scanner
- **Django Check** - Built-in security checks

### Manual Security Checks
```bash
# Security linting
bandit -r todoapp/

# Vulnerability scanning
safety check

# Django security checks
python manage.py check --deploy
```

## 🔍 Code Quality

### Automated Checks
- **Black** - Code formatting
- **isort** - Import sorting
- **Flake8** - Style and error checking
- **Pre-commit hooks** - Run checks before commits

### Setup Pre-commit
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## 📈 Test Metrics

### Current Coverage
- **Target**: 80% minimum
- **Current**: Check latest CI run
- **Reports**: Available in `htmlcov/` after running tests

### Test Count
- **Total Tests**: 24+ comprehensive test cases
- **Test Classes**: 5 specialized test suites
- **Coverage Areas**: Views, Models, URLs, Templates, Security

## 🐛 Debugging Tests

### Failed Tests
```bash
# Verbose output
python manage.py test --verbosity=2

# Stop on first failure
python manage.py test --failfast

# Specific test with debug
python manage.py test accounts.tests.UserRegistrationTestCase.test_successful_user_registration -v 2
```

### Common Issues
1. **Database errors**: Run `python manage.py migrate`
2. **Import errors**: Check `DJANGO_SETTINGS_MODULE`
3. **Permission errors**: Ensure proper file permissions

## 📝 Writing New Tests

### Best Practices
1. Use descriptive test names
2. Follow AAA pattern (Arrange, Act, Assert)
3. Test both success and failure cases
4. Mock external dependencies
5. Keep tests isolated and independent

### Example Test
```python
def test_user_registration_success(self):
    """Test successful user registration"""
    # Arrange
    user_data = {
        'username': 'testuser',
        'password1': 'testpass123',
        'password2': 'testpass123'
    }
    
    # Act
    response = self.client.post(self.register_url, user_data)
    
    # Assert
    self.assertRedirects(response, '/')
    self.assertTrue(User.objects.filter(username='testuser').exists())
```

## 🚀 GitHub Actions Status

Add this badge to your README:

```markdown
![Tests](https://github.com/HenriqueDSousa/todo-app/workflows/Tests/badge.svg)
```

## 💡 Tips

- Run tests frequently during development
- Use coverage reports to find untested code
- Write tests before fixing bugs (TDD)
- Keep test data minimal and focused
- Use factories for complex object creation

For more information, see the [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/).