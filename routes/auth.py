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
                welcome_email_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to MoodMatch</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Outfit', sans-serif; background-color: #f4f7fa;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: 1px;">MOODMATCH</h1>
                            <p style="margin: 10px 0 0 0; color: #e0e7ff; font-size: 16px;">Welcome to Your Journey</p>
                        </td>
                    </tr>
                    
                    <!-- Success Badge -->
                    <tr>
                        <td style="padding: 30px 30px 10px 30px; text-align: center;">
                            <div style="display: inline-block; background-color: #10b981; color: white; padding: 10px 20px; border-radius: 25px; font-size: 14px; font-weight: 600;">
                                ✓ Account Created Successfully
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Greeting -->
                    <tr>
                        <td style="padding: 20px 30px 10px 30px;">
                            <h2 style="margin: 0; color: #1f2937; font-size: 24px; font-weight: 600;">Hello {first_name},</h2>
                            <p style="margin: 15px 0 0 0; color: #6b7280; font-size: 16px; line-height: 1.6;">
                                Congratulations! Your MoodMatch account has been successfully created. We're thrilled to have you join our community of like-minded individuals discovering activities that match their mood.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Account Details Card -->
                    <tr>
                        <td style="padding: 20px 30px;">
                            <table style="width: 100%; border-collapse: collapse; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                                <tr>
                                    <td style="padding: 20px; border-bottom: 1px solid #e5e7eb;">
                                        <h3 style="margin: 0 0 15px 0; color: #1f2937; font-size: 16px; font-weight: 600;">Account Details</h3>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 0 20px 10px 20px;">
                                        <table style="width: 100%;">
                                            <tr>
                                                <td style="padding: 8px 0; color: #6b7280; font-size: 14px; width: 35%;">Username:</td>
                                                <td style="padding: 8px 0; color: #1f2937; font-size: 14px; font-weight: 600;">{username}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;">Email:</td>
                                                <td style="padding: 8px 0; color: #1f2937; font-size: 14px; font-weight: 600;">{email}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #6b7280; font-size: 14px;">Status:</td>
                                                <td style="padding: 8px 0; color: #10b981; font-size: 14px; font-weight: 600;">Active ✓</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- What's Next -->
                    <tr>
                        <td style="padding: 10px 30px 20px 30px;">
                            <h3 style="margin: 0 0 15px 0; color: #1f2937; font-size: 18px; font-weight: 600;">What's Next?</h3>
                            <table style="width: 100%;">
                                <tr>
                                    <td style="padding: 8px 0;">
                                        <span style="color: #10b981; font-size: 18px; margin-right: 10px;">✓</span>
                                        <span style="color: #4b5563; font-size: 15px;">Complete your profile with interests and preferences</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0;">
                                        <span style="color: #10b981; font-size: 18px; margin-right: 10px;">✓</span>
                                        <span style="color: #4b5563; font-size: 15px;">Explore personalized activity recommendations</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0;">
                                        <span style="color: #10b981; font-size: 18px; margin-right: 10px;">✓</span>
                                        <span style="color: #4b5563; font-size: 15px;">Connect with like-minded individuals</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0;">
                                        <span style="color: #10b981; font-size: 18px; margin-right: 10px;">✓</span>
                                        <span style="color: #4b5563; font-size: 15px;">Discover events that match your mood</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- CTA Button -->
                    <tr>
                        <td style="padding: 10px 30px 30px 30px; text-align: center;">
                            <a href="http://127.0.0.1:6969/login" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 14px 40px; border-radius: 6px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);">
                                Get Started Now →
                            </a>
                        </td>
                    </tr>
                    
                    <!-- Getting Started Steps -->
                    <tr>
                        <td style="padding: 20px 30px; background-color: #f9fafb; border-top: 1px solid #e5e7eb;">
                            <h3 style="margin: 0 0 15px 0; color: #1f2937; font-size: 16px; font-weight: 600;">Getting Started</h3>
                            <ol style="margin: 0; padding-left: 20px; color: #4b5563; font-size: 14px; line-height: 1.8;">
                                <li style="margin-bottom: 8px;">Log in with your username: <strong style="color: #667eea;">{username}</strong></li>
                                <li style="margin-bottom: 8px;">Customize your profile settings</li>
                                <li style="margin-bottom: 8px;">Browse activities tailored to your interests</li>
                                <li style="margin-bottom: 8px;">Start your MoodMatch journey!</li>
                            </ol>
                        </td>
                    </tr>
                    
                    <!-- Support Section -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px; border-top: 1px solid #e5e7eb;">
                            <h3 style="margin: 0 0 15px 0; color: #1f2937; font-size: 16px; font-weight: 600;">Need Assistance?</h3>
                            <p style="margin: 0 0 15px 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                We're here to help! If you have any questions or need support:
                            </p>
                            <table style="width: 100%;">
                                <tr>
                                    <td style="padding: 6px 0; color: #4b5563; font-size: 14px;">
                                        <span style="margin-right: 8px;">📧</span>
                                        <a href="mailto:support@moodmatch.com" style="color: #667eea; text-decoration: none;">support@moodmatch.com</a>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 6px 0; color: #4b5563; font-size: 14px;">
                                        <span style="margin-right: 8px;">🌐</span>
                                        <a href="http://www.moodmatch.com/help" style="color: #667eea; text-decoration: none;">www.moodmatch.com/help</a>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 6px 0; color: #4b5563; font-size: 14px;">
                                        <span style="margin-right: 8px;">💬</span>
                                        Live Chat available 24/7 in your dashboard
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Security Reminder -->
                    <tr>
                        <td style="padding: 20px 30px; background-color: #fef3c7; border-left: 4px solid #f59e0b;">
                            <h4 style="margin: 0 0 10px 0; color: #92400e; font-size: 14px; font-weight: 600;">🔒 Security Reminder</h4>
                            <ul style="margin: 0; padding-left: 20px; color: #92400e; font-size: 13px; line-height: 1.6;">
                                <li>Never share your password with anyone</li>
                                <li>Enable two-factor authentication for added security</li>
                                <li>Log out when using shared devices</li>
                            </ul>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; text-align: center; background-color: #1f2937; color: #9ca3af;">
                            <p style="margin: 0 0 10px 0; font-size: 14px; line-height: 1.6;">
                                We're thrilled to have you as part of the MoodMatch community!
                            </p>
                            <p style="margin: 0 0 20px 0; font-size: 14px; color: #d1d5db;">
                                Best regards,<br>
                                <strong style="color: #ffffff;">The MoodMatch Team</strong>
                            </p>
                            <div style="border-top: 1px solid #374151; padding-top: 20px; margin-top: 20px;">
                                <p style="margin: 0 0 5px 0; font-size: 12px; color: #6b7280;">
                                    © 2026 MoodMatch. All rights reserved.
                                </p>
                                <p style="margin: 5px 0 0 0; font-size: 11px; color: #6b7280; line-height: 1.5;">
                                    This email was sent to {email}. If you did not create this account,<br>
                                    please contact us immediately at <a href="mailto:security@moodmatch.com" style="color: #667eea; text-decoration: none;">security@moodmatch.com</a>
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
                send_email(
                    to_email=email,
                    subject="Welcome to MoodMatch - Account Created Successfully ✓",
                    body=welcome_email_body,
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
                    is_admin=True,  # Explicitly set to True
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
                    is_admin=False,  # Explicitly set to False
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

        reset_email_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset - MoodMatch</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Outfit', sans-serif; background-color: #f4f7fa;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 40px 30px; text-align: center;">
                            <div style="background-color: rgba(255, 255, 255, 0.2); width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center;">
                                <span style="font-size: 40px; align-items: center;">🔐</span>
                            </div>
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">Password Reset Request</h1>
                            <p style="margin: 10px 0 0 0; color: #fecaca; font-size: 14px;">MoodMatch Security</p>
                        </td>
                    </tr>
                    
                    <!-- Alert Badge -->
                    <tr>
                        <td style="padding: 30px 30px 10px 30px; text-align: center;">
                            <div style="display: inline-block; background-color: #fef3c7; border: 2px solid #f59e0b; color: #92400e; padding: 10px 20px; border-radius: 6px; font-size: 14px; font-weight: 600;">
                                ⚠️ Security Alert
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Greeting -->
                    <tr>
                        <td style="padding: 20px 30px 10px 30px;">
                            <h2 style="margin: 0; color: #1f2937; font-size: 22px; font-weight: 600;">Hello {first_name or "there"},</h2>
                            <p style="margin: 15px 0 0 0; color: #6b7280; font-size: 16px; line-height: 1.6;">
                                We received a request to reset the password for your MoodMatch account. Use the verification code below to proceed with resetting your password.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Verification Code Card -->
                    <tr>
                        <td style="padding: 20px 30px;">
                            <table style="width: 100%; border-collapse: collapse; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; overflow: hidden; box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);">
                                <tr>
                                    <td style="padding: 30px; text-align: center;">
                                        <p style="margin: 0 0 10px 0; color: #e0e7ff; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Your Verification Code</p>
                                        <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; margin: 15px 0;">
                                            <p style="margin: 0; color: #667eea; font-size: 42px; font-weight: 700; letter-spacing: 8px; font-family: 'Outfit', sans-serif;">{reset_code}</p>
                                        </div>
                                        <p style="margin: 10px 0 0 0; color: #fde68a; font-size: 13px; font-weight: 500;">
                                            ⏰ This code will expire in 15 minutes
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- How to Reset -->
                    <tr>
                        <td style="padding: 10px 30px 20px 30px;">
                            <h3 style="margin: 0 0 15px 0; color: #1f2937; font-size: 18px; font-weight: 600;">How to Reset Your Password</h3>
                            <ol style="margin: 0; padding-left: 20px; color: #4b5563; font-size: 15px; line-height: 1.8;">
                                <li style="margin-bottom: 10px;">Return to the MoodMatch password reset page</li>
                                <li style="margin-bottom: 10px;">Enter the verification code: <strong style="color: #667eea; font-family: 'Outfit', sans-serif;">{reset_code}</strong></li>
                                <li style="margin-bottom: 10px;">Create a new secure password</li>
                                <li style="margin-bottom: 10px;">Log in with your new credentials</li>
                            </ol>
                        </td>
                    </tr>
                    
                    <!-- CTA Button -->
                    <tr>
                        <td style="padding: 10px 30px 30px 30px; text-align: center;">
                            <a href="http://127.0.0.1:6969/verify_code?username={username}" style="display: inline-block; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: #ffffff; text-decoration: none; padding: 14px 40px; border-radius: 6px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 6px rgba(239, 68, 68, 0.3);">
                                Reset Password Now →
                            </a>
                        </td>
                    </tr>
                    
                    <!-- Security Warning -->
                    <tr>
                        <td style="padding: 20px 30px; background-color: #fee2e2; border-left: 4px solid #ef4444;">
                            <h4 style="margin: 0 0 10px 0; color: #991b1b; font-size: 15px; font-weight: 700;">⚠️ SECURITY NOTICE</h4>
                            <ul style="margin: 0; padding-left: 20px; color: #991b1b; font-size: 13px; line-height: 1.7;">
                                <li style="margin-bottom: 6px;"><strong>DO NOT share this code with anyone</strong> - not even MoodMatch support</li>
                                <li style="margin-bottom: 6px;">MoodMatch staff will <strong>NEVER</strong> ask for your verification code</li>
                                <li style="margin-bottom: 6px;">If you didn't request this reset, ignore this email</li>
                                <li>Your account remains secure and no changes have been made</li>
                            </ul>
                        </td>
                    </tr>
                    
                    <!-- Didn't Request Section -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px; border-top: 1px solid #e5e7eb;">
                            <h3 style="margin: 0 0 12px 0; color: #1f2937; font-size: 16px; font-weight: 600;">Didn't Request This?</h3>
                            <p style="margin: 0 0 12px 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                If you did not initiate this password reset:
                            </p>
                            <table style="width: 100%; background-color: #f9fafb; border-radius: 6px; padding: 15px;">
                                <tr>
                                    <td style="color: #4b5563; font-size: 14px; line-height: 1.7;">
                                        <div style="margin-bottom: 8px;">✓ Your account is still secure</div>
                                        <div style="margin-bottom: 8px;">✓ No action is required from you</div>
                                        <div style="margin-bottom: 8px;">✓ Consider changing your password as a precaution</div>
                                        <div>✓ Contact us if you suspect unauthorized access</div>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin: 15px 0 0 0; color: #6b7280; font-size: 13px;">
                                📧 Security Team: <a href="mailto:security@moodmatch.com" style="color: #ef4444; text-decoration: none; font-weight: 600;">security@moodmatch.com</a>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Need Help -->
                    <tr>
                        <td style="padding: 20px 30px 30px 30px; background-color: #f9fafb;">
                            <h3 style="margin: 0 0 12px 0; color: #1f2937; font-size: 16px; font-weight: 600;">Need Help?</h3>
                            <table style="width: 100%;">
                                <tr>
                                    <td style="padding: 5px 0; color: #4b5563; font-size: 14px;">
                                        <span style="margin-right: 8px;">🌐</span>
                                        <a href="http://www.moodmatch.com/help" style="color: #667eea; text-decoration: none;">Help Center</a>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px 0; color: #4b5563; font-size: 14px;">
                                        <span style="margin-right: 8px;">📧</span>
                                        <a href="mailto:support@moodmatch.com" style="color: #667eea; text-decoration: none;">support@moodmatch.com</a>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px 0; color: #4b5563; font-size: 14px;">
                                        <span style="margin-right: 8px;">💬</span>
                                        Live Chat available 24/7
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; text-align: center; background-color: #1f2937; color: #9ca3af;">
                            <p style="margin: 0 0 10px 0; font-size: 14px; line-height: 1.6;">
                                Stay safe,
                            </p>
                            <p style="margin: 0 0 20px 0; font-size: 14px; color: #d1d5db;">
                                <strong style="color: #ffffff;">The MoodMatch Security Team</strong>
                            </p>
                            <div style="border-top: 1px solid #374151; padding-top: 20px; margin-top: 20px;">
                                <p style="margin: 0 0 5px 0; font-size: 12px; color: #6b7280;">
                                    © 2026 MoodMatch. All rights reserved.
                                </p>
                                <p style="margin: 5px 0 0 0; font-size: 11px; color: #6b7280; line-height: 1.5;">
                                    This is an automated security email sent to {email}
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

        send_email(
            to_email=email,
            subject="MoodMatch Password Reset - Verification Code Inside 🔐",
            body=reset_email_body,
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
