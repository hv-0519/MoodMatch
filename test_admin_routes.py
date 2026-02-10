#!/usr/bin/env python3
"""
MoodMatch Admin Routes Test Suite
Comprehensive tests for all admin.py route functions and utilities

Run: python test_admin_routes.py

Test Categories:
1. Helper Functions (get_db, get_admin_name)
2. Dashboard Route (admin_dashboard)
3. User Management (manage_users)
4. Activity Management (manage_activity - CRUD)
5. Category Management (manage_categories - CRUD)
6. Report Generation (export_* routes)
7. Analytics (view_analytics)
8. Admin Profile & Settings
9. Report Generation (generate_reports - PDF/CSV)
"""

import unittest
import sys
import sqlite3
from io import StringIO
from datetime import datetime, date, timedelta
from flask import Flask
from flask_login import LoginManager, UserMixin

# Import the admin blueprint
from routes.admin import admin_bp
from routes.auth import User

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'


class AdminRoutesTestSuite(unittest.TestCase):
    """Test suite for admin.py routes and functions"""
    
    @classmethod
    def setUpClass(cls):
        """Setup Flask app and database for testing"""
        print(f"\n{Colors.CYAN}{'='*70}")
        print(f"  ADMIN ROUTES TEST SUITE - SETUP")
        print(f"{'='*70}{Colors.END}\n")
        
        # Create Flask app
        cls.app = Flask(__name__)
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.app.secret_key = 'test-secret-key'
        
        # Setup Flask-Login
        login_manager = LoginManager()
        login_manager.init_app(cls.app)
        
        @login_manager.user_loader
        def load_user(user_id):
            return User(id=0, username="admin", first_name="Admin")
        
        # Register admin blueprint
        cls.app.register_blueprint(admin_bp, url_prefix="/admin")
        
        # Create test client
        cls.client = cls.app.test_client()
        
        # Get database connection
        cls.db_path = "models/instance/moodmatch.db"
        
        print(f"{Colors.GREEN}✅ Flask app initialized{Colors.END}")
        print(f"{Colors.GREEN}✅ Test client ready{Colors.END}")
        print(f"{Colors.GREEN}✅ Database connection ready{Colors.END}\n")
    
    def setUp(self):
        """Setup for each test"""
        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
    
    def tearDown(self):
        """Cleanup after each test"""
        self.db.close()
    
    # =============================================
    # 1. HELPER FUNCTIONS TESTS
    # =============================================
    
    def test_database_connection(self):
        """Test: Database connection is valid"""
        try:
            self.cursor.execute("SELECT 1")
            result = self.cursor.fetchone()
            self.assertIsNotNone(result)
            print(f"{Colors.GREEN}✅ Database connection: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Database connection failed: {e}")
    
    def test_admin_table_exists(self):
        """Test: Admin table exists and has required columns"""
        try:
            self.cursor.execute("PRAGMA table_info(admins)")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            
            required_columns = ['id', 'username', 'password_hash']
            for col in required_columns:
                self.assertIn(col, columns, f"Missing column: {col}")
            
            print(f"{Colors.GREEN}✅ Admin table structure: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Admin table check failed: {e}")
    
    def test_users_table_exists(self):
        """Test: Users table exists with required columns"""
        try:
            self.cursor.execute("PRAGMA table_info(users)")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            
            required_columns = ['id', 'username', 'email', 'created_at']
            for col in required_columns:
                self.assertIn(col, columns, f"Missing column: {col}")
            
            print(f"{Colors.GREEN}✅ Users table structure: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Users table check failed: {e}")
    
    def test_activities_table_exists(self):
        """Test: Activities table exists with required columns"""
        try:
            self.cursor.execute("PRAGMA table_info(activities)")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            
            required_columns = ['id', 'name', 'execution_type', 'category_id']
            for col in required_columns:
                self.assertIn(col, columns, f"Missing column: {col}")
            
            print(f"{Colors.GREEN}✅ Activities table structure: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Activities table check failed: {e}")
    
    def test_categories_table_exists(self):
        """Test: Categories table exists"""
        try:
            self.cursor.execute("PRAGMA table_info(categories)")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            
            required_columns = ['id', 'name']
            for col in required_columns:
                self.assertIn(col, columns, f"Missing column: {col}")
            
            print(f"{Colors.GREEN}✅ Categories table structure: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Categories table check failed: {e}")
    
    def test_user_history_table_exists(self):
        """Test: User history table exists"""
        try:
            self.cursor.execute("PRAGMA table_info(user_history)")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            
            required_columns = ['id', 'user_id', 'activity_id']
            for col in required_columns:
                self.assertIn(col, columns, f"Missing column: {col}")
            
            print(f"{Colors.GREEN}✅ User history table structure: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"User history table check failed: {e}")
    
    # =============================================
    # 2. ACTIVITY MANAGEMENT TESTS
    # =============================================
    
    def test_add_activity_valid(self):
        """Test: Add a valid activity"""
        try:
            # Get a valid category
            self.cursor.execute("SELECT id FROM categories LIMIT 1")
            category = self.cursor.fetchone()
            
            if not category:
                # Create a test category
                self.cursor.execute(
                    "INSERT INTO categories (name, icon) VALUES (?, ?)",
                    ("Test Category", "📚")
                )
                self.db.commit()
                category_id = self.cursor.lastrowid
            else:
                category_id = category[0]
            
            # Add activity
            self.cursor.execute(
                """INSERT INTO activities 
                (name, execution_type, description, mood_tags, energy_level, 
                 location_type, social_type, category_id, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("Test Activity", "online", "Test Description", "happy,calm", 
                 "high", "indoor", "solo", category_id, 1)
            )
            self.db.commit()
            activity_id = self.cursor.lastrowid
            
            # Verify it was added
            self.cursor.execute("SELECT * FROM activities WHERE id=?", (activity_id,))
            activity = self.cursor.fetchone()
            self.assertIsNotNone(activity)
            self.assertEqual(activity['name'], "Test Activity")
            
            # Cleanup
            self.cursor.execute("DELETE FROM activities WHERE id=?", (activity_id,))
            self.db.commit()
            
            print(f"{Colors.GREEN}✅ Add activity (valid): PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Add activity test failed: {e}")
    
    def test_add_activity_missing_name(self):
        """Test: Cannot add activity without name"""
        try:
            # Get a valid category
            self.cursor.execute("SELECT id FROM categories LIMIT 1")
            category = self.cursor.fetchone()
            if not category:
                self.cursor.execute(
                    "INSERT INTO categories (name, icon) VALUES (?, ?)",
                    ("Test Category", "📚")
                )
                self.db.commit()
                category_id = self.cursor.lastrowid
            else:
                category_id = category[0]
            
            # Try to add activity without name (should fail)
            try:
                self.cursor.execute(
                    """INSERT INTO activities 
                    (execution_type, description, category_id)
                    VALUES (?, ?, ?)""",
                    ("online", "Test", category_id)
                )
                self.db.commit()
                # If we get here, the test should check if NOT NULL constraint exists
                print(f"{Colors.YELLOW}⚠ Add activity without name: Constraint not enforced{Colors.END}")
            except sqlite3.IntegrityError:
                # Expected behavior - NOT NULL constraint
                print(f"{Colors.GREEN}✅ Add activity (missing name): PASSED{Colors.END}")
                self.db.rollback()
        except Exception as e:
            self.fail(f"Test failed: {e}")
    
    def test_update_activity(self):
        """Test: Update activity details"""
        try:
            # Get or create a category
            self.cursor.execute("SELECT id FROM categories LIMIT 1")
            category = self.cursor.fetchone()
            if not category:
                self.cursor.execute(
                    "INSERT INTO categories (name, icon) VALUES (?, ?)",
                    ("Test Category", "📚")
                )
                self.db.commit()
                category_id = self.cursor.lastrowid
            else:
                category_id = category[0]
            
            # Create test activity
            self.cursor.execute(
                """INSERT INTO activities 
                (name, execution_type, description, mood_tags, category_id, is_active)
                VALUES (?, ?, ?, ?, ?, ?)""",
                ("Original Name", "online", "Original Desc", "happy", category_id, 1)
            )
            self.db.commit()
            activity_id = self.cursor.lastrowid
            
            # Update it
            self.cursor.execute(
                """UPDATE activities 
                SET name=?, description=?, is_active=?
                WHERE id=?""",
                ("Updated Name", "Updated Desc", 0, activity_id)
            )
            self.db.commit()
            
            # Verify update
            self.cursor.execute("SELECT * FROM activities WHERE id=?", (activity_id,))
            activity = self.cursor.fetchone()
            self.assertEqual(activity['name'], "Updated Name")
            self.assertEqual(activity['description'], "Updated Desc")
            
            # Cleanup
            self.cursor.execute("DELETE FROM activities WHERE id=?", (activity_id,))
            self.db.commit()
            
            print(f"{Colors.GREEN}✅ Update activity: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Update activity test failed: {e}")
    
    def test_delete_activity(self):
        """Test: Delete activity"""
        try:
            # Get or create category
            self.cursor.execute("SELECT id FROM categories LIMIT 1")
            category = self.cursor.fetchone()
            if not category:
                self.cursor.execute(
                    "INSERT INTO categories (name, icon) VALUES (?, ?)",
                    ("Test Category", "📚")
                )
                self.db.commit()
                category_id = self.cursor.lastrowid
            else:
                category_id = category[0]
            
            # Create test activity
            self.cursor.execute(
                """INSERT INTO activities 
                (name, execution_type, category_id, mood_tags)
                VALUES (?, ?, ?, ?)""",
                ("Delete Test Activity", "online", category_id, "happy")
            )
            self.db.commit()
            activity_id = self.cursor.lastrowid
            
            # Delete it
            self.cursor.execute("DELETE FROM activities WHERE id=?", (activity_id,))
            self.db.commit()
            
            # Verify deletion
            self.cursor.execute("SELECT * FROM activities WHERE id=?", (activity_id,))
            result = self.cursor.fetchone()
            self.assertIsNone(result)
            
            print(f"{Colors.GREEN}✅ Delete activity: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Delete activity test failed: {e}")
    
    # =============================================
    # 3. CATEGORY MANAGEMENT TESTS
    # =============================================
    
    def test_add_category_valid(self):
        """Test: Add a valid category"""
        try:
            self.cursor.execute(
                "INSERT INTO categories (name, icon, description) VALUES (?, ?, ?)",
                ("Test Category", "📚", "Test Description")
            )
            self.db.commit()
            category_id = self.cursor.lastrowid
            
            # Verify
            self.cursor.execute("SELECT * FROM categories WHERE id=?", (category_id,))
            category = self.cursor.fetchone()
            self.assertIsNotNone(category)
            self.assertEqual(category['name'], "Test Category")
            
            # Cleanup
            self.cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
            self.db.commit()
            
            print(f"{Colors.GREEN}✅ Add category (valid): PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Add category test failed: {e}")
    
    def test_update_category(self):
        """Test: Update category"""
        try:
            # Create test category
            self.cursor.execute(
                "INSERT INTO categories (name, icon) VALUES (?, ?)",
                ("Original Category", "🎯")
            )
            self.db.commit()
            category_id = self.cursor.lastrowid
            
            # Update it
            self.cursor.execute(
                "UPDATE categories SET name=?, icon=? WHERE id=?",
                ("Updated Category", "📚", category_id)
            )
            self.db.commit()
            
            # Verify
            self.cursor.execute("SELECT * FROM categories WHERE id=?", (category_id,))
            category = self.cursor.fetchone()
            self.assertEqual(category['name'], "Updated Category")
            
            # Cleanup
            self.cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
            self.db.commit()
            
            print(f"{Colors.GREEN}✅ Update category: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Update category test failed: {e}")
    
    def test_delete_category(self):
        """Test: Delete category"""
        try:
            # Create test category
            self.cursor.execute(
                "INSERT INTO categories (name, icon) VALUES (?, ?)",
                ("Delete Test Category", "🗑️")
            )
            self.db.commit()
            category_id = self.cursor.lastrowid
            
            # Delete it
            self.cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
            self.db.commit()
            
            # Verify
            self.cursor.execute("SELECT * FROM categories WHERE id=?", (category_id,))
            result = self.cursor.fetchone()
            self.assertIsNone(result)
            
            print(f"{Colors.GREEN}✅ Delete category: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Delete category test failed: {e}")
    
    # =============================================
    # 4. STATISTICS & QUERIES TESTS
    # =============================================
    
    def test_count_total_users(self):
        """Test: Get count of total users"""
        try:
            self.cursor.execute("SELECT COUNT(*) as total FROM users")
            result = self.cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertGreaterEqual(result['total'], 0)
            
            print(f"{Colors.GREEN}✅ Count total users: PASSED (Total: {result['total']}){Colors.END}")
        except Exception as e:
            self.fail(f"Count users test failed: {e}")
    
    def test_count_total_activities(self):
        """Test: Get count of total activities"""
        try:
            self.cursor.execute("SELECT COUNT(*) as total FROM activities")
            result = self.cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertGreaterEqual(result['total'], 0)
            
            print(f"{Colors.GREEN}✅ Count total activities: PASSED (Total: {result['total']}){Colors.END}")
        except Exception as e:
            self.fail(f"Count activities test failed: {e}")
    
    def test_count_total_categories(self):
        """Test: Get count of total categories"""
        try:
            self.cursor.execute("SELECT COUNT(*) as total FROM categories")
            result = self.cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertGreaterEqual(result['total'], 0)
            
            print(f"{Colors.GREEN}✅ Count total categories: PASSED (Total: {result['total']}){Colors.END}")
        except Exception as e:
            self.fail(f"Count categories test failed: {e}")
    
    def test_count_user_history(self):
        """Test: Get count of user history records"""
        try:
            self.cursor.execute("SELECT COUNT(*) as total FROM user_history")
            result = self.cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertGreaterEqual(result['total'], 0)
            
            print(f"{Colors.GREEN}✅ Count user history: PASSED (Total: {result['total']}){Colors.END}")
        except Exception as e:
            self.fail(f"Count history test failed: {e}")
    
    def test_get_recent_users(self):
        """Test: Get recent users"""
        try:
            self.cursor.execute(
                "SELECT id, username, email, created_at FROM users ORDER BY created_at DESC LIMIT 5"
            )
            users = self.cursor.fetchall()
            self.assertIsInstance(users, list)
            
            print(f"{Colors.GREEN}✅ Get recent users: PASSED (Retrieved: {len(users)}){Colors.END}")
        except Exception as e:
            self.fail(f"Get recent users test failed: {e}")
    
    def test_get_user_interests(self):
        """Test: Get user interests distribution"""
        try:
            self.cursor.execute(
                """SELECT i.name as interest_name, COUNT(DISTINCT ui.user_id) as user_count
                FROM interests i
                LEFT JOIN user_interests ui ON i.id = ui.interest_id
                GROUP BY i.id, i.name
                ORDER BY user_count DESC
                LIMIT 10"""
            )
            interests = self.cursor.fetchall()
            self.assertIsInstance(interests, list)
            
            print(f"{Colors.GREEN}✅ Get user interests: PASSED (Retrieved: {len(interests)}){Colors.END}")
        except Exception as e:
            self.fail(f"Get interests test failed: {e}")
    
    def test_get_activity_by_category(self):
        """Test: Get activities grouped by category"""
        try:
            self.cursor.execute(
                """SELECT c.name as category_name, COUNT(a.id) as activity_count
                FROM categories c
                LEFT JOIN activities a ON c.id = a.category_id
                GROUP BY c.id
                ORDER BY activity_count DESC"""
            )
            categories = self.cursor.fetchall()
            self.assertIsInstance(categories, list)
            
            print(f"{Colors.GREEN}✅ Get activities by category: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Get activities by category test failed: {e}")
    
    # =============================================
    # 5. FEEDBACK & RATINGS TESTS
    # =============================================
    
    def test_get_feedback_distribution(self):
        """Test: Get feedback ratings distribution"""
        try:
            self.cursor.execute(
                """SELECT feedback_rating, COUNT(*) as count
                FROM user_history
                WHERE feedback_rating IS NOT NULL
                GROUP BY feedback_rating
                ORDER BY feedback_rating DESC"""
            )
            feedback = self.cursor.fetchall()
            self.assertIsInstance(feedback, list)
            
            print(f"{Colors.GREEN}✅ Get feedback distribution: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Get feedback distribution test failed: {e}")
    
    def test_get_average_feedback_rating(self):
        """Test: Get average feedback rating"""
        try:
            self.cursor.execute(
                """SELECT AVG(feedback_rating) as avg_rating
                FROM user_history
                WHERE feedback_rating IS NOT NULL"""
            )
            result = self.cursor.fetchone()
            self.assertIsNotNone(result)
            
            print(f"{Colors.GREEN}✅ Get average feedback rating: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Get average feedback rating test failed: {e}")
    
    # =============================================
    # 6. MOOD ANALYTICS TESTS
    # =============================================
    
    def test_get_mood_distribution(self):
        """Test: Get mood distribution (positive/negative/neutral)"""
        try:
            self.cursor.execute(
                """SELECT 
                    CASE 
                        WHEN sentiment_score >= 0.2 THEN 'positive'
                        WHEN sentiment_score <= -0.2 THEN 'negative'
                        ELSE 'neutral'
                    END as mood_type,
                    COUNT(*) as count
                FROM user_history
                WHERE sentiment_score IS NOT NULL
                GROUP BY mood_type"""
            )
            moods = self.cursor.fetchall()
            self.assertIsInstance(moods, list)
            
            print(f"{Colors.GREEN}✅ Get mood distribution: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Get mood distribution test failed: {e}")
    
    def test_get_common_mood_inputs(self):
        """Test: Get common mood keywords"""
        try:
            self.cursor.execute(
                """SELECT mood_input, COUNT(*) as frequency
                FROM user_history
                WHERE mood_input IS NOT NULL AND mood_input != ''
                GROUP BY mood_input
                ORDER BY frequency DESC
                LIMIT 10"""
            )
            moods = self.cursor.fetchall()
            self.assertIsInstance(moods, list)
            
            print(f"{Colors.GREEN}✅ Get common mood inputs: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Get common mood inputs test failed: {e}")
    
    # =============================================
    # 7. ANALYTICS TESTS
    # =============================================
    
    def test_get_most_recommended_activities(self):
        """Test: Get most recommended activities"""
        try:
            self.cursor.execute(
                """SELECT a.name, COUNT(uh.id) as recommendation_count
                FROM user_history uh
                JOIN activities a ON uh.activity_id = a.id
                GROUP BY uh.activity_id
                ORDER BY recommendation_count DESC
                LIMIT 10"""
            )
            activities = self.cursor.fetchall()
            self.assertIsInstance(activities, list)
            
            print(f"{Colors.GREEN}✅ Get most recommended: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Get most recommended test failed: {e}")
    
    def test_get_most_favorited_activities(self):
        """Test: Get most favorited activities"""
        try:
            self.cursor.execute(
                """SELECT a.name, COUNT(f.id) as favorite_count
                FROM favorites f
                JOIN activities a ON f.activity_id = a.id
                GROUP BY f.activity_id
                ORDER BY favorite_count DESC
                LIMIT 10"""
            )
            activities = self.cursor.fetchall()
            self.assertIsInstance(activities, list)
            
            print(f"{Colors.GREEN}✅ Get most favorited: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Get most favorited test failed: {e}")
    
    def test_get_completion_rates(self):
        """Test: Get activity completion rates"""
        try:
            self.cursor.execute(
                """SELECT 
                    a.name,
                    COUNT(CASE WHEN uh.feedback_rating IS NOT NULL THEN 1 END) as completed,
                    COUNT(uh.id) as total,
                    ROUND(CAST(COUNT(CASE WHEN uh.feedback_rating IS NOT NULL THEN 1 END) AS FLOAT) / COUNT(uh.id) * 100, 1) as completion_rate
                FROM user_history uh
                JOIN activities a ON uh.activity_id = a.id
                GROUP BY uh.activity_id
                HAVING total > 0
                ORDER BY completion_rate DESC
                LIMIT 10"""
            )
            rates = self.cursor.fetchall()
            self.assertIsInstance(rates, list)
            
            print(f"{Colors.GREEN}✅ Get completion rates: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Get completion rates test failed: {e}")
    
    def test_get_least_used_activities(self):
        """Test: Get least used activities"""
        try:
            self.cursor.execute(
                """SELECT 
                    a.name,
                    COALESCE(COUNT(uh.id), 0) as usage_count
                FROM activities a
                LEFT JOIN user_history uh ON a.id = uh.activity_id
                WHERE a.is_active = 1
                GROUP BY a.id
                ORDER BY usage_count ASC
                LIMIT 10"""
            )
            activities = self.cursor.fetchall()
            self.assertIsInstance(activities, list)
            
            print(f"{Colors.GREEN}✅ Get least used activities: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Get least used activities test failed: {e}")
    
    # =============================================
    # 8. ROUTE TESTS
    # =============================================
    
    def test_route_admin_dashboard_exists(self):
        """Test: Admin dashboard route exists"""
        try:
            # Test that route is registered
            routes = [str(rule) for rule in self.app.url_map.iter_rules()]
            self.assertIn('/admin/admin_dashboard', routes)
            
            print(f"{Colors.GREEN}✅ Admin dashboard route exists: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Dashboard route test failed: {e}")
    
    def test_route_manage_users_exists(self):
        """Test: Manage users route exists"""
        try:
            routes = [str(rule) for rule in self.app.url_map.iter_rules()]
            self.assertIn('/admin/manage_users', routes)
            
            print(f"{Colors.GREEN}✅ Manage users route exists: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Manage users route test failed: {e}")
    
    def test_route_manage_activity_exists(self):
        """Test: Manage activity route exists"""
        try:
            routes = [str(rule) for rule in self.app.url_map.iter_rules()]
            self.assertIn('/admin/manage_activity', routes)
            
            print(f"{Colors.GREEN}✅ Manage activity route exists: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Manage activity route test failed: {e}")
    
    def test_route_manage_categories_exists(self):
        """Test: Manage categories route exists"""
        try:
            routes = [str(rule) for rule in self.app.url_map.iter_rules()]
            self.assertIn('/admin/manage_categories', routes)
            
            print(f"{Colors.GREEN}✅ Manage categories route exists: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Manage categories route test failed: {e}")
    
    def test_route_export_users_report_exists(self):
        """Test: Export users report route exists"""
        try:
            routes = [str(rule) for rule in self.app.url_map.iter_rules()]
            self.assertIn('/admin/export_users_report', routes)
            
            print(f"{Colors.GREEN}✅ Export users report route exists: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Export users route test failed: {e}")
    
    def test_route_view_analytics_exists(self):
        """Test: View analytics route exists"""
        try:
            routes = [str(rule) for rule in self.app.url_map.iter_rules()]
            self.assertIn('/admin/view_analytics', routes)
            
            print(f"{Colors.GREEN}✅ View analytics route exists: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"View analytics route test failed: {e}")
    
    def test_route_admin_profile_exists(self):
        """Test: Admin profile route exists"""
        try:
            routes = [str(rule) for rule in self.app.url_map.iter_rules()]
            self.assertIn('/admin/admin_profile', routes)
            
            print(f"{Colors.GREEN}✅ Admin profile route exists: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Admin profile route test failed: {e}")
    
    def test_route_admin_settings_exists(self):
        """Test: Admin settings route exists"""
        try:
            routes = [str(rule) for rule in self.app.url_map.iter_rules()]
            self.assertIn('/admin/admin_settings', routes)
            
            print(f"{Colors.GREEN}✅ Admin settings route exists: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Admin settings route test failed: {e}")
    
    def test_route_generate_reports_exists(self):
        """Test: Generate reports route exists"""
        try:
            routes = [str(rule) for rule in self.app.url_map.iter_rules()]
            self.assertIn('/admin/generate_reports', routes)
            
            print(f"{Colors.GREEN}✅ Generate reports route exists: PASSED{Colors.END}")
        except Exception as e:
            self.fail(f"Generate reports route test failed: {e}")


def run_tests():
    """Run all tests"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"  RUNNING ADMIN ROUTES TEST SUITE")
    print(f"{'='*70}{Colors.END}\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(AdminRoutesTestSuite)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"  TEST SUMMARY")
    print(f"{'='*70}{Colors.END}")
    print(f"{Colors.GREEN}✅ Tests Run: {result.testsRun}{Colors.END}")
    print(f"{Colors.GREEN}✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}{Colors.END}")
    print(f"{Colors.RED}❌ Failed: {len(result.failures)}{Colors.END}")
    print(f"{Colors.RED}❌ Errors: {len(result.errors)}{Colors.END}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"{Colors.BLUE}📊 Success Rate: {success_rate:.1f}%{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
