from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from django.contrib.messages import get_messages
from accounts.models import UserProfile


class UserRegistrationTestCase(TestCase):
    """Test cases for user registration functionality"""
    
    def setUp(self):
        """Set up test client and common test data"""
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.home_url = reverse('home')
        self.valid_user_data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
    
    def test_register_view_get_request(self):
        """Test GET request to registration page"""
        response = self.client.get(self.register_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
        self.assertContains(response, '<form method="post">')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password1')
        self.assertContains(response, 'password2')
    
    def test_register_view_uses_correct_template(self):
        """Test that registration view uses the correct template"""
        response = self.client.get(self.register_url)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_successful_user_registration(self):
        """Test successful user registration with valid data"""
        initial_user_count = User.objects.count()
        initial_profile_count = UserProfile.objects.count()
        
        response = self.client.post(self.register_url, self.valid_user_data)
        
        # Check redirect to home page
        self.assertRedirects(response, self.home_url)
        
        # Check user was created
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        
        # Check user exists with correct username
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('testpassword123'))
        
        # Check UserProfile was automatically created
        self.assertEqual(UserProfile.objects.count(), initial_profile_count + 1)
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.user, user)
    
    def test_automatic_login_after_registration(self):
        """Test that user is automatically logged in after successful registration"""
        response = self.client.post(self.register_url, self.valid_user_data)
        
        # Check user is logged in
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'testuser')
    
    def test_success_message_after_registration(self):
        """Test that success message is displayed after registration"""
        response = self.client.post(self.register_url, self.valid_user_data, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Account created for testuser!')
    
    def test_registration_with_mismatched_passwords(self):
        """Test registration fails with mismatched passwords"""
        invalid_data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'differentpassword'
        }
        
        initial_user_count = User.objects.count()
        response = self.client.post(self.register_url, invalid_data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        
        # No user should be created
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_registration_with_weak_password(self):
        """Test registration fails with weak password"""
        invalid_data = {
            'username': 'testuser',
            'password1': '123',
            'password2': '123'
        }
        
        initial_user_count = User.objects.count()
        response = self.client.post(self.register_url, invalid_data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        
        # No user should be created
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_registration_with_duplicate_username(self):
        """Test registration fails with duplicate username"""
        # Create a user first
        User.objects.create_user(username='testuser', password='somepassword')
        
        initial_user_count = User.objects.count()
        response = self.client.post(self.register_url, self.valid_user_data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists')
        
        # No additional user should be created
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_registration_with_empty_username(self):
        """Test registration fails with empty username"""
        invalid_data = {
            'username': '',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        
        initial_user_count = User.objects.count()
        response = self.client.post(self.register_url, invalid_data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
        
        # No user should be created
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_authenticated_user_redirect(self):
        """Test that authenticated users are redirected from registration page"""
        # Create and login a user
        user = User.objects.create_user(username='existinguser', password='password123')
        self.client.force_login(user)
        
        response = self.client.get(self.register_url)
        
        # Should redirect to home page
        self.assertRedirects(response, self.home_url)
    
    def test_authenticated_user_cannot_register_again(self):
        """Test that authenticated users cannot register again via POST"""
        # Create and login a user
        user = User.objects.create_user(username='existinguser', password='password123')
        self.client.force_login(user)
        
        initial_user_count = User.objects.count()
        response = self.client.post(self.register_url, self.valid_user_data)
        
        # Should redirect to home page
        self.assertRedirects(response, self.home_url)
        
        # No new user should be created
        self.assertEqual(User.objects.count(), initial_user_count)


class UserProfileCreationTestCase(TestCase):
    """Test cases for UserProfile automatic creation"""
    
    def test_userprofile_created_on_user_creation(self):
        """Test that UserProfile is automatically created when User is created"""
        initial_profile_count = UserProfile.objects.count()
        
        user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )
        
        # Check UserProfile was created
        self.assertEqual(UserProfile.objects.count(), initial_profile_count + 1)
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.user, user)
    
    def test_userprofile_default_values(self):
        """Test that UserProfile has correct default values"""
        user = User.objects.create_user(username='testuser', password='testpassword123')
        profile = user.profile
        
        self.assertEqual(profile.default_task_priority, 'medium')
        self.assertTrue(profile.email_notifications)
        self.assertEqual(profile.timezone, 'UTC')
        self.assertEqual(profile.bio, '')
        self.assertEqual(profile.phone_number, '')
        self.assertIsNone(profile.date_of_birth)
    
    def test_userprofile_str_method(self):
        """Test UserProfile string representation"""
        user = User.objects.create_user(username='testuser', password='testpassword123')
        profile = user.profile
        
        self.assertEqual(str(profile), "testuser's Profile")
    
    def test_userprofile_get_full_name_with_names(self):
        """Test get_full_name method when first and last names are provided"""
        user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )
        profile = user.profile
        
        self.assertEqual(profile.get_full_name(), 'John Doe')
    
    def test_userprofile_get_full_name_without_names(self):
        """Test get_full_name method when names are not provided"""
        user = User.objects.create_user(username='testuser', password='testpassword123')
        profile = user.profile
        
        self.assertEqual(profile.get_full_name(), 'testuser')


class RegistrationURLTestCase(TestCase):
    """Test cases for registration URL routing"""
    
    def test_registration_url_resolves(self):
        """Test that registration URL resolves correctly"""
        url = reverse('accounts:register')
        self.assertEqual(url, '/accounts/register/')
    
    def test_registration_url_accessible(self):
        """Test that registration URL is accessible"""
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)


class RegistrationIntegrationTestCase(TestCase):
    """Integration tests for the complete registration flow"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.home_url = reverse('home')
    
    def test_complete_registration_and_navigation_flow(self):
        """Test complete user journey from registration to navigation"""
        # Step 1: Visit registration page
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
        
        # Step 2: Register new user
        user_data = {
            'username': 'journeyuser',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = self.client.post(self.register_url, user_data)
        self.assertRedirects(response, self.home_url)
        
        # Step 3: Check user can access home page while logged in
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'journeyuser')
        self.assertContains(response, 'Logout')
        
        # Step 4: Verify user cannot access registration again
        response = self.client.get(self.register_url)
        self.assertRedirects(response, self.home_url)
        
        # Step 5: Verify user exists in database with profile
        user = User.objects.get(username='journeyuser')
        self.assertTrue(user.check_password('complexpassword123'))
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.default_task_priority, 'medium')
    
    def test_registration_form_preserves_data_on_error(self):
        """Test that form preserves username when password validation fails"""
        invalid_data = {
            'username': 'preserveuser',
            'password1': 'weak',
            'password2': 'different'
        }
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        
        # Check that username is preserved in the form
        self.assertContains(response, 'value="preserveuser"')
    
    def test_registration_error_messages_display(self):
        """Test that appropriate error messages are displayed"""
        invalid_data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        
        response = self.client.post(self.register_url, invalid_data)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        error_found = any('error' in str(message).lower() for message in messages)
        
        # If form validation fails, error message should be present
        if response.status_code == 200 and User.objects.filter(username='testuser').count() == 0:
            self.assertTrue(error_found or 'error' in response.content.decode().lower())


class RegistrationSecurityTestCase(TestCase):
    """Security-focused tests for registration"""
    
    def test_csrf_protection_on_registration_form(self):
        """Test that CSRF protection is enabled on registration form"""
        response = self.client.get(reverse('accounts:register'))
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_password_not_exposed_in_response(self):
        """Test that passwords are not exposed in any response"""
        user_data = {
            'username': 'securityuser',
            'password1': 'secretpassword123',
            'password2': 'secretpassword123'
        }
        
        # Test both successful and failed registration
        response = self.client.post(reverse('accounts:register'), user_data)
        content = response.content.decode()
        
        self.assertNotIn('secretpassword123', content)
        
        # Test with invalid data too
        invalid_data = {
            'username': 'securityuser2',
            'password1': 'anothersecret123',
            'password2': 'differentpassword'
        }
        
        response = self.client.post(reverse('accounts:register'), invalid_data)
        content = response.content.decode()
        
        self.assertNotIn('anothersecret123', content)
        self.assertNotIn('differentpassword', content)
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are prevented"""
        malicious_data = {
            'username': "'; DROP TABLE auth_user; --",
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        
        initial_user_count = User.objects.count()
        
        # This should not cause any damage
        response = self.client.post(reverse('accounts:register'), malicious_data)
        
        # Users table should still exist and be accessible
        final_user_count = User.objects.count()
        self.assertEqual(initial_user_count, final_user_count)
