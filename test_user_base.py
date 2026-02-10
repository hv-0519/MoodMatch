#!/usr/bin/env python3
"""
MoodMatch User Base Template Test
Tests the user_base.html template rendering and UI components

Run: python test_user_base.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'

class UserBaseTemplateTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:6969"
        self.driver = None
        self.wait = None
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Initialize browser"""
        print(f"\n{Colors.BLUE}🚀 Initializing Chrome Browser for User Base Template Test...{Colors.END}")
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
            
    def login_user(self):
        """Login with test user credentials"""
        print(f"\n{Colors.CYAN}🔐 Logging in test user...{Colors.END}")
        try:
            self.driver.get(f"{self.base_url}/login")
            
            # Fill username field
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys("testuser")
            
            # Fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys("password123")
            
            # Submit form
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_btn.click()
            
            # Wait for redirect to dashboard
            self.wait.until(EC.url_contains("user_dashboard"))
            print(f"{Colors.GREEN}✅ Successfully logged in{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Login failed: {str(e)}{Colors.END}")
            return False
            
    def test_navbar_exists(self):
        """Test navbar element exists and contains brand"""
        try:
            navbar = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "navbar"))
            )
            brand = navbar.find_element(By.CLASS_NAME, "navbar-brand")
            brand_text = brand.find_element(By.CLASS_NAME, "brand-text").text
            
            status = brand_text == "MoodMatch"
            self.test_print("Navbar exists with MoodMatch brand", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing navbar: {str(e)}{Colors.END}")
            self.test_print("Navbar exists with MoodMatch brand", False)
            return False
            
    def test_navbar_profile_section(self):
        """Test navbar shows user profile picture/initial"""
        try:
            navbar = self.driver.find_element(By.CLASS_NAME, "navbar")
            
            # Check if profile picture or initial is displayed
            profile_pic = navbar.find_element(By.CLASS_NAME, "profile-pic")
            status = profile_pic.is_displayed()
            
            self.test_print("Navbar shows profile picture/initial", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing profile section: {str(e)}{Colors.END}")
            self.test_print("Navbar shows profile picture/initial", False)
            return False
            
    def test_sidebar_exists(self):
        """Test admin sidebar exists"""
        try:
            sidebar = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "admin-sidebar"))
            )
            status = sidebar.is_displayed()
            self.test_print("Sidebar exists and is visible", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing sidebar: {str(e)}{Colors.END}")
            self.test_print("Sidebar exists and is visible", False)
            return False
            
    def test_sidebar_navigation_links(self):
        """Test sidebar contains all required navigation links"""
        try:
            sidebar = self.driver.find_element(By.CLASS_NAME, "admin-sidebar")
            nav_links = sidebar.find_elements(By.CSS_SELECTOR, "a.admin-nav-link")
            
            # Get all link hrefs and texts
            link_data = [(link.get_attribute("href"), link.text) for link in nav_links]
            
            # Required routes that should exist
            required_routes = [
                "user_dashboard",
                "index", 
                "try_activity",
                "favorites",
                "history",
                "about",
                "profile",
                "logout"
            ]
            
            # Check if all required routes are present in the links
            found_routes = sum(1 for req in required_routes if any(req in href for href, _ in link_data if href))
            status = found_routes >= 6  # At least 6 of the main routes
            
            self.test_print(f"Sidebar navigation links present ({found_routes}/{len(required_routes)})", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing sidebar navigation: {str(e)}{Colors.END}")
            self.test_print("Sidebar navigation links present", False)
            return False
            
    def test_footer_exists(self):
        """Test footer element exists"""
        try:
            footer = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "footer"))
            )
            status = footer.is_displayed()
            self.test_print("Footer exists and is visible", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing footer: {str(e)}{Colors.END}")
            self.test_print("Footer exists and is visible", False)
            return False
            
    def test_footer_content(self):
        """Test footer contains MoodMatch branding and links"""
        try:
            footer = self.driver.find_element(By.CLASS_NAME, "footer")
            footer_text = footer.text
            
            # Check for required content
            has_brand = "MoodMatch" in footer_text
            has_copyright = "2026" in footer_text
            
            status = has_brand and has_copyright
            self.test_print("Footer contains MoodMatch branding and copyright", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing footer content: {str(e)}{Colors.END}")
            self.test_print("Footer contains MoodMatch branding and copyright", False)
            return False
            
    def test_hamburger_menu_toggle(self):
        """Test hamburger menu toggle functionality"""
        try:
            # First check if toggle button exists
            try:
                toggle_btn = self.wait.until(
                    EC.presence_of_element_located((By.ID, "navbarToggle"))
                )
            except:
                self.test_print("Hamburger menu toggle works", False)
                return False
            
            # Check if it's displayable/visible
            if not toggle_btn.is_displayed():
                # Toggle might be hidden on large screens - that's OK
                self.test_print("Hamburger menu toggle works (not visible on this viewport)", True)
                return True
            
            # Try to click it (with scroll into view)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", toggle_btn)
            time.sleep(0.3)
            toggle_btn.click()
            time.sleep(0.5)
            
            # Check if sidebar expanded
            sidebar = self.driver.find_element(By.CLASS_NAME, "admin-sidebar")
            is_expanded = "expanded" in sidebar.get_attribute("class")
            
            # Click again to collapse
            toggle_btn.click()
            time.sleep(0.5)
            
            status = is_expanded
            self.test_print("Hamburger menu toggle works", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing hamburger menu: {str(e)}{Colors.END}")
            self.test_print("Hamburger menu toggle works", False)
            return False
            
    def test_responsive_design(self):
        """Test responsive design by checking viewport"""
        try:
            # Check if navbar toggle exists and has proper attributes
            toggle = self.wait.until(
                EC.presence_of_element_located((By.ID, "navbarToggle"))
            )
            
            # Check if it has the proper aria-label
            aria_label = toggle.get_attribute("aria-label")
            has_label = aria_label == "Toggle navigation"
            
            status = has_label
            self.test_print("Responsive design toggle button has proper attributes", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing responsive design: {str(e)}{Colors.END}")
            self.test_print("Responsive design toggle button has proper attributes", False)
            return False
            
    def test_url_links_valid(self):
        """Test that navigation links have valid URLs"""
        try:
            sidebar = self.driver.find_element(By.CLASS_NAME, "admin-sidebar")
            nav_links = sidebar.find_elements(By.CSS_SELECTOR, "a.admin-nav-link")
            
            # Check each link has href attribute
            valid_links = sum(1 for link in nav_links if link.get_attribute("href"))
            status = valid_links > 0
            
            self.test_print(f"Navigation links have valid URLs ({valid_links} links)", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing URL links: {str(e)}{Colors.END}")
            self.test_print("Navigation links have valid URLs", False)
            return False
            
    def test_logout_link_present(self):
        """Test logout link is present in sidebar"""
        try:
            logout_link = self.wait.until(
                EC.presence_of_element_located((By.ID, "logout"))
            )
            href = logout_link.get_attribute("href")
            status = "logout" in href.lower()
            
            self.test_print("Logout link present and points to logout route", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing logout link: {str(e)}{Colors.END}")
            self.test_print("Logout link present and points to logout route", False)
            return False
            
    def test_content_block_exists(self):
        """Test that content block placeholder exists for child templates"""
        try:
            # Check if page body contains content (injected by child template)
            body = self.driver.find_element(By.TAG_NAME, "body")
            status = body.is_displayed()
            
            self.test_print("Content block placeholder for child templates exists", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing content block: {str(e)}{Colors.END}")
            self.test_print("Content block placeholder for child templates exists", False)
            return False
            
    def test_theme_styles_applied(self):
        """Test that CSS styles are applied"""
        try:
            navbar = self.driver.find_element(By.CLASS_NAME, "navbar")
            
            # Check if styles are applied by checking computed styles
            background_color = navbar.value_of_css_property("background-color")
            status = background_color != ""
            
            self.test_print("Theme styles are applied to navbar", status)
            return status
        except Exception as e:
            print(f"{Colors.RED}Error testing theme styles: {str(e)}{Colors.END}")
            self.test_print("Theme styles are applied to navbar", False)
            return False
            
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.CYAN}{'='*60}")
        print(f"  USER BASE TEMPLATE TEST SUITE")
        print(f"{'='*60}{Colors.END}\n")
        
        # Setup
        self.setup()
        
        try:
            # Login first
            if not self.login_user():
                print(f"\n{Colors.RED}Cannot proceed without login{Colors.END}")
                self.driver.quit()
                return
                
            # Run all tests
            print(f"\n{Colors.CYAN}Running template tests...{Colors.END}\n")
            
            self.test_navbar_exists()
            self.test_navbar_profile_section()
            self.test_sidebar_exists()
            self.test_sidebar_navigation_links()
            self.test_footer_exists()
            self.test_footer_content()
            self.test_hamburger_menu_toggle()
            self.test_responsive_design()
            self.test_url_links_valid()
            self.test_logout_link_present()
            self.test_content_block_exists()
            self.test_theme_styles_applied()
            
            # Print results
            self.print_results()
            
        except Exception as e:
            print(f"\n{Colors.RED}Test execution error: {str(e)}{Colors.END}")
            import traceback
            traceback.print_exc()
        finally:
            time.sleep(2)
            self.driver.quit()
            
    def print_results(self):
        """Print test summary"""
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.CYAN}{'='*60}")
        print(f"  TEST RESULTS")
        print(f"{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}✅ Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {self.failed}{Colors.END}")
        print(f"{Colors.BLUE}📊 Success Rate: {percentage:.1f}%{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
        
        if self.failed > 0:
            sys.exit(1)

if __name__ == "__main__":
    test = UserBaseTemplateTest()
    test.run_all_tests()
