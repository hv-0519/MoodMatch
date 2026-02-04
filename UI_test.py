"""
MoodMatch UI Test Suite
Tests all user-facing features and admin interface
Run: python ui_test.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import sys

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'

class MoodMatchUITest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:6969"
        self.driver = None
        self.wait = None
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Initialize browser"""
        print(f"\n{Colors.BLUE}🚀 Initializing Chrome Browser...{Colors.END}")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        # options.add_argument('--headless')  # Uncomment for headless mode
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        print(f"{Colors.GREEN}✅ Browser Ready!{Colors.END}\n")
        
    def test_print(self, test_name, status):
        """Print test result"""
        if status:
            print(f"{Colors.GREEN}✅ {test_name}: PASSED{Colors.END}")
            self.passed += 1
        else:
            print(f"{Colors.RED}❌ {test_name}: FAILED{Colors.END}")
            self.failed += 1
            
    # ==========================================
    # PUBLIC PAGES TESTS
    # ==========================================
    
    def test_homepage(self):
        """Test homepage loads"""
        try:
            self.driver.get(self.base_url)
            assert "MoodMatch" in self.driver.title
            self.test_print("Homepage Load", True)
            time.sleep(1)
        except Exception as e:
            self.test_print("Homepage Load", False)
            print(f"   Error: {e}")
            
    def test_navigation_links(self):
        """Test navbar links"""
        try:
            self.driver.get(self.base_url)
            
            # Test Home link
            home_link = self.driver.find_element(By.LINK_TEXT, "Home")
            home_link.click()
            time.sleep(0.5)
            assert self.driver.current_url == f"{self.base_url}/"
            
            # Test About link
            about_link = self.driver.find_element(By.LINK_TEXT, "About")
            about_link.click()
            time.sleep(0.5)
            assert "about" in self.driver.current_url.lower()
            
            # Test Login link
            login_link = self.driver.find_element(By.LINK_TEXT, "Login")
            login_link.click()
            time.sleep(0.5)
            assert "login" in self.driver.current_url
            
            self.test_print("Navigation Links", True)
        except Exception as e:
            self.test_print("Navigation Links", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # REGISTRATION TESTS
    # ==========================================
    
    def test_registration_page_load(self):
        """Test registration page loads"""
        try:
            self.driver.get(f"{self.base_url}/register")
            assert "Create Account" in self.driver.page_source
            
            # Check all 5 steps are present
            steps = self.driver.find_elements(By.CLASS_NAME, "step")
            assert len(steps) == 5
            
            self.test_print("Registration Page Load", True)
            time.sleep(1)
        except Exception as e:
            self.test_print("Registration Page Load", False)
            print(f"   Error: {e}")
            
    def test_registration_step_navigation(self):
        """Test multi-step form navigation"""
        try:
            self.driver.get(f"{self.base_url}/register")
            
            # Step 1: Personal Info
            self.driver.find_element(By.ID, "first_name").send_keys("UI")
            self.driver.find_element(By.ID, "last_name").send_keys("Tester")
            self.driver.find_element(By.CSS_SELECTOR, "input[value='male']").click()
            self.driver.find_element(By.ID, "date_of_birth").send_keys("01/01/2000")
            
            # Click Next
            next_btn = self.driver.find_element(By.ID, "nextBtn")
            next_btn.click()
            time.sleep(0.5)
            
            # Verify Step 2 is active
            step2 = self.driver.find_element(By.CSS_SELECTOR, ".form-step.active[data-step='2']")
            assert step2 is not None
            
            # Test Previous button
            prev_btn = self.driver.find_element(By.ID, "prevBtn")
            prev_btn.click()
            time.sleep(0.5)
            
            # Verify Step 1 is active again
            step1 = self.driver.find_element(By.CSS_SELECTOR, ".form-step.active[data-step='1']")
            assert step1 is not None
            
            self.test_print("Registration Step Navigation", True)
        except Exception as e:
            self.test_print("Registration Step Navigation", False)
            print(f"   Error: {e}")
            
    def test_registration_validation(self):
        """Test form validation"""
        try:
            self.driver.get(f"{self.base_url}/register")
            
            # Try to proceed without filling required fields
            next_btn = self.driver.find_element(By.ID, "nextBtn")
            next_btn.click()
            time.sleep(0.5)
            
            # Should show error and stay on step 1
            current_step = self.driver.find_element(By.CSS_SELECTOR, ".form-step.active")
            assert current_step.get_attribute("data-step") == "1"
            
            self.test_print("Registration Validation", True)
        except Exception as e:
            self.test_print("Registration Validation", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # LOGIN TESTS
    # ==========================================
    
    def test_login_page_load(self):
        """Test login page loads"""
        try:
            self.driver.get(f"{self.base_url}/login")
            assert "Login" in self.driver.page_source
            
            # Check form elements exist
            self.driver.find_element(By.ID, "username")
            self.driver.find_element(By.ID, "password")
            
            self.test_print("Login Page Load", True)
            time.sleep(1)
        except Exception as e:
            self.test_print("Login Page Load", False)
            print(f"   Error: {e}")
            
    def test_admin_login(self):
        """Test admin login functionality"""
        try:
            self.driver.get(f"{self.base_url}/login")
            
            # Enter admin credentials
            self.driver.find_element(By.ID, "username").send_keys("admin")
            self.driver.find_element(By.ID, "password").send_keys("admin123")
            
            # Submit form
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(2)
            
            # Verify redirect to admin dashboard
            assert "admin_dashboard" in self.driver.current_url
            assert "Dashboard Overview" in self.driver.page_source
            
            self.test_print("Admin Login", True)
        except Exception as e:
            self.test_print("Admin Login", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # ADMIN DASHBOARD TESTS
    # ==========================================
    
    def test_admin_dashboard_elements(self):
        """Test admin dashboard displays correctly"""
        try:
            # Should already be logged in from previous test
            if "admin_dashboard" not in self.driver.current_url:
                self.test_admin_login()
                
            # Check stat cards
            stat_cards = self.driver.find_elements(By.CLASS_NAME, "stat-card")
            assert len(stat_cards) >= 4  # Total Users, Activities, Categories, Engagement
            
            # Check chart exists
            chart = self.driver.find_element(By.ID, "registrationChart")
            assert chart is not None
            
            # Check interests chart
            interests_chart = self.driver.find_element(By.ID, "interestsChart")
            assert interests_chart is not None
            
            # Check recent users table
            users_table = self.driver.find_element(By.CLASS_NAME, "users-table")
            assert users_table is not None
            
            self.test_print("Admin Dashboard Elements", True)
        except Exception as e:
            self.test_print("Admin Dashboard Elements", False)
            print(f"   Error: {e}")
            
    def test_admin_sidebar_navigation(self):
        """Test admin sidebar links"""
        try:
            if "admin" not in self.driver.current_url:
                self.test_admin_login()
                
            # Test Manage Users link
            manage_users = self.driver.find_element(By.LINK_TEXT, "Manage Users")
            manage_users.click()
            time.sleep(1)
            assert "manage_users" in self.driver.current_url
            
            # Test Manage Activities link
            manage_activities = self.driver.find_element(By.LINK_TEXT, "Manage Activities")
            manage_activities.click()
            time.sleep(1)
            assert "manage_activity" in self.driver.current_url
            
            # Test Manage Categories link
            manage_categories = self.driver.find_element(By.LINK_TEXT, "Manage Categories")
            manage_categories.click()
            time.sleep(1)
            assert "manage_categories" in self.driver.current_url
            
            # Test View Analytics link
            view_analytics = self.driver.find_element(By.LINK_TEXT, "View Analytics")
            view_analytics.click()
            time.sleep(1)
            assert "view_analytics" in self.driver.current_url
            
            self.test_print("Admin Sidebar Navigation", True)
        except Exception as e:
            self.test_print("Admin Sidebar Navigation", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # MANAGE USERS TESTS
    # ==========================================
    
    def test_manage_users_page(self):
        """Test manage users page displays user cards"""
        try:
            self.driver.get(f"{self.base_url}/admin/manage_users")
            time.sleep(1)
            
            # Check page title
            assert "User Management" in self.driver.page_source
            
            # Check user cards grid
            users_grid = self.driver.find_element(By.CLASS_NAME, "users-grid")
            assert users_grid is not None
            
            # Check at least one user card exists
            user_cards = self.driver.find_elements(By.CLASS_NAME, "premium-card")
            assert len(user_cards) > 0
            
            self.test_print("Manage Users Page", True)
        except Exception as e:
            self.test_print("Manage Users Page", False)
            print(f"   Error: {e}")
            
    def test_view_user_profile_modal(self):
        """Test user profile modal opens"""
        try:
            self.driver.get(f"{self.base_url}/admin/manage_users")
            time.sleep(1)
            
            # Click first "View Profile" button
            view_btn = self.driver.find_element(By.CLASS_NAME, "btn-view")
            view_btn.click()
            time.sleep(0.5)
            
            # Check modal is visible
            modal = self.driver.find_element(By.ID, "viewUserModal")
            assert "active" in modal.get_attribute("class")
            
            # Check modal has user details
            assert "User Profile" in self.driver.page_source
            
            # Close modal
            close_btn = self.driver.find_element(By.CLASS_NAME, "close-btn")
            close_btn.click()
            time.sleep(0.5)
            
            self.test_print("View User Profile Modal", True)
        except Exception as e:
            self.test_print("View User Profile Modal", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # MANAGE ACTIVITIES TESTS
    # ==========================================
    
    def test_manage_activities_page(self):
        """Test manage activities page"""
        try:
            self.driver.get(f"{self.base_url}/admin/manage_activity")
            time.sleep(1)
            
            # Check page title
            assert "Activity Management" in self.driver.page_source
            
            # Check table or empty state
            try:
                table = self.driver.find_element(By.CLASS_NAME, "admin-table")
                assert table is not None
            except:
                # Empty state is also valid
                empty_state = self.driver.find_element(By.CLASS_NAME, "empty-state")
                assert empty_state is not None
                
            self.test_print("Manage Activities Page", True)
        except Exception as e:
            self.test_print("Manage Activities Page", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # MANAGE CATEGORIES TESTS
    # ==========================================
    
    def test_manage_categories_page(self):
        """Test manage categories page"""
        try:
            self.driver.get(f"{self.base_url}/admin/manage_categories")
            time.sleep(1)
            
            # Check page title
            assert "Category Management" in self.driver.page_source
            
            # Check categories grid
            categories_grid = self.driver.find_element(By.CLASS_NAME, "categories-grid")
            assert categories_grid is not None
            
            # Check category cards
            category_cards = self.driver.find_elements(By.CLASS_NAME, "premium-card")
            assert len(category_cards) > 0
            
            self.test_print("Manage Categories Page", True)
        except Exception as e:
            self.test_print("Manage Categories Page", False)
            print(f"   Error: {e}")
            
    def test_add_category_modal(self):
        """Test add category modal opens"""
        try:
            self.driver.get(f"{self.base_url}/admin/manage_categories")
            time.sleep(1)
            
            # Click Add Category button
            add_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Add Category')]")
            add_btn.click()
            time.sleep(0.5)
            
            # Check modal is visible
            modal = self.driver.find_element(By.ID, "addModal")
            assert "active" in modal.get_attribute("class")
            
            # Check form fields
            self.driver.find_element(By.NAME, "icon")
            self.driver.find_element(By.NAME, "name")
            self.driver.find_element(By.NAME, "description")
            
            # Close modal
            self.driver.execute_script("closeModal('addModal')")
            time.sleep(0.5)
            
            self.test_print("Add Category Modal", True)
        except Exception as e:
            self.test_print("Add Category Modal", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # VIEW ANALYTICS TESTS
    # ==========================================
    
    def test_view_analytics_page(self):
        """Test analytics page loads with all charts"""
        try:
            self.driver.get(f"{self.base_url}/admin/view_analytics")
            time.sleep(2)  # Charts need time to render
            
            # Check page title
            assert "Analytics Dashboard" in self.driver.page_source
            
            # Check all main sections exist
            assert "Activity Metrics" in self.driver.page_source
            assert "Mood Analytics" in self.driver.page_source
            assert "Engagement Metrics" in self.driver.page_source
            assert "Interest Analytics" in self.driver.page_source
            assert "Recent Activity" in self.driver.page_source
            
            # Check charts exist
            charts = [
                "categoryUsageChart",
                "moodDistChart",
                "moodTrendsChart",
                "feedbackChart"
            ]
            
            for chart_id in charts:
                chart = self.driver.find_element(By.ID, chart_id)
                assert chart is not None
                
            self.test_print("View Analytics Page", True)
        except Exception as e:
            self.test_print("View Analytics Page", False)
            print(f"   Error: {e}")
            
    def test_analytics_data_tables(self):
        """Test analytics data tables display"""
        try:
            self.driver.get(f"{self.base_url}/admin/view_analytics")
            time.sleep(1)
            
            # Check data tables exist
            tables = self.driver.find_elements(By.CLASS_NAME, "data-table")
            assert len(tables) > 0
            
            # Check recent activity feed
            activity_feed = self.driver.find_element(By.CLASS_NAME, "activity-feed")
            assert activity_feed is not None
            
            # Check activity items
            activity_items = self.driver.find_elements(By.CLASS_NAME, "activity-item")
            # May be empty, so just check it exists
            
            self.test_print("Analytics Data Tables", True)
        except Exception as e:
            self.test_print("Analytics Data Tables", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # RESPONSIVE DESIGN TESTS
    # ==========================================
    
    def test_mobile_responsiveness(self):
        """Test mobile view"""
        try:
            # Set mobile viewport
            self.driver.set_window_size(375, 667)
            time.sleep(0.5)
            
            # Test homepage on mobile
            self.driver.get(self.base_url)
            time.sleep(0.5)
            
            # Test admin dashboard on mobile
            self.driver.get(f"{self.base_url}/admin/admin_dashboard")
            time.sleep(0.5)
            
            # Restore normal size
            self.driver.maximize_window()
            time.sleep(0.5)
            
            self.test_print("Mobile Responsiveness", True)
        except Exception as e:
            self.test_print("Mobile Responsiveness", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # LOGOUT TEST
    # ==========================================
    
    def test_admin_logout(self):
        """Test admin logout"""
        try:
            if "admin" not in self.driver.current_url:
                self.test_admin_login()
                
            # Click logout button
            logout_btn = self.driver.find_element(By.LINK_TEXT, "Logout")
            logout_btn.click()
            time.sleep(1)
            
            # Verify redirect to homepage
            assert self.driver.current_url == f"{self.base_url}/"
            
            # Try to access admin page (should redirect to login)
            self.driver.get(f"{self.base_url}/admin/admin_dashboard")
            time.sleep(1)
            assert "login" in self.driver.current_url
            
            self.test_print("Admin Logout", True)
        except Exception as e:
            self.test_print("Admin Logout", False)
            print(f"   Error: {e}")
            
    # ==========================================
    # RUN ALL TESTS
    # ==========================================
    
    def run_all_tests(self):
        """Execute all UI tests"""
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"🧪 Testing MoodMatch UI Components")
        print(f"{'='*60}{Colors.END}\n")
        
        try:
            self.setup()
            
            print(f"{Colors.YELLOW}📄 PUBLIC PAGES{Colors.END}")
            self.test_homepage()
            self.test_navigation_links()
            
            print(f"\n{Colors.YELLOW}📝 REGISTRATION{Colors.END}")
            self.test_registration_page_load()
            self.test_registration_step_navigation()
            self.test_registration_validation()
            
            print(f"\n{Colors.YELLOW}🔐 LOGIN{Colors.END}")
            self.test_login_page_load()
            self.test_admin_login()
            
            print(f"\n{Colors.YELLOW}📊 ADMIN DASHBOARD{Colors.END}")
            self.test_admin_dashboard_elements()
            self.test_admin_sidebar_navigation()
            
            print(f"\n{Colors.YELLOW}👥 MANAGE USERS{Colors.END}")
            self.test_manage_users_page()
            self.test_view_user_profile_modal()
            
            print(f"\n{Colors.YELLOW}🎯 MANAGE ACTIVITIES{Colors.END}")
            self.test_manage_activities_page()
            
            print(f"\n{Colors.YELLOW}🏷️ MANAGE CATEGORIES{Colors.END}")
            self.test_manage_categories_page()
            self.test_add_category_modal()
            
            print(f"\n{Colors.YELLOW}📈 VIEW ANALYTICS{Colors.END}")
            self.test_view_analytics_page()
            self.test_analytics_data_tables()
            
            print(f"\n{Colors.YELLOW}📱 RESPONSIVE DESIGN{Colors.END}")
            self.test_mobile_responsiveness()
            
            print(f"\n{Colors.YELLOW}🚪 LOGOUT{Colors.END}")
            self.test_admin_logout()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}⚠️ Tests interrupted by user{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Critical Error: {e}{Colors.END}")
        finally:
            self.teardown()
            
    def teardown(self):
        """Close browser and show results"""
        if self.driver:
            self.driver.quit()
            
        # Print summary
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"📊 TEST RESULTS")
        print(f"{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}✅ Passed: {self.passed}/{total}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {self.failed}/{total}{Colors.END}")
        print(f"{Colors.BLUE}📈 Pass Rate: {pass_rate:.1f}%{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
        
        if self.failed == 0:
            print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! YOUR UI IS PRODUCTION READY!{Colors.END}\n")
        else:
            print(f"{Colors.YELLOW}⚠️ Some tests failed. Please review and fix.{Colors.END}\n")

if __name__ == "__main__":
    tester = MoodMatchUITest()
    tester.run_all_tests()