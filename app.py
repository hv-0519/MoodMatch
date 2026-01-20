from flask import Flask
from flask_login import LoginManager
import sqlite3

from routes.main import main_bp
from routes.auth import auth_bp, User  # 👈 import User class

app = Flask(__name__)

# 🔑 REQUIRED for Flask-Login
app.secret_key = "moodmatch-secret-key"

# ===============================
# Flask-Login setup
# ===============================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("models/mood.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, profile_picture FROM users WHERE id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return User(
            row[0],
            row[1],
            row[2],
        )
    return None


# ===============================
# Register Blueprints
# ===============================
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
# app.register_blueprint(admin_bp)
# app.register_blueprint(user_bp)


# ===============================
# Run App
# ===============================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MoodMatch Application Starting...")
    print("=" * 60)
    print("📊 Environment: development")
    print("🔑 Debug Mode: True")
    print("=" * 60)
    print("🌐 Access the app at: http://127.0.0.1:6969")
    print("=" * 60)

    app.run(debug=True, port=6969)
