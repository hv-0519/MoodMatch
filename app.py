from flask import Flask
from flask_login import LoginManager
import sqlite3
from datetime import timedelta

from routes.main import main_bp
from routes.auth import auth_bp, User  # 👈 import User class
from routes.admin import admin_bp
from routes.user import user_bp
from routes.activities import activities_bp  # 👈 import activities blueprint


app = Flask(__name__)

# 🔒 REQUIRED for Flask-Login
app.secret_key = "moodmatch-secret-key"

# ✅ ADDED: Session configuration for proper logout behavior
app.config["SESSION_COOKIE_NAME"] = "moodmatch_session"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    days=7
)  # Session expires after 7 days
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production with HTTPS

# ===============================
# Flask-Login setup
# ===============================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.session_protection = "strong"  # ✅ ADDED: Stronger session protection


@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)  # safety

    # Special case for hardcoded super admin
    if user_id == 0:
        return User(id=0, username="admin", first_name="Admin")

    # Normal users from 'users' table
    conn = sqlite3.connect("models/mood.db")
    cursor = conn.cursor()

    # Query with correct column order
    cursor.execute(
        "SELECT id, username, first_name, profile_picture FROM users WHERE id = ?",
        (user_id,),
    )
    row = cursor.fetchone()

    # Also check admins table (optional but recommended)
    if not row:
        cursor.execute(
            "SELECT id, username, NULL as first_name, NULL as profile_picture FROM admins WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()

    conn.close()

    if row:
        # Create User with correct parameter order
        # User(id, username, first_name, profile_picture)
        return User(
            id=row[0],  # id
            username=row[1],  # username
            first_name=row[2],  # first_name (can be None for admins)
            profile_picture=row[3],  # profile_picture (can be None)
        )

    return None


# ===============================
# Register Blueprints
# ===============================
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(activities_bp)  # 👈 activities blueprint (has url_prefix in blueprint)


# ===============================
# Run App
# ===============================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MoodMatch Application Starting...")
    print("=" * 60)
    print("📊 Environment: development")
    print("🔧 Debug Mode: True")
    print("=" * 60)
    print("🌐 Access the app at: http://127.0.0.1:6969")
    print("=" * 60)
    print("\n💡 TIP: To clear session, visit /logout or clear browser cookies")
    print("=" * 60)

    app.run(debug=True, port=6969)
