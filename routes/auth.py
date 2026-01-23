import os
import random
import string
import sqlite3
from flask import request, redirect, url_for, render_template, Blueprint, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    UserMixin,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from utils.helper import generate_username, send_email

auth_bp = Blueprint("auth", __name__)


# ---------------------------
# BLOCK LOGIN / REGISTER FOR LOGGED-IN USERS (FIXED)
# ---------------------------
@auth_bp.before_request
def block_auth_pages_for_logged_in_users():
    if current_user.is_authenticated:
        if request.endpoint == "auth.login":
            # Logged-in users should NOT see login again
            return redirect(url_for("main.index"))
        if request.endpoint == "auth.register":
            return redirect(url_for("main.index"))


# ---------------------------
# USER MODEL (IMPROVED)
# ---------------------------
class User(UserMixin):
    def __init__(
        self,
        id,
        username,
        first_name=None,
        profile_picture=None,
        is_admin=False,
    ):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.profile_picture = profile_picture
        self.is_admin = is_admin


# ---------------------------
# REGISTER
# ---------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone")
        gender = request.form.get("gender")
        date_of_birth = request.form.get("date_of_birth")
        street_address = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")
        postal_code = request.form.get("postal_code")
        country = request.form.get("country")

        file = request.files.get("profile_picture")
        profile_picture = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join("static", "uploads")
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, filename))
            profile_picture = filename

        username = generate_username(first_name, last_name)
        password_hash = generate_password_hash(request.form.get("password"))

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (
                first_name, last_name, username, email,
                phone_number, gender, date_of_birth,
                street_address, city, state,
                postal_code, country, profile_picture,
                password_hash
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                first_name,
                last_name,
                username,
                email,
                phone_number,
                gender,
                date_of_birth,
                street_address,
                city,
                state,
                postal_code,
                country,
                profile_picture,
                password_hash,
            ),
        )
        conn.commit()
        conn.close()

        send_email(
            to_email=email,
            subject="Welcome to MoodMatch",
            body=f"Hello {first_name},\n\nUsername: {username}",
        )

        return redirect(url_for("auth.login"))

    return render_template("auth/registration.html")


# ---------------------------
# LOGIN (FIXED)
# ---------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # ✅ FIX: checkbox handling
        remember = True if request.form.get("remember") == "on" else False

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()

        # ---------------------------
        # ADMIN LOGIN
        # ---------------------------
        cursor.execute(
            "SELECT id, username, password_hash FROM admins WHERE username = ?",
            (username,),
        )
        admin = cursor.fetchone()

        if admin and check_password_hash(admin[2], password):
            login_user(
                User(
                    id=admin[0],
                    username=admin[1],
                    first_name="Admin",
                    is_admin=True,
                ),
                remember=remember,
            )
            conn.close()
            return redirect(url_for("admin.admin_dashboard"))

        # ---------------------------
        # USER LOGIN
        # ---------------------------
        cursor.execute(
            """
            SELECT id, username, first_name, profile_picture, password_hash
            FROM users
            WHERE username = ?
            """,
            (username,),
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[4], password):
            login_user(
                User(
                    id=user[0],
                    username=user[1],
                    first_name=user[2],
                    profile_picture=user[3],
                    is_admin=False,
                ),
                remember=remember,
            )
            return redirect(url_for("user.user_dashboard"))

        return render_template("auth/login.html", error="Invalid credentials")

    return render_template("auth/login.html")


# ---------------------------
# LOGOUT (CORRECT)
# ---------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("main.index"))


# ---------------------------
# FORGET PASSWORD
# ---------------------------
@auth_bp.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND email = ?",
            (username, email),
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return render_template(
                "auth/forget_password.html",
                error="Invalid username or email",
            )

        reset_code = "".join(random.choices(string.digits, k=6))

        cursor.execute(
            "UPDATE users SET reset_code = ? WHERE username = ?",
            (reset_code, username),
        )
        conn.commit()
        conn.close()

        send_email(
            to_email=email,
            subject="Password Reset Code",
            body=f"Your reset code is: {reset_code}",
        )

        return redirect(url_for("auth.verify_code", username=username))

    return render_template("auth/forget_password.html")


# ---------------------------
# VERIFY CODE
# ---------------------------
@auth_bp.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    username = request.args.get("username")

    if request.method == "POST":
        username = request.form.get("username")
        code = request.form.get("reset_code")

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT reset_code FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row or row[0] != code:
            return render_template(
                "auth/verify_reset_code.html",
                error="Invalid code",
                username=username,
            )

        return redirect(url_for("auth.reset_password", username=username))

    return render_template("auth/verify_reset_code.html", username=username)


# ---------------------------
# RESET PASSWORD
# ---------------------------
@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    username = request.args.get("username")

    if request.method == "POST":
        username = request.form.get("username")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            return render_template(
                "auth/reset_password.html",
                error="Passwords do not match",
                username=username,
            )

        password_hash = generate_password_hash(new_password)

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET password_hash = ?, reset_code = NULL
            WHERE username = ?
            """,
            (password_hash, username),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", username=username)
