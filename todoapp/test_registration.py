#!/usr/bin/env python
"""
Test runner script for the registration feature tests.
Run this to execute all registration-related tests.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapp.settings')
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    print("Running User Registration Tests...")
    print("=" * 50)

    failures = test_runner.run_tests([
        "accounts.tests.UserRegistrationTestCase",
        "accounts.tests.UserProfileCreationTestCase", 
        "accounts.tests.RegistrationURLTestCase"
    ])

    if failures:
        print(f"\n {failures} test(s) failed!")
        sys.exit(1)
    else:
        print("\n✅ All registration tests passed!")
        sys.exit(0)