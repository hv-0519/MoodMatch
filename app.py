from flask import Flask
from routes.main import main_bp
from routes.auth import auth_bp
# from routes.admin import admin_bp
# from routes.user import user_bp

app = Flask(__name__)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
# app.register_blueprint(admin_bp)
# app.register_blueprint(user_bp)

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