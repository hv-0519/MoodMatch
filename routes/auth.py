import os
import random
import string
import sqlite3
from flask import request, redirect, url_for, render_template, Blueprint, session, flash
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


# Helper to get database connection
def get_db_connection():
    db_path = os.path.join("models", "instance", "moodmatch.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@auth_bp.before_request
def block_auth_pages_for_logged_in_users():
    if current_user.is_authenticated:
        if request.endpoint in ["auth.login", "auth.register"]:
            return redirect(url_for("main.index"))


class User(UserMixin):
    def __init__(
        self, id, username, first_name=None, profile_picture=None, is_admin=False
    ):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.profile_picture = profile_picture
        self.is_admin = is_admin



# ---------------------------
# REGISTER (FIXED - CORRECT FIELD NAMES + FILE UPLOAD)
# ---------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 1. Capture Form Data
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone")  # Matches HTML 'name="phone"'
        gender = request.form.get("gender")
        date_of_birth = request.form.get("date_of_birth")
        street_address = request.form.get("street")  # Matches HTML 'name="street"'
        city = request.form.get("city")
        state = request.form.get("state")
        postal_code = request.form.get("postal_code")
        country = request.form.get("country")
        password = request.form.get("password")
        selected_interests = request.form.getlist("interests")

        # 2. Handle Profile Picture Upload
        file = request.files.get("profile_picture")
        profile_picture = "default.png"

        if file and file.filename != "":
            filename = secure_filename(f"{email}_{file.filename}")
            upload_path = os.path.join("static", "uploads")
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, filename))
            profile_picture = filename

        # 3. Security and Identity
        username = generate_username(first_name, last_name)
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert User
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

            new_user_id = cursor.lastrowid

            # 4. Save Interests (FIXED LOOP)
            interests_saved = 0
            for interest_name in selected_interests:
                # Find ID for this interest name
                cursor.execute(
                    "SELECT id FROM interests WHERE LOWER(name) = LOWER(?)",
                    (interest_name,),
                )
                row = cursor.fetchone()

                if row:
                    cursor.execute(
                        "INSERT INTO user_interests (user_id, interest_id) VALUES (?, ?)",
                        (new_user_id, row["id"]),
                    )
                    interests_saved += 1
                    print(f"✅ Saved interest: {interest_name}")
                else:
                    print(f"⚠️ Interest not found in DB: {interest_name}")

            conn.commit()
            print(
                f"✅ Registration complete. User ID: {new_user_id}, Interests: {interests_saved}"
            )

            # 5. Send Welcome Email
            try:
                send_email(
                    to_email=email,
                    subject="Welcome to MoodMatch 🎉",
                    body=f" Hello {first_name},\n\nWelcome to MoodMatch! Your account has been successfully created with the username: {username}.\n\nWe're excited to have you on board and can't wait for you to explore all the features we offer. If you have any questions or need assistance, feel free to reach out to our support team.\n\nHappy matching!\n\n— Team MoodMatch",
                )
            except Exception as e:
                print(f"⚠️ Email failed: {e}")

            flash(f"Account created! Your username is {username}", "success")
            return redirect(url_for("auth.login"))

        except sqlite3.Error as e:
            conn.rollback()
            print(f"❌ DATABASE ERROR: {e}")
            flash("Database error: Could not complete registration.", "danger")
        finally:
            conn.close()

    return render_template("auth/registration.html")


# ---------------------------
# LOGIN (UNCHANGED)
# ---------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember") == "on"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 1. Check the Admins Table first
            cursor.execute(
                "SELECT id, username, password_hash FROM admins WHERE username = ?",
                (username,),
            )
            admin_row = cursor.fetchone()

            if admin_row and check_password_hash(admin_row["password_hash"], password):
                admin_obj = User(
                    id=admin_row["id"],
                    username=admin_row["username"],
                    first_name="Admin",
                    is_admin=True  # Explicitly set to True
                )
                login_user(admin_obj, remember=remember)
                return redirect(url_for("admin.admin_dashboard"))

            # 2. Check the Users Table if not found in Admins
            cursor.execute(
                "SELECT id, username, first_name, profile_picture, password_hash FROM users WHERE username = ?",
                (username,),
            )
            user_row = cursor.fetchone()

            if user_row and check_password_hash(user_row["password_hash"], password):
                user_obj = User(
                    id=user_row["id"],
                    username=user_row["username"],
                    first_name=user_row["first_name"],
                    profile_picture=user_row["profile_picture"],
                    is_admin=False  # Explicitly set to False
                )
                login_user(user_obj, remember=remember)
                return redirect(url_for("user.user_dashboard"))

            # If neither match
            flash("Invalid username or password", "danger")

        except Exception as e:
            print(f"Login error: {e}")
            flash("An error occurred during login.", "danger")
        finally:
            conn.close()

    return render_template("auth/login.html")


# ---------------------------
# LOGOUT (UNCHANGED)
# ---------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("main.index"))


# ---------------------------
# FORGET PASSWORD (UNCHANGED)
# ---------------------------
@auth_bp.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")

        conn = sqlite3.connect("models/instance/moodmatch.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, first_name FROM users WHERE username = ? AND email = ?",
            (username, email),
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return render_template(
                "auth/forget_password.html",
                error="Invalid username or email",
            )

        user_id, first_name = row

        reset_code = "".join(random.choices(string.digits, k=6))

        cursor.execute(
            "UPDATE users SET reset_code = ? WHERE id = ?",
            (reset_code, user_id),
        )
        conn.commit()
        conn.close()

        print("EMAIL BODY:\n", f"Code is {reset_code}")
        send_email(
            to_email=email,
            subject="Your MoodMatch Password Reset Code",
            body=f"""Hello {first_name or "there"},

We received a request to reset the password for your MoodMatch account ✨

To continue, please use the verification code below:

🔐 Password Reset Code: {reset_code}

Enter this code in the app to securely reset your password.
For your safety, please do not share this code with anyone — even if they claim to be from MoodMatch.

If you didn't request a password reset, you can safely ignore this email. Your account remains protected.

Thanks for being part of MoodMatch 💙
— Team MoodMatch
""",
        )

        return redirect(url_for("auth.verify_code", username=username))

    return render_template("auth/forget_password.html")


# ---------------------------
# VERIFY CODE (UNCHANGED)
# ---------------------------
@auth_bp.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    username = request.args.get("username")

    if request.method == "POST":
        username = request.form.get("username")
        code = request.form.get("reset_code")

        conn = sqlite3.connect("models/instance/moodmatch.db")
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
# RESET PASSWORD (UNCHANGED)
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

        conn = sqlite3.connect("models/instance/moodmatch.db")
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
