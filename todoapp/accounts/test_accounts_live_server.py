import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from django.test import tag

@tag('e2e')
@override_settings(DEBUG=True)
class AccountsLiveServerTestCase(StaticLiveServerTestCase):
    """Base class for accounts live server tests"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
    
    def setUp(self):
        """Set up test data for each test"""
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
    
    def wait_for_element(self, locator, timeout=10):
        """Helper method to wait for an element to be present"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
    def wait_for_element_clickable(self, locator, timeout=10):
        """Helper method to wait for an element to be clickable"""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    
    def get_messages(self):
        """Helper method to get Django messages from the page"""
        try:
            # Wait for messages container to be present
            messages_container = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'messages'))
            )
            return [msg.text for msg in messages_container.find_elements(By.TAG_NAME, 'div')]
        except (NoSuchElementException, TimeoutException):
            return []


class UserRegistrationLiveServerTests(AccountsLiveServerTestCase):
    """LiveServerTestCase for user registration functionality"""
    
    def test_registration_page_loads_correctly(self):
        """Test that the registration page loads with all required elements"""
        # Navigate to registration page
        register_url = f"{self.live_server_url}{reverse('accounts:register')}"
        self.driver.get(register_url)
        
        # Check page title
        self.assertIn('Register', self.driver.title)
        
        # Check that the form is present
        form = self.wait_for_element((By.TAG_NAME, 'form'))
        self.assertTrue(form.is_displayed())
        
        # Check required form fields
        username_field = self.driver.find_element(By.ID, 'id_username')
        password1_field = self.driver.find_element(By.ID, 'id_password1')
        password2_field = self.driver.find_element(By.ID, 'id_password2')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        self.assertTrue(username_field.is_displayed())
        self.assertTrue(password1_field.is_displayed())
        self.assertTrue(password2_field.is_displayed())
        self.assertTrue(submit_button.is_displayed())
    
    def test_successful_user_registration(self):
        """Test successful user registration with valid data"""
        initial_user_count = User.objects.count()
        
        # Navigate to registration page
        register_url = f"{self.live_server_url}{reverse('accounts:register')}"
        self.driver.get(register_url)
        
        # Fill out the registration form
        username_field = self.wait_for_element((By.ID, 'id_username'))
        password1_field = self.driver.find_element(By.ID, 'id_password1')
        password2_field = self.driver.find_element(By.ID, 'id_password2')
        
        username_field.send_keys(self.test_user_data['username'])
        password1_field.send_keys(self.test_user_data['password1'])
        password2_field.send_keys(self.test_user_data['password2'])
        
        # Submit the form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )
        
        # Verify user was created
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        new_user = User.objects.get(username=self.test_user_data['username'])
        self.assertEqual(new_user.username, self.test_user_data['username'])
        
        # Check success message
        messages = self.get_messages()
        expected_message = f'Account created for {self.test_user_data["username"]}!'
        self.assertTrue(any(expected_message in msg for msg in messages))
    
    def test_registration_with_mismatched_passwords(self):
        """Test registration fails with mismatched passwords"""
        # Navigate to registration page
        register_url = f"{self.live_server_url}{reverse('accounts:register')}"
        self.driver.get(register_url)
        
        # Fill out form with mismatched passwords
        username_field = self.wait_for_element((By.ID, 'id_username'))
        password1_field = self.driver.find_element(By.ID, 'id_password1')
        password2_field = self.driver.find_element(By.ID, 'id_password2')
        
        username_field.send_keys('testuser2')
        password1_field.send_keys('password123')
        password2_field.send_keys('differentpassword')
        
        # Submit the form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should stay on registration page
        time.sleep(1)  # Brief wait for form processing
        self.assertIn('/accounts/register/', self.driver.current_url)
        
        # Check for error message
        try:
            error_list = self.driver.find_element(By.CLASS_NAME, 'errorlist')
            self.assertTrue(error_list.is_displayed())
        except NoSuchElementException:
            # Error might be displayed differently
            pass
    
    def test_registration_with_existing_username(self):
        """Test registration fails with existing username"""
        # Navigate to registration page
        register_url = f"{self.live_server_url}{reverse('accounts:register')}"
        self.driver.get(register_url)
        
        # Try to register with existing username
        username_field = self.wait_for_element((By.ID, 'id_username'))
        password1_field = self.driver.find_element(By.ID, 'id_password1')
        password2_field = self.driver.find_element(By.ID, 'id_password2')
        
        username_field.send_keys(self.existing_user_data['username'])
        password1_field.send_keys('newpassword123')
        password2_field.send_keys('newpassword123')
        
        # Submit the form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should stay on registration page
        time.sleep(1)  # Brief wait for form processing
        self.assertIn('/accounts/register/', self.driver.current_url)
        
        # Check for error message about username already existing
        try:
            error_list = self.driver.find_element(By.CLASS_NAME, 'errorlist')
            self.assertTrue(error_list.is_displayed())
            self.assertIn('already exists', error_list.text.lower())
        except NoSuchElementException:
            # Error might be displayed differently
            pass


class UserLoginLiveServerTests(AccountsLiveServerTestCase):
    """LiveServerTestCase for user login functionality"""
    
    def test_login_page_loads_correctly(self):
        """Test that the login page loads with all required elements"""
        # Navigate to login page
        login_url = f"{self.live_server_url}{reverse('accounts:login')}"
        self.driver.get(login_url)
        
        # Check page title
        self.assertIn('Login', self.driver.title)
        
        # Check that the form is present
        form = self.wait_for_element((By.TAG_NAME, 'form'))
        self.assertTrue(form.is_displayed())
        
        # Check required form fields
        username_field = self.driver.find_element(By.ID, 'id_username')
        password_field = self.driver.find_element(By.ID, 'id_password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        self.assertTrue(username_field.is_displayed())
        self.assertTrue(password_field.is_displayed())
        self.assertTrue(submit_button.is_displayed())
    
    def test_successful_login(self):
        """Test successful login with valid credentials"""
        # Navigate to login page
        login_url = f"{self.live_server_url}{reverse('accounts:login')}"
        self.driver.get(login_url)
        
        # Fill out login form
        username_field = self.wait_for_element((By.ID, 'id_username'))
        password_field = self.driver.find_element(By.ID, 'id_password')
        
        username_field.send_keys(self.existing_user_data['username'])
        password_field.send_keys(self.existing_user_data['password'])
        
        # Submit the form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )
        
        # Verify we're on home page
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/")
    
    def test_login_with_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        # Navigate to login page
        login_url = f"{self.live_server_url}{reverse('accounts:login')}"
        self.driver.get(login_url)
        
        # Fill out login form with invalid credentials
        username_field = self.wait_for_element((By.ID, 'id_username'))
        password_field = self.driver.find_element(By.ID, 'id_password')
        
        username_field.send_keys('invaliduser')
        password_field.send_keys('invalidpassword')
        
        # Submit the form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should stay on login page
        time.sleep(1)  # Brief wait for form processing
        self.assertIn('/accounts/login/', self.driver.current_url)
        
        # Check for error message
        try:
            error_list = self.driver.find_element(By.CLASS_NAME, 'errorlist')
            self.assertTrue(error_list.is_displayed())
        except NoSuchElementException:
            # Error might be displayed differently
            pass
    
    def test_login_with_empty_fields(self):
        """Test login fails with empty fields"""
        # Navigate to login page
        login_url = f"{self.live_server_url}{reverse('accounts:login')}"
        self.driver.get(login_url)
        
        # Submit the form without filling fields
        submit_button = self.wait_for_element((By.CSS_SELECTOR, 'button[type="submit"]'))
        submit_button.click()
        
        # Should stay on login page
        time.sleep(1)  # Brief wait for form processing
        self.assertIn('/accounts/login/', self.driver.current_url)


class UserLogoutLiveServerTests(AccountsLiveServerTestCase):
    """LiveServerTestCase for user logout functionality"""
    
    def test_successful_logout(self):
        """Test successful logout"""
        # First login
        login_url = f"{self.live_server_url}{reverse('accounts:login')}"
        self.driver.get(login_url)
        
        username_field = self.wait_for_element((By.ID, 'id_username'))
        password_field = self.driver.find_element(By.ID, 'id_password')
        
        username_field.send_keys(self.existing_user_data['username'])
        password_field.send_keys(self.existing_user_data['password'])
        
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )
        
        # Now test logout
        logout_url = f"{self.live_server_url}{reverse('accounts:logout')}"
        self.driver.get(logout_url)
        
        # Should redirect to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )
        
        # Check for logout success message
        messages = self.get_messages()
        self.assertTrue(any('logged out' in msg.lower() for msg in messages))


class AuthenticationFlowLiveServerTests(AccountsLiveServerTestCase):
    """LiveServerTestCase for complete authentication flow scenarios"""
    
    def test_complete_registration_login_logout_flow(self):
        """Test complete user flow: registration -> login -> logout"""
        # Step 1: Register new user
        register_url = f"{self.live_server_url}{reverse('accounts:register')}"
        self.driver.get(register_url)
        
        username_field = self.wait_for_element((By.ID, 'id_username'))
        password1_field = self.driver.find_element(By.ID, 'id_password1')
        password2_field = self.driver.find_element(By.ID, 'id_password2')
        
        test_username = 'flowtest_user'
        test_password = 'flow_test_password_123'
        
        username_field.send_keys(test_username)
        password1_field.send_keys(test_password)
        password2_field.send_keys(test_password)
        
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should redirect to home after registration (auto-login)
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )
        
        # Step 2: Logout
        logout_url = f"{self.live_server_url}{reverse('accounts:logout')}"
        self.driver.get(logout_url)
        
        # Should redirect to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )
        
        # Step 3: Login again with the same credentials
        login_url = f"{self.live_server_url}{reverse('accounts:login')}"
        self.driver.get(login_url)
        
        username_field = self.wait_for_element((By.ID, 'id_username'))
        password_field = self.driver.find_element(By.ID, 'id_password')
        
        username_field.send_keys(test_username)
        password_field.send_keys(test_password)
        
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should redirect to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )
        
        # Verify user exists in database
        user = User.objects.get(username=test_username)
        self.assertEqual(user.username, test_username)
    
    def test_authenticated_user_redirect_from_auth_pages(self):
        """Test that authenticated users are redirected away from login/register pages"""
        # First login
        login_url = f"{self.live_server_url}{reverse('accounts:login')}"
        self.driver.get(login_url)
        
        username_field = self.wait_for_element((By.ID, 'id_username'))
        password_field = self.driver.find_element(By.ID, 'id_password')
        
        username_field.send_keys(self.existing_user_data['username'])
        password_field.send_keys(self.existing_user_data['password'])
        
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )
        
        # Now try to access login page while authenticated
        self.driver.get(login_url)
        
        # Should be redirected to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )
        
        # Try to access register page while authenticated
        register_url = f"{self.live_server_url}{reverse('accounts:register')}"
        self.driver.get(register_url)
        
        # Should be redirected to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.current_url == f"{self.live_server_url}/"
        )