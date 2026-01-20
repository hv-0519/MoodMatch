import os
import random
import string
import sqlite3
from flask import request, redirect, url_for, render_template, Blueprint
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from utils.helper import generate_username, send_email

auth_bp = Blueprint("auth", __name__)


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

        # PROFILE PICTURE
        file = request.files.get("profile_picture")
        profile_picture = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join("static", "uploads")
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, filename))
            profile_picture = filename

        # GENERATE USERNAME BEFORE INSERT
        username = generate_username(first_name, last_name)
        password_hash = generate_password_hash(request.form.get("password"))

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (
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

        # SEND USERNAME EMAIL
        if email:
            send_email(
                to_email=email,
                subject="Welcome To MoodMatch!!!",
                body=f"""Hello {first_name},

We’re glad that you’ve registered with MoodMatch 🎉

Your account has been created successfully.
Below is your auto-generated username, which you’ll need to log in.
You can change this later from your profile settings.

Username: {username}

Kindly enter this username on the login page to continue.

Enjoy your journey with us 💙
Team MoodMatch
""",
                from_email="jay451428@gmail.com",
                from_password="xpya nqal apnd jxqe",
            )

        return redirect(url_for("auth.login"))

    return render_template("auth/registration.html")


# ---------------------------
# LOGIN
# ---------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,),
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            # TODO: verify password_hash with check_password_hash if needed
            return redirect(url_for("main.index"))

    return render_template("auth/login.html")


# ---------------------------
# FORGET PASSWORD
# ---------------------------
@auth_bp.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()

        if not email or not username:
            return render_template(
                "auth/forget_password.html", error="Both username and email are required"
            )

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()

        # Fetch user with both username and email
        cursor.execute(
            "SELECT id FROM users WHERE email = ? AND username = ?",
            (email, username)
        )
        res = cursor.fetchone()
        conn.close()

        if not res:
            return render_template(
                "auth/forget_password.html", error="No user found with that username and email"
            )

        user_id = res[0]

        # Generate 6-character reset code
        reset_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Store reset code in DB for this user
        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET reset_code = ? WHERE id = ?", (reset_code, user_id))
        conn.commit()
        conn.close()

        # Send reset code to the email
        send_email(
            to_email=email,
            subject="MoodMatch Password Reset Code",
            body=f"""Hello {username},

You requested to reset your MoodMatch password.

Your password reset code is: {reset_code}

Enter this code in the application to reset your password.
Do not share this code with anyone.

Team MoodMatch
""",
        )

        # Redirect to verify code page passing username as parameter
        return redirect(url_for("auth.verify_code", username=username))

    return render_template("auth/forget_password.html")



# ---------------------------
# VERIFY RESET CODE
# ---------------------------
@auth_bp.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    username = request.args.get("username", "").strip()
    if not username:
        return redirect(url_for("auth.forget_password"))

    if request.method == "POST":
        code_entered = request.form.get("reset_code").strip()
        username = request.form.get("username").strip()  # hidden input

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()
        cursor.execute("SELECT reset_code FROM users WHERE username = ?", (username,))
        res = cursor.fetchone()
        conn.close()

        if not res or res[0] != code_entered:
            return render_template("auth/verify_reset_code.html", error="Invalid reset code", username=username)

        # Code verified → redirect to reset password page
        return redirect(url_for("auth.reset_password", username=username))

    return render_template("auth/verify_reset_code.html", username=username)



# ---------------------------
# RESET PASSWORD
# ---------------------------
@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    username = request.form.get("username") or request.args.get("username")
    if not username:
        return redirect(url_for("auth.forget_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        username = request.form.get("username")  # hidden field

        if new_password != confirm_password:
            return render_template("auth/reset_password.html", error="Passwords do not match", username=username)

        password_hash = generate_password_hash(new_password)

        conn = sqlite3.connect("models/mood.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ?, reset_code = NULL WHERE username = ?",
            (password_hash, username)
        )
        conn.commit()
        conn.close()

        return render_template("auth/reset_password.html", success="Password reset successfully!", username=username)

    return render_template("auth/reset_password.html", username=username)



@auth_bp.route("/logout")
def logout():
    return redirect(url_for("main.index"))
