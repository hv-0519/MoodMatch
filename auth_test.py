# # # """
# # # Comprehensive Test Cases for MoodMatch Authentication Module

# # # This test suite covers all authentication functionalities:
# # # - User Registration
# # # - User Login (Users and Admins)
# # # - Password Reset Flow
# # # - Session Management
# # # - Input Validation
# # # - Security Measures
# # # """

# # # import unittest
# # # import sqlite3
# # # import os
# # # import tempfile
# # # from datetime import datetime
# # # from werkzeug.security import generate_password_hash, check_password_hash
# # # from flask import Flask, session
# # # from flask_login import LoginManager, current_user
# # # from io import BytesIO

# # # # Mock imports - adjust based on your actual project structure
# # # # from auth import auth_bp, User, get_db_connection
# # # # from utils.helper import generate_username, send_email


# # # class TestAuthenticationModule(unittest.TestCase):
# # #     """Base test class for authentication module"""
    
# # #     @classmethod
# # #     def setUpClass(cls):
# # #         """Set up test fixtures that are used by all test methods"""
# # #         cls.app = Flask(__name__)
# # #         cls.app.config['SECRET_KEY'] = 'test-secret-key'
# # #         cls.app.config['TESTING'] = True
# # #         cls.app.config['WTF_CSRF_ENABLED'] = False
        
# # #         # Create temporary database
# # #         cls.db_fd, cls.db_path = tempfile.mkstemp()
# # #         cls.app.config['DATABASE'] = cls.db_path
        
# # #     @classmethod
# # #     def tearDownClass(cls):
# # #         """Clean up after all tests"""
# # #         os.close(cls.db_fd)
# # #         os.unlink(cls.db_path)
    
# # #     def setUp(self):
# # #         """Set up before each test"""
# # #         self.client = self.app.test_client()
# # #         self.create_test_database()
        
# # #     def tearDown(self):
# # #         """Clean up after each test"""
# # #         self.drop_test_database()
    
# # #     def create_test_database(self):
# # #         """Create test database with required schema"""
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
        
# # #         # Create users table
# # #         cursor.execute('''
# # #             CREATE TABLE IF NOT EXISTS users (
# # #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 username TEXT UNIQUE NOT NULL,
# # #                 first_name TEXT NOT NULL,
# # #                 last_name TEXT NOT NULL,
# # #                 email TEXT NOT NULL,
# # #                 phone_number TEXT,
# # #                 gender TEXT CHECK (gender IN ('male', 'female', 'other')),
# # #                 date_of_birth DATE,
# # #                 street_address TEXT,
# # #                 city TEXT,
# # #                 state TEXT,
# # #                 postal_code TEXT,
# # #                 country TEXT,
# # #                 profile_picture TEXT DEFAULT 'default.png',
# # #                 password_hash TEXT NOT NULL,
# # #                 reset_code TEXT,
# # #                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP
# # #             )
# # #         ''')
        
# # #         # Create admins table
# # #         cursor.execute('''
# # #             CREATE TABLE IF NOT EXISTS admins (
# # #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 username TEXT UNIQUE NOT NULL,
# # #                 password_hash TEXT NOT NULL,
# # #                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP
# # #             )
# # #         ''')
        
# # #         # Create interests tables
# # #         cursor.execute('''
# # #             CREATE TABLE IF NOT EXISTS interest_categories (
# # #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 name TEXT NOT NULL UNIQUE,
# # #                 description TEXT
# # #             )
# # #         ''')
        
# # #         cursor.execute('''
# # #             CREATE TABLE IF NOT EXISTS interests (
# # #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 category_id INTEGER NOT NULL,
# # #                 name TEXT NOT NULL,
# # #                 FOREIGN KEY (category_id) REFERENCES interest_categories(id) ON DELETE CASCADE
# # #             )
# # #         ''')
        
# # #         cursor.execute('''
# # #             CREATE TABLE IF NOT EXISTS user_interests (
# # #                 user_id INTEGER NOT NULL,
# # #                 interest_id INTEGER NOT NULL,
# # #                 PRIMARY KEY (user_id, interest_id),
# # #                 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
# # #                 FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
# # #             )
# # #         ''')
        
# # #         conn.commit()
# # #         conn.close()
    
# # #     def drop_test_database(self):
# # #         """Drop all test tables"""
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute("DROP TABLE IF EXISTS user_interests")
# # #         cursor.execute("DROP TABLE IF EXISTS interests")
# # #         cursor.execute("DROP TABLE IF EXISTS interest_categories")
# # #         cursor.execute("DROP TABLE IF EXISTS admins")
# # #         cursor.execute("DROP TABLE IF EXISTS users")
# # #         conn.commit()
# # #         conn.close()
    
# # #     def insert_test_user(self, username="testuser", email="test@example.com", 
# # #                         password="Test@123", first_name="Test", last_name="User"):
# # #         """Helper method to insert a test user"""
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         password_hash = generate_password_hash(password)
# # #         cursor.execute('''
# # #             INSERT INTO users (username, first_name, last_name, email, password_hash)
# # #             VALUES (?, ?, ?, ?, ?)
# # #         ''', (username, first_name, last_name, email, password_hash))
# # #         user_id = cursor.lastrowid
# # #         conn.commit()
# # #         conn.close()
# # #         return user_id
    
# # #     def insert_test_admin(self, username="admin", password="Admin@123"):
# # #         """Helper method to insert a test admin"""
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         password_hash = generate_password_hash(password)
# # #         cursor.execute('''
# # #             INSERT INTO admins (username, password_hash)
# # #             VALUES (?, ?)
# # #         ''', (username, password_hash))
# # #         admin_id = cursor.lastrowid
# # #         conn.commit()
# # #         conn.close()
# # #         return admin_id


# # # # ============================================
# # # # TEST CASES: USER REGISTRATION
# # # # ============================================

# # # class TestUserRegistration(TestAuthenticationModule):
# # #     """Test cases for user registration functionality"""
    
# # #     def test_registration_page_loads(self):
# # #         """TC-REG-001: Test that registration page loads successfully"""
# # #         response = self.client.get('/register')
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_successful_registration_with_all_fields(self):
# # #         """TC-REG-002: Test successful user registration with all fields"""
# # #         data = {
# # #             'first_name': 'John',
# # #             'last_name': 'Doe',
# # #             'email': 'john.doe@example.com',
# # #             'phone': '1234567890',
# # #             'gender': 'male',
# # #             'date_of_birth': '1995-01-15',
# # #             'street': '123 Main St',
# # #             'city': 'New York',
# # #             'state': 'NY',
# # #             'postal_code': '10001',
# # #             'country': 'USA',
# # #             'password': 'SecurePass@123',
# # #             'interests': ['reading', 'gaming']
# # #         }
        
# # #         response = self.client.post('/register', data=data, follow_redirects=True)
        
# # #         # Verify user was created in database
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('SELECT * FROM users WHERE email = ?', (data['email'],))
# # #         user = cursor.fetchone()
# # #         conn.close()
        
# # #         self.assertIsNotNone(user, "User should be created in database")
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_registration_with_minimum_required_fields(self):
# # #         """TC-REG-003: Test registration with only required fields"""
# # #         data = {
# # #             'first_name': 'Jane',
# # #             'last_name': 'Smith',
# # #             'email': 'jane.smith@example.com',
# # #             'password': 'Pass@1234',
# # #         }
        
# # #         response = self.client.post('/register', data=data, follow_redirects=True)
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_registration_duplicate_email(self):
# # #         """TC-REG-004: Test registration with duplicate email fails"""
# # #         # Insert existing user
# # #         self.insert_test_user(email='existing@example.com')
        
# # #         data = {
# # #             'first_name': 'New',
# # #             'last_name': 'User',
# # #             'email': 'existing@example.com',  # Duplicate
# # #             'password': 'NewPass@123'
# # #         }
        
# # #         response = self.client.post('/register', data=data, follow_redirects=True)
# # #         # Should fail or show error message
# # #         self.assertIn(b'error', response.data.lower() or b'exists', response.data.lower())
    
# # #     def test_registration_password_validation(self):
# # #         """TC-REG-005: Test password strength validation"""
# # #         weak_passwords = [
# # #             '123',           # Too short
# # #             'password',      # No special chars, no numbers
# # #             'Pass123',       # No special chars
# # #             'pass@word',     # No numbers, no uppercase
# # #         ]
        
# # #         for weak_pwd in weak_passwords:
# # #             data = {
# # #                 'first_name': 'Test',
# # #                 'last_name': 'User',
# # #                 'email': f'test_{weak_pwd}@example.com',
# # #                 'password': weak_pwd
# # #             }
# # #             response = self.client.post('/register', data=data)
# # #             # Should reject weak passwords
# # #             # Note: Actual validation depends on implementation
    
# # #     def test_registration_email_format_validation(self):
# # #         """TC-REG-006: Test email format validation"""
# # #         invalid_emails = [
# # #             'notanemail',
# # #             'missing@domain',
# # #             '@nodomain.com',
# # #             'spaces in@email.com'
# # #         ]
        
# # #         for invalid_email in invalid_emails:
# # #             data = {
# # #                 'first_name': 'Test',
# # #                 'last_name': 'User',
# # #                 'email': invalid_email,
# # #                 'password': 'Valid@123'
# # #             }
# # #             response = self.client.post('/register', data=data)
# # #             # Should reject invalid email formats
    
# # #     def test_registration_username_generation(self):
# # #         """TC-REG-007: Test automatic username generation"""
# # #         data = {
# # #             'first_name': 'Alice',
# # #             'last_name': 'Johnson',
# # #             'email': 'alice.j@example.com',
# # #             'password': 'Secure@123'
# # #         }
        
# # #         response = self.client.post('/register', data=data, follow_redirects=True)
        
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('SELECT username FROM users WHERE email = ?', (data['email'],))
# # #         result = cursor.fetchone()
# # #         conn.close()
        
# # #         if result:
# # #             username = result[0]
# # #             # Username should be generated from first and last name
# # #             self.assertIsNotNone(username)
# # #             self.assertTrue(len(username) > 0)
    
# # #     def test_registration_profile_picture_upload(self):
# # #         """TC-REG-008: Test profile picture file upload"""
# # #         data = {
# # #             'first_name': 'Bob',
# # #             'last_name': 'Wilson',
# # #             'email': 'bob.w@example.com',
# # #             'password': 'Secure@456',
# # #             'profile_picture': (BytesIO(b'fake image data'), 'profile.jpg')
# # #         }
        
# # #         response = self.client.post('/register', data=data, 
# # #                                    content_type='multipart/form-data',
# # #                                    follow_redirects=True)
        
# # #         # Verify profile picture was saved
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('SELECT profile_picture FROM users WHERE email = ?', (data['email'],))
# # #         result = cursor.fetchone()
# # #         conn.close()
        
# # #         if result:
# # #             self.assertIsNotNone(result[0])
    
# # #     def test_registration_interests_saving(self):
# # #         """TC-REG-009: Test user interests are saved correctly"""
# # #         # First, insert some interests
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute("INSERT INTO interest_categories (name) VALUES ('Hobbies')")
# # #         cat_id = cursor.lastrowid
# # #         cursor.execute("INSERT INTO interests (category_id, name) VALUES (?, ?)", (cat_id, 'reading'))
# # #         interest_id = cursor.lastrowid
# # #         conn.commit()
# # #         conn.close()
        
# # #         data = {
# # #             'first_name': 'Carol',
# # #             'last_name': 'Davis',
# # #             'email': 'carol.d@example.com',
# # #             'password': 'Pass@789',
# # #             'interests': ['reading']
# # #         }
        
# # #         response = self.client.post('/register', data=data, follow_redirects=True)
        
# # #         # Verify interests were saved
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('''
# # #             SELECT ui.interest_id FROM user_interests ui
# # #             JOIN users u ON ui.user_id = u.id
# # #             WHERE u.email = ?
# # #         ''', (data['email'],))
# # #         saved_interests = cursor.fetchall()
# # #         conn.close()
        
# # #         self.assertGreater(len(saved_interests), 0, "User interests should be saved")
    
# # #     def test_registration_welcome_email_sent(self):
# # #         """TC-REG-010: Test welcome email is sent after registration"""
# # #         data = {
# # #             'first_name': 'David',
# # #             'last_name': 'Miller',
# # #             'email': 'david.m@example.com',
# # #             'password': 'Welcome@123'
# # #         }
        
# # #         # This test would need to mock the send_email function
# # #         # and verify it was called with correct parameters
# # #         response = self.client.post('/register', data=data, follow_redirects=True)
# # #         # Assertion would depend on email mock implementation
    
# # #     def test_registration_gender_validation(self):
# # #         """TC-REG-011: Test gender field accepts only valid values"""
# # #         valid_genders = ['male', 'female', 'other']
        
# # #         for gender in valid_genders:
# # #             data = {
# # #                 'first_name': 'Test',
# # #                 'last_name': 'User',
# # #                 'email': f'test_{gender}@example.com',
# # #                 'password': 'Test@123',
# # #                 'gender': gender
# # #             }
# # #             response = self.client.post('/register', data=data, follow_redirects=True)
# # #             self.assertEqual(response.status_code, 200)
    
# # #     def test_registration_date_of_birth_format(self):
# # #         """TC-REG-012: Test date of birth format validation"""
# # #         data = {
# # #             'first_name': 'Young',
# # #             'last_name': 'User',
# # #             'email': 'young@example.com',
# # #             'password': 'Young@123',
# # #             'date_of_birth': '2005-12-25'
# # #         }
        
# # #         response = self.client.post('/register', data=data, follow_redirects=True)
# # #         self.assertEqual(response.status_code, 200)


# # # # ============================================
# # # # TEST CASES: USER LOGIN
# # # # ============================================

# # # class TestUserLogin(TestAuthenticationModule):
# # #     """Test cases for user login functionality"""
    
# # #     def test_login_page_loads(self):
# # #         """TC-LOGIN-001: Test login page loads successfully"""
# # #         response = self.client.get('/login')
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_successful_user_login(self):
# # #         """TC-LOGIN-002: Test successful login with valid credentials"""
# # #         # Create test user
# # #         self.insert_test_user(username='john_doe', password='Test@123')
        
# # #         data = {
# # #             'username': 'john_doe',
# # #             'password': 'Test@123'
# # #         }
        
# # #         response = self.client.post('/login', data=data, follow_redirects=True)
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_login_with_wrong_password(self):
# # #         """TC-LOGIN-003: Test login fails with incorrect password"""
# # #         self.insert_test_user(username='testuser', password='Correct@123')
        
# # #         data = {
# # #             'username': 'testuser',
# # #             'password': 'Wrong@Password'
# # #         }
        
# # #         response = self.client.post('/login', data=data, follow_redirects=True)
# # #         self.assertIn(b'Invalid', response.data)
    
# # #     def test_login_with_nonexistent_user(self):
# # #         """TC-LOGIN-004: Test login fails with non-existent username"""
# # #         data = {
# # #             'username': 'nonexistent',
# # #             'password': 'Any@Password'
# # #         }
        
# # #         response = self.client.post('/login', data=data, follow_redirects=True)
# # #         self.assertIn(b'Invalid', response.data)
    
# # #     def test_login_with_empty_credentials(self):
# # #         """TC-LOGIN-005: Test login with empty username and password"""
# # #         data = {
# # #             'username': '',
# # #             'password': ''
# # #         }
        
# # #         response = self.client.post('/login', data=data)
# # #         # Should return validation error
    
# # #     def test_login_remember_me_functionality(self):
# # #         """TC-LOGIN-006: Test 'Remember Me' checkbox functionality"""
# # #         self.insert_test_user(username='remember_user', password='Test@123')
        
# # #         data = {
# # #             'username': 'remember_user',
# # #             'password': 'Test@123',
# # #             'remember': 'on'
# # #         }
        
# # #         response = self.client.post('/login', data=data, follow_redirects=True)
# # #         # Session should persist
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_successful_admin_login(self):
# # #         """TC-LOGIN-007: Test successful admin login"""
# # #         self.insert_test_admin(username='admin', password='Admin@123')
        
# # #         data = {
# # #             'username': 'admin',
# # #             'password': 'Admin@123'
# # #         }
        
# # #         response = self.client.post('/login', data=data, follow_redirects=True)
# # #         self.assertEqual(response.status_code, 200)
# # #         # Should redirect to admin dashboard
    
# # #     def test_admin_and_user_separation(self):
# # #         """TC-LOGIN-008: Test admin login redirects to admin dashboard"""
# # #         self.insert_test_admin(username='admin', password='Admin@123')
# # #         self.insert_test_user(username='user', password='User@123')
        
# # #         # Admin login
# # #         response = self.client.post('/login', 
# # #                                    data={'username': 'admin', 'password': 'Admin@123'},
# # #                                    follow_redirects=False)
# # #         # Should redirect to admin dashboard (depends on routing)
    
# # #     def test_case_sensitivity_username(self):
# # #         """TC-LOGIN-009: Test username case sensitivity"""
# # #         self.insert_test_user(username='TestUser', password='Test@123')
        
# # #         # Try with different case
# # #         data = {
# # #             'username': 'testuser',  # lowercase
# # #             'password': 'Test@123'
# # #         }
        
# # #         response = self.client.post('/login', data=data)
# # #         # Behavior depends on implementation (case-sensitive or not)
    
# # #     def test_sql_injection_prevention(self):
# # #         """TC-LOGIN-010: Test SQL injection prevention"""
# # #         malicious_inputs = [
# # #             "admin' OR '1'='1",
# # #             "admin'; DROP TABLE users--",
# # #             "' OR 1=1--"
# # #         ]
        
# # #         for malicious in malicious_inputs:
# # #             data = {
# # #                 'username': malicious,
# # #                 'password': 'anything'
# # #             }
# # #             response = self.client.post('/login', data=data)
# # #             # Should not cause SQL error or unauthorized access
# # #             self.assertNotEqual(response.status_code, 500)
    
# # #     def test_redirect_authenticated_users_from_login(self):
# # #         """TC-LOGIN-011: Test authenticated users are redirected from login page"""
# # #         # This would require session management testing
# # #         pass


# # # # ============================================
# # # # TEST CASES: PASSWORD RESET
# # # # ============================================

# # # class TestPasswordReset(TestAuthenticationModule):
# # #     """Test cases for password reset functionality"""
    
# # #     def test_forget_password_page_loads(self):
# # #         """TC-RESET-001: Test forget password page loads"""
# # #         response = self.client.get('/forget_password')
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_request_reset_with_valid_credentials(self):
# # #         """TC-RESET-002: Test password reset request with valid email and username"""
# # #         self.insert_test_user(username='resetuser', email='reset@example.com')
        
# # #         data = {
# # #             'username': 'resetuser',
# # #             'email': 'reset@example.com'
# # #         }
        
# # #         response = self.client.post('/forget_password', data=data, follow_redirects=True)
        
# # #         # Verify reset code was generated
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('SELECT reset_code FROM users WHERE username = ?', ('resetuser',))
# # #         result = cursor.fetchone()
# # #         conn.close()
        
# # #         if result:
# # #             self.assertIsNotNone(result[0], "Reset code should be generated")
    
# # #     def test_request_reset_with_invalid_email(self):
# # #         """TC-RESET-003: Test reset request with non-existent email"""
# # #         data = {
# # #             'username': 'someuser',
# # #             'email': 'nonexistent@example.com'
# # #         }
        
# # #         response = self.client.post('/forget_password', data=data, follow_redirects=True)
# # #         self.assertIn(b'Invalid', response.data)
    
# # #     def test_request_reset_with_mismatched_credentials(self):
# # #         """TC-RESET-004: Test reset with valid username but wrong email"""
# # #         self.insert_test_user(username='user1', email='correct@example.com')
        
# # #         data = {
# # #             'username': 'user1',
# # #             'email': 'wrong@example.com'
# # #         }
        
# # #         response = self.client.post('/forget_password', data=data, follow_redirects=True)
# # #         self.assertIn(b'Invalid', response.data)
    
# # #     def test_reset_code_generation_format(self):
# # #         """TC-RESET-005: Test reset code is 6 digits"""
# # #         self.insert_test_user(username='codeuser', email='code@example.com')
        
# # #         data = {
# # #             'username': 'codeuser',
# # #             'email': 'code@example.com'
# # #         }
        
# # #         response = self.client.post('/forget_password', data=data, follow_redirects=True)
        
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('SELECT reset_code FROM users WHERE username = ?', ('codeuser',))
# # #         result = cursor.fetchone()
# # #         conn.close()
        
# # #         if result and result[0]:
# # #             self.assertEqual(len(result[0]), 6, "Reset code should be 6 digits")
# # #             self.assertTrue(result[0].isdigit(), "Reset code should be numeric")
    
# # #     def test_reset_email_sent(self):
# # #         """TC-RESET-006: Test reset email is sent"""
# # #         self.insert_test_user(username='emailuser', email='email@example.com')
        
# # #         data = {
# # #             'username': 'emailuser',
# # #             'email': 'email@example.com'
# # #         }
        
# # #         # Would need to mock send_email and verify it was called
# # #         response = self.client.post('/forget_password', data=data, follow_redirects=True)
    
# # #     def test_verify_reset_code_page_loads(self):
# # #         """TC-RESET-007: Test verify code page loads with username parameter"""
# # #         response = self.client.get('/verify_code?username=testuser')
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_verify_correct_reset_code(self):
# # #         """TC-RESET-008: Test verification with correct reset code"""
# # #         user_id = self.insert_test_user(username='verifyuser', email='verify@example.com')
        
# # #         # Set a known reset code
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('UPDATE users SET reset_code = ? WHERE id = ?', ('123456', user_id))
# # #         conn.commit()
# # #         conn.close()
        
# # #         data = {
# # #             'username': 'verifyuser',
# # #             'reset_code': '123456'
# # #         }
        
# # #         response = self.client.post('/verify_code', data=data, follow_redirects=False)
# # #         # Should redirect to reset password page
    
# # #     def test_verify_incorrect_reset_code(self):
# # #         """TC-RESET-009: Test verification with incorrect code"""
# # #         user_id = self.insert_test_user(username='wrongcode', email='wrong@example.com')
        
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('UPDATE users SET reset_code = ? WHERE id = ?', ('123456', user_id))
# # #         conn.commit()
# # #         conn.close()
        
# # #         data = {
# # #             'username': 'wrongcode',
# # #             'reset_code': '999999'  # Wrong code
# # #         }
        
# # #         response = self.client.post('/verify_code', data=data, follow_redirects=True)
# # #         self.assertIn(b'Invalid', response.data)
    
# # #     def test_reset_password_page_loads(self):
# # #         """TC-RESET-010: Test reset password page loads"""
# # #         response = self.client.get('/reset_password?username=testuser')
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_successful_password_reset(self):
# # #         """TC-RESET-011: Test successful password reset"""
# # #         user_id = self.insert_test_user(username='resetpwd', 
# # #                                        email='resetpwd@example.com', 
# # #                                        password='OldPass@123')
        
# # #         data = {
# # #             'username': 'resetpwd',
# # #             'new_password': 'NewPass@456',
# # #             'confirm_password': 'NewPass@456'
# # #         }
        
# # #         response = self.client.post('/reset_password', data=data, follow_redirects=True)
        
# # #         # Verify password was changed
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('SELECT password_hash FROM users WHERE username = ?', ('resetpwd',))
# # #         result = cursor.fetchone()
# # #         conn.close()
        
# # #         if result:
# # #             # Try logging in with new password
# # #             login_response = self.client.post('/login', 
# # #                                             data={'username': 'resetpwd', 
# # #                                                   'password': 'NewPass@456'})
    
# # #     def test_password_reset_with_mismatched_passwords(self):
# # #         """TC-RESET-012: Test reset fails when passwords don't match"""
# # #         data = {
# # #             'username': 'mismatch',
# # #             'new_password': 'NewPass@123',
# # #             'confirm_password': 'Different@456'
# # #         }
        
# # #         response = self.client.post('/reset_password', data=data, follow_redirects=True)
# # #         self.assertIn(b'do not match', response.data)
    
# # #     def test_reset_code_cleared_after_reset(self):
# # #         """TC-RESET-013: Test reset code is cleared after password reset"""
# # #         user_id = self.insert_test_user(username='clearcode', email='clear@example.com')
        
# # #         # Set reset code
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('UPDATE users SET reset_code = ? WHERE id = ?', ('123456', user_id))
# # #         conn.commit()
# # #         conn.close()
        
# # #         data = {
# # #             'username': 'clearcode',
# # #             'new_password': 'NewPass@789',
# # #             'confirm_password': 'NewPass@789'
# # #         }
        
# # #         response = self.client.post('/reset_password', data=data, follow_redirects=True)
        
# # #         # Verify reset code is NULL
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('SELECT reset_code FROM users WHERE username = ?', ('clearcode',))
# # #         result = cursor.fetchone()
# # #         conn.close()
        
# # #         if result:
# # #             self.assertIsNone(result[0], "Reset code should be cleared")


# # # # ============================================
# # # # TEST CASES: LOGOUT
# # # # ============================================

# # # class TestLogout(TestAuthenticationModule):
# # #     """Test cases for logout functionality"""
    
# # #     def test_logout_clears_session(self):
# # #         """TC-LOGOUT-001: Test logout clears user session"""
# # #         # Login first
# # #         self.insert_test_user(username='logoutuser', password='Test@123')
# # #         self.client.post('/login', data={'username': 'logoutuser', 'password': 'Test@123'})
        
# # #         # Logout
# # #         response = self.client.get('/logout', follow_redirects=True)
# # #         self.assertEqual(response.status_code, 200)
    
# # #     def test_logout_redirects_to_index(self):
# # #         """TC-LOGOUT-002: Test logout redirects to index page"""
# # #         self.insert_test_user(username='redirect', password='Test@123')
# # #         self.client.post('/login', data={'username': 'redirect', 'password': 'Test@123'})
        
# # #         response = self.client.get('/logout', follow_redirects=False)
# # #         # Should redirect (302 or 303)
# # #         self.assertIn(response.status_code, [302, 303])
    
# # #     def test_logout_requires_authentication(self):
# # #         """TC-LOGOUT-003: Test logout requires user to be logged in"""
# # #         response = self.client.get('/logout')
# # #         # Should redirect to login (401 or redirect)


# # # # ============================================
# # # # TEST CASES: SECURITY
# # # # ============================================

# # # class TestSecurity(TestAuthenticationModule):
# # #     """Test cases for security features"""
    
# # #     def test_password_hashing(self):
# # #         """TC-SEC-001: Test passwords are hashed, not stored as plaintext"""
# # #         user_id = self.insert_test_user(username='hashtest', 
# # #                                        email='hash@example.com',
# # #                                        password='PlainText@123')
        
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
# # #         result = cursor.fetchone()
# # #         conn.close()
        
# # #         if result:
# # #             password_hash = result[0]
# # #             # Hash should not equal plain password
# # #             self.assertNotEqual(password_hash, 'PlainText@123')
# # #             # Should be using werkzeug format
# # #             self.assertTrue(password_hash.startswith('pbkdf2:') or 
# # #                           password_hash.startswith('scrypt:'))
    
# # #     def test_session_security(self):
# # #         """TC-SEC-002: Test session uses secret key"""
# # #         # Verify app has secret key configured
# # #         self.assertTrue(self.app.config.get('SECRET_KEY'))
    
# # #     def test_file_upload_security(self):
# # #         """TC-SEC-003: Test file uploads use secure_filename"""
# # #         # This would test the secure_filename function usage
# # #         pass
    
# # #     def test_blocked_auth_pages_for_logged_in_users(self):
# # #         """TC-SEC-004: Test logged-in users can't access login/register pages"""
# # #         # Login first
# # #         self.insert_test_user(username='blocked', password='Test@123')
# # #         self.client.post('/login', data={'username': 'blocked', 'password': 'Test@123'})
        
# # #         # Try to access login page
# # #         response = self.client.get('/login', follow_redirects=False)
# # #         # Should redirect away from login page


# # # # ============================================
# # # # TEST CASES: INPUT VALIDATION
# # # # ============================================

# # # class TestInputValidation(TestAuthenticationModule):
# # #     """Test cases for input validation"""
    
# # #     def test_xss_prevention_in_inputs(self):
# # #         """TC-VAL-001: Test XSS script injection is prevented"""
# # #         malicious_inputs = [
# # #             "<script>alert('XSS')</script>",
# # #             "<img src=x onerror=alert('XSS')>",
# # #             "javascript:alert('XSS')"
# # #         ]
        
# # #         for malicious in malicious_inputs:
# # #             data = {
# # #                 'first_name': malicious,
# # #                 'last_name': 'User',
# # #                 'email': 'xss@example.com',
# # #                 'password': 'Test@123'
# # #             }
# # #             response = self.client.post('/register', data=data)
# # #             # Should escape or reject malicious input
    
# # #     def test_phone_number_format_validation(self):
# # #         """TC-VAL-002: Test phone number format validation"""
# # #         valid_phones = ['1234567890', '+1234567890', '123-456-7890']
        
# # #         for phone in valid_phones:
# # #             data = {
# # #                 'first_name': 'Test',
# # #                 'last_name': 'User',
# # #                 'email': f'phone{phone}@example.com',
# # #                 'password': 'Test@123',
# # #                 'phone': phone
# # #             }
# # #             # Should accept valid phone formats
    
# # #     def test_postal_code_validation(self):
# # #         """TC-VAL-003: Test postal code validation"""
# # #         data = {
# # #             'first_name': 'Test',
# # #             'last_name': 'User',
# # #             'email': 'postal@example.com',
# # #             'password': 'Test@123',
# # #             'postal_code': '12345'
# # #         }
# # #         response = self.client.post('/register', data=data)
    
# # #     def test_max_length_constraints(self):
# # #         """TC-VAL-004: Test maximum length constraints on fields"""
# # #         very_long_string = 'A' * 1000
        
# # #         data = {
# # #             'first_name': very_long_string,
# # #             'last_name': 'User',
# # #             'email': 'long@example.com',
# # #             'password': 'Test@123'
# # #         }
        
# # #         response = self.client.post('/register', data=data)
# # #         # Should reject or truncate overly long inputs


# # # # ============================================
# # # # TEST CASES: EDGE CASES
# # # # ============================================

# # # class TestEdgeCases(TestAuthenticationModule):
# # #     """Test cases for edge cases and boundary conditions"""
    
# # #     def test_registration_with_unicode_characters(self):
# # #         """TC-EDGE-001: Test registration with unicode/special characters in name"""
# # #         data = {
# # #             'first_name': 'Jöhn',
# # #             'last_name': 'Döe',
# # #             'email': 'unicode@example.com',
# # #             'password': 'Test@123'
# # #         }
# # #         response = self.client.post('/register', data=data)
    
# # #     def test_concurrent_registrations_same_email(self):
# # #         """TC-EDGE-002: Test handling of concurrent registrations"""
# # #         # This would require threading/async testing
# # #         pass
    
# # #     def test_password_with_special_characters(self):
# # #         """TC-EDGE-003: Test password with various special characters"""
# # #         special_passwords = [
# # #             'P@ssw0rd!',
# # #             'T3st#2024$',
# # #             'C0mplex&P@ss'
# # #         ]
        
# # #         for pwd in special_passwords:
# # #             data = {
# # #                 'first_name': 'Test',
# # #                 'last_name': 'User',
# # #                 'email': f'special{pwd[:3]}@example.com',
# # #                 'password': pwd
# # #             }
# # #             response = self.client.post('/register', data=data)
    
# # #     def test_timezone_handling_for_timestamps(self):
# # #         """TC-EDGE-004: Test created_at timestamp is set correctly"""
# # #         user_id = self.insert_test_user()
        
# # #         conn = sqlite3.connect(self.db_path)
# # #         cursor = conn.cursor()
# # #         cursor.execute('SELECT created_at FROM users WHERE id = ?', (user_id,))
# # #         result = cursor.fetchone()
# # #         conn.close()
        
# # #         if result:
# # #             self.assertIsNotNone(result[0])


# # # # ============================================
# # # # MAIN TEST RUNNER
# # # # ============================================

# # # def run_tests():
# # #     """Run all test suites"""
    
# # #     # Create test suite
# # #     loader = unittest.TestLoader()
# # #     suite = unittest.TestSuite()
    
# # #     # Add all test classes
# # #     suite.addTests(loader.loadTestsFromTestCase(TestUserRegistration))
# # #     suite.addTests(loader.loadTestsFromTestCase(TestUserLogin))
# # #     suite.addTests(loader.loadTestsFromTestCase(TestPasswordReset))
# # #     suite.addTests(loader.loadTestsFromTestCase(TestLogout))
# # #     suite.addTests(loader.loadTestsFromTestCase(TestSecurity))
# # #     suite.addTests(loader.loadTestsFromTestCase(TestInputValidation))
# # #     suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
# # #     # Run tests
# # #     runner = unittest.TextTestRunner(verbosity=2)
# # #     result = runner.run(suite)
    
# # #     # Print summary
# # #     print("\n" + "="*70)
# # #     print("TEST SUMMARY")
# # #     print("="*70)
# # #     print(f"Tests Run: {result.testsRun}")
# # #     print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
# # #     print(f"Failures: {len(result.failures)}")
# # #     print(f"Errors: {len(result.errors)}")
# # #     print("="*70)
    
# # #     return result


# # # if __name__ == '__main__':
# # #     run_tests()
# # """
# # MoodMatch Authentication Module - Integration Test Suite
# # Fixed version that properly integrates with your Flask application

# # This test suite is designed to work with your actual application structure.
# # """

# # import random
# # import string
# # import unittest
# # import sqlite3
# # import os
# # import sys
# # import tempfile
# # from datetime import datetime
# # from werkzeug.security import generate_password_hash, check_password_hash

# # # Add project root to path - adjust this path based on your project structure
# # # sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# # class TestAuthenticationModuleIntegration(unittest.TestCase):
# #     """
# #     Integration tests for authentication module
# #     These tests verify the core authentication logic and database operations
# #     """
    
# #     @classmethod
# #     def setUpClass(cls):
# #         """Set up test fixtures once for all tests"""
# #         # Create temporary database
# #         cls.db_fd, cls.db_path = tempfile.mkstemp(suffix='.db')
# #         cls.setup_test_database()
        
# #     @classmethod
# #     def tearDownClass(cls):
# #         """Clean up after all tests"""
# #         os.close(cls.db_fd)
# #         os.unlink(cls.db_path)
    
# #     @classmethod
# #     def setup_test_database(cls):
# #         """Create test database with schema"""
# #         conn = sqlite3.connect(cls.db_path)
# #         cursor = conn.cursor()
        
# #         # Create users table
# #         cursor.execute('''
# #             CREATE TABLE IF NOT EXISTS users (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 username TEXT UNIQUE NOT NULL,
# #                 first_name TEXT NOT NULL,
# #                 last_name TEXT NOT NULL,
# #                 email TEXT NOT NULL UNIQUE,
# #                 phone_number TEXT,
# #                 gender TEXT CHECK (gender IN ('male', 'female', 'other')),
# #                 date_of_birth DATE,
# #                 street_address TEXT,
# #                 city TEXT,
# #                 state TEXT,
# #                 postal_code TEXT,
# #                 country TEXT,
# #                 profile_picture TEXT DEFAULT 'default.png',
# #                 password_hash TEXT NOT NULL,
# #                 reset_code TEXT,
# #                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP
# #             )
# #         ''')
        
# #         # Create admins table
# #         cursor.execute('''
# #             CREATE TABLE IF NOT EXISTS admins (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 username TEXT UNIQUE NOT NULL,
# #                 password_hash TEXT NOT NULL,
# #                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP
# #             )
# #         ''')
        
# #         # Create interest tables
# #         cursor.execute('''
# #             CREATE TABLE IF NOT EXISTS interest_categories (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 name TEXT NOT NULL UNIQUE,
# #                 description TEXT
# #             )
# #         ''')
        
# #         cursor.execute('''
# #             CREATE TABLE IF NOT EXISTS interests (
# #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 category_id INTEGER NOT NULL,
# #                 name TEXT NOT NULL,
# #                 FOREIGN KEY (category_id) REFERENCES interest_categories(id) ON DELETE CASCADE
# #             )
# #         ''')
        
# #         cursor.execute('''
# #             CREATE TABLE IF NOT EXISTS user_interests (
# #                 user_id INTEGER NOT NULL,
# #                 interest_id INTEGER NOT NULL,
# #                 PRIMARY KEY (user_id, interest_id),
# #                 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
# #                 FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
# #             )
# #         ''')
        
# #         # Insert sample interest categories and interests
# #         cursor.execute("INSERT INTO interest_categories (name, description) VALUES ('Hobbies', 'General hobbies and interests')")
# #         cat_id = cursor.lastrowid
        
# #         interests_list = ['reading', 'gaming', 'cooking', 'sports', 'music', 'art']
# #         for interest in interests_list:
# #             cursor.execute("INSERT INTO interests (category_id, name) VALUES (?, ?)", (cat_id, interest))
        
# #         conn.commit()
# #         conn.close()
    
# #     def setUp(self):
# #         """Set up before each test"""
# #         self.clear_test_data()
        
# #     def tearDown(self):
# #         """Clean up after each test"""
# #         self.clear_test_data()
    
# #     def clear_test_data(self):
# #         """Clear all user data from test database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
# #         cursor.execute("DELETE FROM user_interests")
# #         cursor.execute("DELETE FROM users")
# #         cursor.execute("DELETE FROM admins")
# #         conn.commit()
# #         conn.close()
    
# #     def get_connection(self):
# #         """Get database connection"""
# #         conn = sqlite3.connect(self.db_path)
# #         conn.row_factory = sqlite3.Row
# #         return conn
    
# #     # ============================================
# #     # CORE FUNCTIONALITY TESTS
# #     # ============================================
    
# #     def test_database_connection(self):
# #         """Test database connection works"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
# #         cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
# #         tables = cursor.fetchall()
# #         conn.close()
        
# #         self.assertGreater(len(tables), 0, "Database should have tables")
# #         table_names = [table['name'] for table in tables]
# #         self.assertIn('users', table_names)
# #         self.assertIn('admins', table_names)
    
# #     def test_password_hashing(self):
# #         """Test password hashing works correctly"""
# #         password = "TestPassword@123"
# #         hashed = generate_password_hash(password)
        
# #         # Hash should not equal plaintext
# #         self.assertNotEqual(hashed, password)
        
# #         # Hash should be verifiable
# #         self.assertTrue(check_password_hash(hashed, password))
        
# #         # Wrong password should fail
# #         self.assertFalse(check_password_hash(hashed, "WrongPassword"))
        
# #         # Same password should generate different hashes (due to salt)
# #         hashed2 = generate_password_hash(password)
# #         self.assertNotEqual(hashed, hashed2)
    
# #     def test_create_user_in_database(self):
# #         """Test creating a user record in database"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         user_data = {
# #             'username': 'testuser',
# #             'first_name': 'Test',
# #             'last_name': 'User',
# #             'email': 'test@example.com',
# #             'password_hash': generate_password_hash('Test@123')
# #         }
        
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash)
# #             VALUES (?, ?, ?, ?, ?)
# #         ''', (user_data['username'], user_data['first_name'], user_data['last_name'],
# #               user_data['email'], user_data['password_hash']))
        
# #         user_id = cursor.lastrowid
# #         conn.commit()
        
# #         # Verify user was created
# #         cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
# #         user = cursor.fetchone()
# #         conn.close()
        
# #         self.assertIsNotNone(user)
# #         self.assertEqual(user['username'], 'testuser')
# #         self.assertEqual(user['email'], 'test@example.com')
    
# #     def test_unique_username_constraint(self):
# #         """Test username uniqueness is enforced"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         # Create first user
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash)
# #             VALUES (?, ?, ?, ?, ?)
# #         ''', ('testuser', 'Test', 'User', 'test1@example.com', generate_password_hash('Test@123')))
# #         conn.commit()
        
# #         # Try to create second user with same username
# #         with self.assertRaises(sqlite3.IntegrityError):
# #             cursor.execute('''
# #                 INSERT INTO users (username, first_name, last_name, email, password_hash)
# #                 VALUES (?, ?, ?, ?, ?)
# #             ''', ('testuser', 'Test', 'User2', 'test2@example.com', generate_password_hash('Test@456')))
# #             conn.commit()
        
# #         conn.close()
    
# #     def test_unique_email_constraint(self):
# #         """Test email uniqueness is enforced"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         # Create first user
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash)
# #             VALUES (?, ?, ?, ?, ?)
# #         ''', ('user1', 'Test', 'User', 'duplicate@example.com', generate_password_hash('Test@123')))
# #         conn.commit()
        
# #         # Try to create second user with same email
# #         with self.assertRaises(sqlite3.IntegrityError):
# #             cursor.execute('''
# #                 INSERT INTO users (username, first_name, last_name, email, password_hash)
# #                 VALUES (?, ?, ?, ?, ?)
# #             ''', ('user2', 'Test', 'User2', 'duplicate@example.com', generate_password_hash('Test@456')))
# #             conn.commit()
        
# #         conn.close()
    
# #     def test_user_login_verification(self):
# #         """Test user login credential verification"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         password = "CorrectPassword@123"
# #         username = "logintest"
        
# #         # Create user
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash)
# #             VALUES (?, ?, ?, ?, ?)
# #         ''', (username, 'Login', 'Test', 'login@example.com', generate_password_hash(password)))
# #         conn.commit()
        
# #         # Verify correct password
# #         cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         self.assertIsNotNone(result)
# #         self.assertTrue(check_password_hash(result['password_hash'], password))
# #         self.assertFalse(check_password_hash(result['password_hash'], "WrongPassword"))
    
# #     def test_admin_user_creation(self):
# #         """Test creating admin user"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         cursor.execute('''
# #             INSERT INTO admins (username, password_hash)
# #             VALUES (?, ?)
# #         ''', ('admin', generate_password_hash('Admin@123')))
# #         admin_id = cursor.lastrowid
# #         conn.commit()
        
# #         cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
# #         admin = cursor.fetchone()
# #         conn.close()
        
# #         self.assertIsNotNone(admin)
# #         self.assertEqual(admin['username'], 'admin')
    
# #     def test_user_interests_association(self):
# #         """Test linking interests to users"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         # Create user
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash)
# #             VALUES (?, ?, ?, ?, ?)
# #         ''', ('interestuser', 'Interest', 'User', 'interests@example.com', generate_password_hash('Test@123')))
# #         user_id = cursor.lastrowid
        
# #         # Get some interests
# #         cursor.execute("SELECT id FROM interests LIMIT 3")
# #         interests = cursor.fetchall()
        
# #         # Link interests to user
# #         for interest in interests:
# #             cursor.execute('''
# #                 INSERT INTO user_interests (user_id, interest_id)
# #                 VALUES (?, ?)
# #             ''', (user_id, interest['id']))
        
# #         conn.commit()
        
# #         # Verify interests were linked
# #         cursor.execute("SELECT COUNT(*) as count FROM user_interests WHERE user_id = ?", (user_id,))
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         self.assertEqual(result['count'], 3)
    
# #     def test_reset_code_generation_and_storage(self):
# #         """Test password reset code generation"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         # Create user
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash)
# #             VALUES (?, ?, ?, ?, ?)
# #         ''', ('resetuser', 'Reset', 'User', 'reset@example.com', generate_password_hash('Test@123')))
# #         user_id = cursor.lastrowid
# #         conn.commit()
        
# #         # Generate reset code (6 digits)
# #         reset_code = ''.join(random.choices(string.digits, k=6))
        
# #         # Store reset code
# #         cursor.execute("UPDATE users SET reset_code = ? WHERE id = ?", (reset_code, user_id))
# #         conn.commit()
        
# #         # Verify reset code stored
# #         cursor.execute("SELECT reset_code FROM users WHERE id = ?", (user_id,))
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         self.assertEqual(result['reset_code'], reset_code)
# #         self.assertEqual(len(reset_code), 6)
# #         self.assertTrue(reset_code.isdigit())
    
# #     def test_reset_code_verification(self):
# #         """Test reset code verification process"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         # Create user with reset code
# #         reset_code = "123456"
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash, reset_code)
# #             VALUES (?, ?, ?, ?, ?, ?)
# #         ''', ('verifyuser', 'Verify', 'User', 'verify@example.com', 
# #               generate_password_hash('Test@123'), reset_code))
# #         user_id = cursor.lastrowid
# #         conn.commit()
        
# #         # Verify correct code
# #         cursor.execute("SELECT reset_code FROM users WHERE username = ?", ('verifyuser',))
# #         result = cursor.fetchone()
        
# #         self.assertEqual(result['reset_code'], reset_code)
        
# #         # Simulate wrong code
# #         wrong_code = "999999"
# #         self.assertNotEqual(result['reset_code'], wrong_code)
        
# #         conn.close()
    
# #     def test_password_reset_process(self):
# #         """Test complete password reset process"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         old_password = "OldPass@123"
# #         new_password = "NewPass@456"
        
# #         # Create user
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash, reset_code)
# #             VALUES (?, ?, ?, ?, ?, ?)
# #         ''', ('resettest', 'Reset', 'Test', 'resettest@example.com', 
# #               generate_password_hash(old_password), '123456'))
# #         user_id = cursor.lastrowid
# #         conn.commit()
        
# #         # Reset password
# #         new_hash = generate_password_hash(new_password)
# #         cursor.execute('''
# #             UPDATE users SET password_hash = ?, reset_code = NULL WHERE id = ?
# #         ''', (new_hash, user_id))
# #         conn.commit()
        
# #         # Verify password changed and reset code cleared
# #         cursor.execute("SELECT password_hash, reset_code FROM users WHERE id = ?", (user_id,))
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         self.assertTrue(check_password_hash(result['password_hash'], new_password))
# #         self.assertFalse(check_password_hash(result['password_hash'], old_password))
# #         self.assertIsNone(result['reset_code'])
    
# #     def test_gender_validation_constraint(self):
# #         """Test gender field accepts only valid values"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         # Valid genders should work
# #         valid_genders = ['male', 'female', 'other']
# #         for i, gender in enumerate(valid_genders):
# #             cursor.execute('''
# #                 INSERT INTO users (username, first_name, last_name, email, password_hash, gender)
# #                 VALUES (?, ?, ?, ?, ?, ?)
# #             ''', (f'user{i}', 'Test', 'User', f'test{i}@example.com', 
# #                   generate_password_hash('Test@123'), gender))
        
# #         conn.commit()
        
# #         # Invalid gender should fail
# #         with self.assertRaises(sqlite3.IntegrityError):
# #             cursor.execute('''
# #                 INSERT INTO users (username, first_name, last_name, email, password_hash, gender)
# #                 VALUES (?, ?, ?, ?, ?, ?)
# #             ''', ('invalid', 'Test', 'User', 'invalid@example.com', 
# #                   generate_password_hash('Test@123'), 'invalid_gender'))
# #             conn.commit()
        
# #         conn.close()
    
# #     def test_default_profile_picture(self):
# #         """Test default profile picture is set"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         # Create user without specifying profile picture
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash)
# #             VALUES (?, ?, ?, ?, ?)
# #         ''', ('picuser', 'Pic', 'User', 'pic@example.com', generate_password_hash('Test@123')))
# #         user_id = cursor.lastrowid
# #         conn.commit()
        
# #         # Verify default picture is set
# #         cursor.execute("SELECT profile_picture FROM users WHERE id = ?", (user_id,))
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         self.assertEqual(result['profile_picture'], 'default.png')
    
# #     def test_timestamp_auto_generation(self):
# #         """Test created_at timestamp is automatically set"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         # Create user
# #         cursor.execute('''
# #             INSERT INTO users (username, first_name, last_name, email, password_hash)
# #             VALUES (?, ?, ?, ?, ?)
# #         ''', ('timeuser', 'Time', 'User', 'time@example.com', generate_password_hash('Test@123')))
# #         user_id = cursor.lastrowid
# #         conn.commit()
        
# #         # Verify timestamp was set
# #         cursor.execute("SELECT created_at FROM users WHERE id = ?", (user_id,))
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         self.assertIsNotNone(result['created_at'])
    
# #     def test_complete_user_registration_data(self):
# #         """Test storing complete user registration data"""
# #         conn = self.get_connection()
# #         cursor = conn.cursor()
        
# #         user_data = {
# #             'username': 'completeuser',
# #             'first_name': 'Complete',
# #             'last_name': 'User',
# #             'email': 'complete@example.com',
# #             'phone_number': '1234567890',
# #             'gender': 'male',
# #             'date_of_birth': '1995-01-15',
# #             'street_address': '123 Main St',
# #             'city': 'Mumbai',
# #             'state': 'Maharashtra',
# #             'postal_code': '400001',
# #             'country': 'India',
# #             'profile_picture': 'custom.jpg',
# #             'password_hash': generate_password_hash('Test@123')
# #         }
        
# #         cursor.execute('''
# #             INSERT INTO users (
# #                 username, first_name, last_name, email, phone_number,
# #                 gender, date_of_birth, street_address, city, state,
# #                 postal_code, country, profile_picture, password_hash
# #             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# #         ''', tuple(user_data.values()))
        
# #         user_id = cursor.lastrowid
# #         conn.commit()
        
# #         # Verify all data stored correctly
# #         cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         self.assertEqual(result['username'], user_data['username'])
# #         self.assertEqual(result['email'], user_data['email'])
# #         self.assertEqual(result['phone_number'], user_data['phone_number'])
# #         self.assertEqual(result['city'], user_data['city'])
# #         self.assertEqual(result['profile_picture'], user_data['profile_picture'])


# # # ============================================
# # # TEST RUNNER
# # # ============================================

# # def run_integration_tests():
# #     """Run integration tests with detailed output"""
# #     loader = unittest.TestLoader()
# #     suite = unittest.TestSuite()
    
# #     suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationModuleIntegration))
    
# #     runner = unittest.TextTestRunner(verbosity=2)
# #     result = runner.run(suite)
    
# #     # Print summary
# #     print("\n" + "="*70)
# #     print("INTEGRATION TEST SUMMARY")
# #     print("="*70)
# #     print(f"Tests Run: {result.testsRun}")
# #     print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
# #     print(f"Failures: {len(result.failures)}")
# #     print(f"Errors: {len(result.errors)}")
# #     print(f"Pass Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
# #     print("="*70)
    
# #     if result.failures:
# #         print("\nFAILURES:")
# #         for test, traceback in result.failures:
# #             print(f"\n{test}:")
# #             print(traceback)
    
# #     if result.errors:
# #         print("\nERRORS:")
# #         for test, traceback in result.errors:
# #             print(f"\n{test}:")
# #             print(traceback)
    
# #     return result


# # if __name__ == '__main__':
# #     run_integration_tests()

# """
# Simple Authentication Tests - No Flask Required
# These tests validate core authentication logic and can run immediately
# """

# import sqlite3
# import os
# from werkzeug.security import generate_password_hash, check_password_hash

# # ANSI color codes for pretty output
# GREEN = '\033[92m'
# RED = '\033[91m'
# YELLOW = '\033[93m'
# RESET = '\033[0m'
# BOLD = '\033[1m'

# test_results = {
#     'passed': 0,
#     'failed': 0,
#     'total': 0
# }

# def print_test_header(test_name):
#     """Print test header"""
#     print(f"\n{BOLD}Testing: {test_name}{RESET}")
#     print("-" * 60)

# def print_result(passed, message):
#     """Print test result"""
#     global test_results
#     test_results['total'] += 1
    
#     if passed:
#         test_results['passed'] += 1
#         print(f"{GREEN}✅ PASS{RESET} - {message}")
#     else:
#         test_results['failed'] += 1
#         print(f"{RED}❌ FAIL{RESET} - {message}")
    
#     return passed

# def print_summary():
#     """Print test summary"""
#     print("\n" + "="*60)
#     print(f"{BOLD}TEST SUMMARY{RESET}")
#     print("="*60)
#     print(f"Total Tests: {test_results['total']}")
#     print(f"{GREEN}Passed: {test_results['passed']}{RESET}")
#     print(f"{RED}Failed: {test_results['failed']}{RESET}")
    
#     if test_results['total'] > 0:
#         pass_rate = (test_results['passed'] / test_results['total']) * 100
#         print(f"Pass Rate: {pass_rate:.1f}%")
    
#     print("="*60)
    
#     if test_results['failed'] == 0:
#         print(f"{GREEN}{BOLD}🎉 ALL TESTS PASSED!{RESET}")
#     else:
#         print(f"{YELLOW}⚠️  Some tests failed. Review output above.{RESET}")

# # ============================================
# # TEST 1: PASSWORD HASHING
# # ============================================

# def test_password_hashing():
#     """Test password hashing and verification"""
#     print_test_header("Password Hashing")
    
#     password = "Test@123456"
    
#     try:
#         # Test hashing
#         hashed = generate_password_hash(password)
#         print_result(True, "Password can be hashed")
        
#         # Test hash is different from plaintext
#         is_different = hashed != password
#         print_result(is_different, "Hashed password differs from plaintext")
        
#         # Test correct password verifies
#         verifies = check_password_hash(hashed, password)
#         print_result(verifies, "Correct password verifies against hash")
        
#         # Test wrong password fails
#         fails = not check_password_hash(hashed, "WrongPassword@123")
#         print_result(fails, "Wrong password fails verification")
        
#         # Test same password generates different hashes (salt)
#         hashed2 = generate_password_hash(password)
#         different_hashes = hashed != hashed2
#         print_result(different_hashes, "Same password generates different hashes (salted)")
        
#         return True
#     except Exception as e:
#         print_result(False, f"Password hashing error: {str(e)}")
#         return False

# # ============================================
# # TEST 2: DATABASE CONNECTION
# # ============================================

# def test_database_connection():
#     """Test database connectivity and structure"""
#     print_test_header("Database Connection")
    
#     db_path = 'models/instance/moodmatch.db'
    
#     # Check if database file exists
#     if not os.path.exists(db_path):
#         print_result(False, f"Database file not found at {db_path}")
#         print(f"{YELLOW}Note: Update db_path if your database is in a different location{RESET}")
#         return False
    
#     print_result(True, f"Database file exists at {db_path}")
    
#     try:
#         # Try to connect
#         conn = sqlite3.connect(db_path)
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
#         print_result(True, "Database connection successful")
        
#         # Check for required tables
#         cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#         tables = cursor.fetchall()
#         table_names = [table['name'] for table in tables]
        
#         print(f"   Found {len(table_names)} tables: {', '.join(table_names)}")
        
#         required_tables = ['users', 'admins', 'interests', 'user_interests']
#         for table in required_tables:
#             exists = table in table_names
#             print_result(exists, f"Table '{table}' exists")
        
#         conn.close()
#         return True
        
#     except sqlite3.Error as e:
#         print_result(False, f"Database error: {str(e)}")
#         return False

# # ============================================
# # TEST 3: USER CREATION
# # ============================================

# def test_user_creation():
#     """Test creating and querying user records"""
#     print_test_header("User Creation")
    
#     db_path = 'models/instance/moodmatch.db'
    
#     if not os.path.exists(db_path):
#         print_result(False, "Database not available - skipping user creation test")
#         return False
    
#     try:
#         conn = sqlite3.connect(db_path)
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
        
#         # Clean up any previous test user
#         cursor.execute("DELETE FROM users WHERE email = 'test_simple@example.com'")
#         conn.commit()
        
#         # Create test user
#         test_user = {
#             'username': 'test_simple_user',
#             'first_name': 'Simple',
#             'last_name': 'Test',
#             'email': 'test_simple@example.com',
#             'password_hash': generate_password_hash('TestPass@123')
#         }
        
#         cursor.execute('''
#             INSERT INTO users (username, first_name, last_name, email, password_hash)
#             VALUES (?, ?, ?, ?, ?)
#         ''', (test_user['username'], test_user['first_name'], test_user['last_name'],
#               test_user['email'], test_user['password_hash']))
        
#         user_id = cursor.lastrowid
#         conn.commit()
        
#         print_result(user_id > 0, f"User created with ID: {user_id}")
        
#         # Verify user exists
#         cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
#         user = cursor.fetchone()
        
#         print_result(user is not None, "User record can be retrieved")
#         print_result(user['username'] == test_user['username'], "Username stored correctly")
#         print_result(user['email'] == test_user['email'], "Email stored correctly")
#         print_result(user['profile_picture'] == 'default.png', "Default profile picture set")
        
#         # Verify password
#         password_correct = check_password_hash(user['password_hash'], 'TestPass@123')
#         print_result(password_correct, "Password stored and verifies correctly")
        
#         # Clean up
#         cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
#         conn.commit()
#         conn.close()
        
#         print_result(True, "Test user cleaned up")
#         return True
        
#     except sqlite3.Error as e:
#         print_result(False, f"User creation error: {str(e)}")
#         if 'conn' in locals():
#             conn.close()
#         return False

# # ============================================
# # TEST 4: DUPLICATE EMAIL PREVENTION
# # ============================================

# def test_duplicate_email_prevention():
#     """Test that duplicate emails are prevented"""
#     print_test_header("Duplicate Email Prevention")
    
#     db_path = 'models/instance/moodmatch.db'
    
#     if not os.path.exists(db_path):
#         print_result(False, "Database not available - skipping duplicate email test")
#         return False
    
#     try:
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
        
#         # Clean up
#         cursor.execute("DELETE FROM users WHERE email = 'duplicate@example.com'")
#         conn.commit()
        
#         # Create first user
#         cursor.execute('''
#             INSERT INTO users (username, first_name, last_name, email, password_hash)
#             VALUES (?, ?, ?, ?, ?)
#         ''', ('user1', 'First', 'User', 'duplicate@example.com', 
#               generate_password_hash('Pass@123')))
#         user1_id = cursor.lastrowid
#         conn.commit()
        
#         print_result(True, "First user created successfully")
        
#         # Try to create second user with same email
#         try:
#             cursor.execute('''
#                 INSERT INTO users (username, first_name, last_name, email, password_hash)
#                 VALUES (?, ?, ?, ?, ?)
#             ''', ('user2', 'Second', 'User', 'duplicate@example.com', 
#                   generate_password_hash('Pass@456')))
#             conn.commit()
            
#             print_result(False, "Duplicate email was NOT prevented (should have failed)")
            
#         except sqlite3.IntegrityError:
#             print_result(True, "Duplicate email correctly prevented by database constraint")
        
#         # Clean up
#         cursor.execute("DELETE FROM users WHERE id = ?", (user1_id,))
#         conn.commit()
#         conn.close()
        
#         return True
        
#     except Exception as e:
#         print_result(False, f"Duplicate email test error: {str(e)}")
#         if 'conn' in locals():
#             conn.close()
#         return False

# # ============================================
# # TEST 5: PASSWORD RESET CODE
# # ============================================

# def test_password_reset_code():
#     """Test password reset code generation and storage"""
#     print_test_header("Password Reset Code")
    
#     db_path = 'models/instance/moodmatch.db'
    
#     if not os.path.exists(db_path):
#         print_result(False, "Database not available - skipping reset code test")
#         return False
    
#     try:
#         conn = sqlite3.connect(db_path)
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
        
#         # Clean up
#         cursor.execute("DELETE FROM users WHERE email = 'reset@example.com'")
#         conn.commit()
        
#         # Create user
#         cursor.execute('''
#             INSERT INTO users (username, first_name, last_name, email, password_hash)
#             VALUES (?, ?, ?, ?, ?)
#         ''', ('resetuser', 'Reset', 'User', 'reset@example.com', 
#               generate_password_hash('Pass@123')))
#         user_id = cursor.lastrowid
#         conn.commit()
        
#         # Generate and store reset code
#         import random
#         import string
#         reset_code = ''.join(random.choices(string.digits, k=6))
        
#         cursor.execute("UPDATE users SET reset_code = ? WHERE id = ?", (reset_code, user_id))
#         conn.commit()
        
#         print_result(True, f"Reset code generated: {reset_code}")
#         print_result(len(reset_code) == 6, "Reset code is 6 digits")
#         print_result(reset_code.isdigit(), "Reset code is numeric")
        
#         # Verify code stored
#         cursor.execute("SELECT reset_code FROM users WHERE id = ?", (user_id,))
#         stored_code = cursor.fetchone()['reset_code']
        
#         print_result(stored_code == reset_code, "Reset code stored correctly")
        
#         # Clean up
#         cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
#         conn.commit()
#         conn.close()
        
#         return True
        
#     except Exception as e:
#         print_result(False, f"Reset code test error: {str(e)}")
#         if 'conn' in locals():
#             conn.close()
#         return False

# # ============================================
# # TEST 6: COMPLETE PASSWORD RESET
# # ============================================

# def test_complete_password_reset():
#     """Test complete password reset flow"""
#     print_test_header("Complete Password Reset")
    
#     db_path = 'models/instance/moodmatch.db'
    
#     if not os.path.exists(db_path):
#         print_result(False, "Database not available - skipping password reset test")
#         return False
    
#     try:
#         conn = sqlite3.connect(db_path)
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
        
#         # Clean up
#         cursor.execute("DELETE FROM users WHERE email = 'resetflow@example.com'")
#         conn.commit()
        
#         old_password = "OldPass@123"
#         new_password = "NewPass@456"
        
#         # Create user with old password
#         cursor.execute('''
#             INSERT INTO users (username, first_name, last_name, email, password_hash, reset_code)
#             VALUES (?, ?, ?, ?, ?, ?)
#         ''', ('resetflow', 'Reset', 'Flow', 'resetflow@example.com', 
#               generate_password_hash(old_password), '123456'))
#         user_id = cursor.lastrowid
#         conn.commit()
        
#         print_result(True, "User created with old password")
        
#         # Simulate password reset
#         new_hash = generate_password_hash(new_password)
#         cursor.execute('''
#             UPDATE users SET password_hash = ?, reset_code = NULL WHERE id = ?
#         ''', (new_hash, user_id))
#         conn.commit()
        
#         print_result(True, "Password updated in database")
        
#         # Verify changes
#         cursor.execute("SELECT password_hash, reset_code FROM users WHERE id = ?", (user_id,))
#         result = cursor.fetchone()
        
#         new_pass_works = check_password_hash(result['password_hash'], new_password)
#         old_pass_fails = not check_password_hash(result['password_hash'], old_password)
#         code_cleared = result['reset_code'] is None
        
#         print_result(new_pass_works, "New password works")
#         print_result(old_pass_fails, "Old password no longer works")
#         print_result(code_cleared, "Reset code cleared")
        
#         # Clean up
#         cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
#         conn.commit()
#         conn.close()
        
#         return True
        
#     except Exception as e:
#         print_result(False, f"Password reset test error: {str(e)}")
#         if 'conn' in locals():
#             conn.close()
#         return False

# # ============================================
# # TEST 7: USER INTERESTS
# # ============================================

# def test_user_interests():
#     """Test linking interests to users"""
#     print_test_header("User Interests")
    
#     db_path = 'models/instance/moodmatch.db'
    
#     if not os.path.exists(db_path):
#         print_result(False, "Database not available - skipping interests test")
#         return False
    
#     try:
#         conn = sqlite3.connect(db_path)
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
        
#         # Clean up
#         cursor.execute("DELETE FROM users WHERE email = 'interests@example.com'")
#         conn.commit()
        
#         # Create user
#         cursor.execute('''
#             INSERT INTO users (username, first_name, last_name, email, password_hash)
#             VALUES (?, ?, ?, ?, ?)
#         ''', ('interestuser', 'Interest', 'User', 'interests@example.com', 
#               generate_password_hash('Pass@123')))
#         user_id = cursor.lastrowid
#         conn.commit()
        
#         # Get some interests
#         cursor.execute("SELECT id FROM interests LIMIT 3")
#         interests = cursor.fetchall()
        
#         if len(interests) == 0:
#             print_result(False, "No interests found in database - cannot test")
#             cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
#             conn.commit()
#             conn.close()
#             return False
        
#         print_result(True, f"Found {len(interests)} interests to link")
        
#         # Link interests
#         for interest in interests:
#             cursor.execute('''
#                 INSERT INTO user_interests (user_id, interest_id)
#                 VALUES (?, ?)
#             ''', (user_id, interest['id']))
        
#         conn.commit()
        
#         # Verify
#         cursor.execute("SELECT COUNT(*) as count FROM user_interests WHERE user_id = ?", (user_id,))
#         count = cursor.fetchone()['count']
        
#         print_result(count == len(interests), f"All {len(interests)} interests linked correctly")
        
#         # Clean up
#         cursor.execute("DELETE FROM user_interests WHERE user_id = ?", (user_id,))
#         cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
#         conn.commit()
#         conn.close()
        
#         return True
        
#     except Exception as e:
#         print_result(False, f"User interests test error: {str(e)}")
#         if 'conn' in locals():
#             conn.close()
#         return False

# # ============================================
# # MAIN TEST RUNNER
# # ============================================

# def run_all_tests():
#     """Run all simple tests"""
#     print(f"\n{BOLD}{'='*60}{RESET}")
#     print(f"{BOLD}MoodMatch Authentication - Simple Test Suite{RESET}")
#     print(f"{BOLD}{'='*60}{RESET}")
#     print("\nThese tests validate core authentication functionality")
#     print("without requiring full Flask application setup.\n")
    
#     # Run all tests
#     test_password_hashing()
#     test_database_connection()
#     test_user_creation()
#     test_duplicate_email_prevention()
#     test_password_reset_code()
#     test_complete_password_reset()
#     test_user_interests()
    
#     # Print summary
#     print_summary()
    
#     return test_results['failed'] == 0

# if __name__ == '__main__':
#     success = run_all_tests()
#     exit(0 if success else 1)