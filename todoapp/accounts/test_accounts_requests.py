from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from django.test import override_settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.test import Client

from .views import register_view, CustomLoginView, logout_view


@override_settings(DEBUG=True)
class BasicAccountsTestCase(TestCase):
    """Base class for accounts tests using RequestFactory"""
    
    def setUp(self):
        """Set up test data for each test"""
        self.factory = RequestFactory()
        self.test_user_data = {
            'username': 'testuser',
            'password1': 'complex_password_123',
            'password2': 'complex_password_123'
        }
        self.existing_user_data = {
            'username': 'existinguser',
            'password': 'existing_password_123'
        }
        # Create an existing user for login tests
        self.existing_user = User.objects.create_user(
            username=self.existing_user_data['username'],
            password=self.existing_user_data['password']
        )
    
    def add_middleware_to_request(self, request, user=None):
        """Helper method to add middleware to request objects"""
        # Add session middleware
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()
        
        # Add authentication middleware
        request.user = user if user else AnonymousUser()
        
        # Add messages middleware
        msg_middleware = MessageMiddleware(lambda r: None)
        msg_middleware.process_request(request)
        
        return request


class UserRegistrationTests(BasicAccountsTestCase):
    """Test cases for user registration functionality using RequestFactory"""
    
    def test_registration_page_accessible(self):
        """Test that the registration page is accessible and returns correct status"""
        request = self.factory.get(reverse('accounts:register'))
        request = self.add_middleware_to_request(request)
        
        response = register_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password1')
        self.assertContains(response, 'password2')
    
    def test_successful_user_registration(self):
        """Test successful user registration using RequestFactory"""
        initial_user_count = User.objects.count()
        
        # Prepare registration data
        registration_data = {
            'username': self.test_user_data['username'],
            'password1': self.test_user_data['password1'],
            'password2': self.test_user_data['password2'],
        }
        
        # Create POST request
        request = self.factory.post(reverse('accounts:register'), data=registration_data)
        request = self.add_middleware_to_request(request)
        
        # Submit registration
        response = register_view(request)
        
        # Should redirect to home page (status 302)
        self.assertEqual(response.status_code, 302)
        
        # Verify user was created
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        new_user = User.objects.get(username=self.test_user_data['username'])
        self.assertEqual(new_user.username, self.test_user_data['username'])
    
    def test_registration_with_mismatched_passwords(self):
        """Test registration fails with mismatched passwords using RequestFactory"""
        # Prepare registration data with mismatched passwords
        registration_data = {
            'username': 'testuser2',
            'password1': 'password123',
            'password2': 'differentpassword',
        }
        
        # Create POST request
        request = self.factory.post(reverse('accounts:register'), data=registration_data)
        request = self.add_middleware_to_request(request)
        
        # Submit registration
        response = register_view(request)
        
        # Should stay on registration page (no redirect)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'password')  # Error should be present
    
    def test_registration_with_existing_username(self):
        """Test registration fails with existing username using RequestFactory"""
        # Try to register with existing username
        registration_data = {
            'username': self.existing_user_data['username'],
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        }
        
        # Create POST request
        request = self.factory.post(reverse('accounts:register'), data=registration_data)
        request = self.add_middleware_to_request(request)
        
        # Submit registration
        response = register_view(request)
        
        # Should stay on registration page (no redirect)
        self.assertEqual(response.status_code, 200)
        # Should contain error about username already existing
        self.assertContains(response, 'already exists', status_code=200)


class UserLoginTests(BasicAccountsTestCase):
    """Test cases for user login functionality using RequestFactory"""
    
    def test_login_page_accessible(self):
        """Test that the login page is accessible and returns correct status"""
        request = self.factory.get(reverse('accounts:login'))
        request = self.add_middleware_to_request(request)
        
        login_view = CustomLoginView.as_view()
        response = login_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password')
    
    def test_successful_login(self):
        """Test successful login using RequestFactory"""
        # For login, we'll use Django's test client since it handles authentication better
        from django.test import Client
        client = Client()
        
        # Prepare login data
        login_data = {
            'username': self.existing_user_data['username'],
            'password': self.existing_user_data['password'],
        }
        
        # Submit login
        response = client.post(reverse('accounts:login'), data=login_data)
        
        # Should redirect to home page
        self.assertEqual(response.status_code, 302)
        
        # Check that we're logged in by accessing the home page
        home_response = client.get('/')
        self.assertEqual(home_response.status_code, 200)
    
    def test_login_with_invalid_credentials(self):
        """Test login fails with invalid credentials using RequestFactory"""
        client = Client()
        
        # Prepare login data with invalid credentials
        login_data = {
            'username': 'invaliduser',
            'password': 'invalidpassword',
        }
        
        # Submit login
        response = client.post(reverse('accounts:login'), data=login_data)
        
        # Should stay on login page (no redirect)
        self.assertEqual(response.status_code, 200)
        # Should contain error message
        self.assertContains(response, 'Please enter a correct')

    def test_login_with_empty_fields(self):
        """Test login fails with empty fields using RequestFactory"""
        from django.test import Client
        client = Client()
        
        # Prepare login data with empty fields
        login_data = {
            'username': '',
            'password': '',
        }
        
        # Submit login
        response = client.post(reverse('accounts:login'), data=login_data)
        
        # Should stay on login page (no redirect)
        self.assertEqual(response.status_code, 200)
        # Should contain required field errors
        self.assertTrue(
            'This field is required' in response.content.decode() or 
            'required' in response.content.decode().lower()
        )


class UserLogoutTests(BasicAccountsTestCase):
    """Test cases for user logout functionality using RequestFactory"""
    
    def test_logout(self):
        """Test logout functionality using RequestFactory"""
        from django.test import Client
        client = Client()
        
        # First login
        login_data = {
            'username': self.existing_user_data['username'],
            'password': self.existing_user_data['password'],
        }
        
        login_response = client.post(reverse('accounts:login'), data=login_data)
        self.assertEqual(login_response.status_code, 302)
        
        # Now test logout
        logout_response = client.get(reverse('accounts:logout'))
        
        # Should redirect to home page
        self.assertEqual(logout_response.status_code, 302)
        
        # Verify we're logged out by accessing the home page
        home_response = client.get('/')
        self.assertEqual(home_response.status_code, 200)


class AuthenticationFlowTests(BasicAccountsTestCase):
    """Test cases for complete authentication flow scenarios using RequestFactory"""    
    def test_complete_registration_login_logout_flow(self):
        """Test complete user flow: registration -> logout -> login using RequestFactory"""
        from django.test import Client
        client = Client()
        
        test_username = 'flowtest_user'
        test_password = 'flow_test_password_123'
        
        # Step 1: Register new user
        registration_data = {
            'username': test_username,
            'password1': test_password,
            'password2': test_password,
        }
        
        register_response = client.post(reverse('accounts:register'), data=registration_data)
        self.assertEqual(register_response.status_code, 302)  # Should redirect to home
        
        # Step 2: Logout
        logout_response = client.get(reverse('accounts:logout'))
        self.assertEqual(logout_response.status_code, 302)
        
        # Step 3: Login again with the same credentials
        login_data = {
            'username': test_username,
            'password': test_password,
        }
        
        login_response = client.post(reverse('accounts:login'), data=login_data)
        self.assertEqual(login_response.status_code, 302)  # Should redirect to home
        
        # Verify user exists in database
        user = User.objects.get(username=test_username)
        self.assertEqual(user.username, test_username)
    
    def test_authenticated_user_access_to_auth_pages(self):
        """Test that authenticated users can access auth pages (basic behavior check)"""
        from django.test import Client
        client = Client()
        
        # First login
        login_data = {
            'username': self.existing_user_data['username'],
            'password': self.existing_user_data['password'],
        }
        
        login_response = client.post(reverse('accounts:login'), data=login_data)
        self.assertEqual(login_response.status_code, 302)
        
        # Try to access register page while authenticated
        register_response = client.get(reverse('accounts:register'))
        
        # The register view should redirect authenticated users to home
        # Let's check if we get a redirect or if the response indicates we're already logged in
        self.assertEqual(register_response.status_code, 302)
        
        # Try to access login page while authenticated
        login_response_while_auth = client.get(reverse('accounts:login'))
        
        # The login view should redirect authenticated users to home
        self.assertEqual(login_response_while_auth.status_code, 302)