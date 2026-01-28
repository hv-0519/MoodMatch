from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date, datetime
import sqlite3

admin_bp = Blueprint("admin", __name__)

DB_PATH = "models/mood.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_admin_name(cursor):
    """Helper to get the admin username for the header."""
    cursor.execute("""SELECT username FROM admins LIMIT 1""")
    row = cursor.fetchone()
    return row[0] if row else "Administrator"

# ===============================
# Admin Dashboard
# ===============================
@admin_bp.route("/admin_dashboard")
@login_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()

    admins = get_admin_name(cursor)

    # Stats for overview cards
    cursor.execute("""SELECT COUNT(*) from users""")
    total_users = cursor.fetchone()[0]

    cursor.execute("""SELECT COUNT(*) FROM activities""")
    total_activities = cursor.fetchone()[0]

    today = date.today().isoformat()
    cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?", (today,))
    registered_today = cursor.fetchone()[0]

    # Recent Users Table
    cursor.execute(
        "SELECT username, email, created_at FROM users ORDER BY created_at DESC LIMIT 5"
    )
    users = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        total_activities=total_activities,
        registered_today=registered_today,
        users=users,
        admins=admins,
    )

# ===============================
# Manage Users
# ===============================
@admin_bp.route("/manage_users")
@login_required
def manage_users():
    conn = get_db()
    cursor = conn.cursor()
    
    admins = get_admin_name(cursor)

    # Fetch all users with a status tag based on account age
    cursor.execute("""
        SELECT 
            id, username, first_name, last_name, email, 
            phone_number, gender, date_of_birth, created_at, profile_picture,
            CASE 
                WHEN created_at > DATE('now', '-7 days') THEN 'New'
                ELSE 'Active'
            END AS status_tag
        FROM users
        ORDER BY created_at DESC
    """)
    users = cursor.fetchall()

    conn.close()
    return render_template(
        "admin/manage_users.html",
        users=users,
        admins=admins,
        current_time=datetime.now().strftime("%d-%m-%Y %H:%M IST")
    )

# ===============================
# Manage Activities (CRUD)
# ===============================
@admin_bp.route("/manage_activity", methods=["GET", "POST"])
@login_required
def manage_activity():
    conn = get_db()
    cursor = conn.cursor()
    admins = get_admin_name(cursor)
    error = None

    if request.method == "POST":
        action = request.form.get("action")
        
        try:
            if action == "add":
                name = request.form.get("name", "").strip()
                execution_type = request.form.get("execution_type", "").strip()
                description = request.form.get("description", "").strip()
                priority = int(request.form.get("priority") or 0)

                if name and execution_type:
                    cursor.execute(
                        "INSERT INTO activities (name, execution_type, description, priority, is_active) VALUES (?, ?, ?, ?, 1)",
                        (name, execution_type, description, priority)
                    )
                    conn.commit()
                    flash("Activity added successfully!", "success")
                else:
                    flash("Name and Type are required.", "error")

            elif action == "edit":
                activity_id = request.form.get("activity_id")
                name = request.form.get("name", "").strip()
                execution_type = request.form.get("execution_type", "").strip()
                description = request.form.get("description", "").strip()
                priority = int(request.form.get("priority") or 0)

                cursor.execute(
                    "UPDATE activities SET name=?, execution_type=?, description=?, priority=? WHERE id=?",
                    (name, execution_type, description, priority, activity_id)
                )
                conn.commit()
                flash("Activity updated successfully!", "success")

            elif action == "delete":
                activity_id = request.form.get("activity_id")
                cursor.execute("DELETE FROM activities WHERE id=?", (activity_id,))
                conn.commit()
                flash("Activity deleted successfully!", "success")

        except sqlite3.Error as e:
            conn.rollback()
            flash(f"Database error: {str(e)}", "error")

    # Fetch updated list for display (Common for GET and POST)
    cursor.execute("""
        SELECT id, name, execution_type, is_active, priority, created_at 
        FROM activities 
        ORDER BY created_at
    """)
    activities = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return render_template(
        "admin/manage_activities.html", 
        activities=activities, 
        admins=admins
    )

@admin_bp.route("/update_activity", methods=["POST"])
@login_required
def update_activity():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        activity_id = request.form.get("activity_id")
        name = request.form.get("name", "").strip()
        execution_type = request.form.get("execution_type", "").strip()
        priority = int(request.form.get("priority") or 0)

        if activity_id and name and execution_type:
            cursor.execute(
                "UPDATE activities SET name=?, execution_type=?, priority=? WHERE id=?",
                (name, execution_type, priority, activity_id)
            )
            conn.commit()
            flash("Activity updated successfully!", "success")
        else:
            flash("Please fill all required fields.", "error")

    except sqlite3.Error as e:
        conn.rollback()
        flash(f"Database error: {str(e)}", "error")
    finally:
        conn.close()
    
    return redirect(url_for("admin.manage_activity"))


@admin_bp.route("/delete_activity", methods=["POST"])
@login_required
def delete_activity():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        activity_id = request.form.get("activity_id")
        
        if activity_id:
            cursor.execute("DELETE FROM activities WHERE id=?", (activity_id,))
            conn.commit()
            flash("Activity deleted successfully!", "success")
        else:
            flash("Invalid activity ID.", "error")

    except sqlite3.Error as e:
        conn.rollback()
        flash(f"Database error: {str(e)}", "error")
    finally:
        conn.close()
    
    return redirect(url_for("admin.manage_activity"))
