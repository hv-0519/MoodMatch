from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from datetime import date, datetime
import sqlite3

admin_bp = Blueprint("admin", __name__)

DB_PATH = "models/mood.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ===============================
# Admin Dashboard
# ===============================
@admin_bp.route("/admin_dashboard")
@login_required
def admin_dashboard():
    conn = sqlite3.connect("models/mood.db")
    # --- ADD THIS LINE ---
    conn.row_factory = sqlite3.Row 
    # ---------------------
    cursor = conn.cursor()

    # Get total Users
    cursor.execute("""SELECT COUNT(*) from users""")
    total_users = cursor.fetchone()[0]

    # Get total Activities
    cursor.execute("""SELECT COUNT(*) FROM activities""")
    total_activities = cursor.fetchone()[0]

    today = date.today().isoformat()
    cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?", (today,))
    registered_today = cursor.fetchone()[0] 

    # Fetch the actual list for the table
    cursor.execute("SELECT username, email, created_at FROM users ORDER BY created_at LIMIT 5")
    
    # Now dict(row) will work because row_factory is set
    users = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        total_activities=total_activities,
        registered_today=registered_today,
        users=users
    )


# ===============================
# Manage Users
# ===============================


@admin_bp.route("/manage_users", methods=["GET", "POST", "PUT"])
@login_required
def manage_users():
    conn = None
    users = []
    error = None

    try:
        conn = sqlite3.connect("models/mood.db")
        conn.row_factory = sqlite3.Row  # so we get dict-like rows
        cursor = conn.cursor()

        # Fetch ALL users - with useful columns
        cursor.execute(
            """
            SELECT 
                id,
                username,
                first_name,
                last_name,
                email,
                phone_number,
                gender,
                date_of_birth,
                created_at,
                profile_picture,
                -- You can add more like: last_login, is_active, etc. later
                CASE 
                    WHEN created_at > DATE('now', '-7 days') THEN 'New'
                    ELSE 'Active'
                END AS status_tag
            FROM users
            ORDER BY created_at
        """
        )

        users = cursor.fetchall()  # list of sqlite3.Row objects (dict-like)

    except sqlite3.Error as e:
        error = f"Database error: {str(e)}"
        print(error)  # log in production

    finally:
        if conn:
            conn.close()

    return render_template(
        "admin/manage_users.html",
        users=users,
        error=error,
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M IST"),
    )


# ===============================
# Manage Activities (CRUD)
# ===============================
@admin_bp.route("/manage_activity", methods=["GET", "POST", "PUT", "PATCH"])
@login_required
def manage_activity():
    conn = get_db()
    cur = conn.cursor()

    try:
        # GET: Fetch data and RENDER the page
        if request.method == "GET":
            cur.execute("""
                SELECT id, name, execution_type, is_active, priority, created_at 
                FROM activities 
                
            """)
            # Convert rows to a list of dictionaries
            activities_list = [dict(row) for row in cur.fetchall()]
            return render_template("admin/manage_activities.html", activities=activities_list)

        # For POST, PUT, PATCH — expect JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON"}), 400

        # POST: Create new activity
        if request.method == "POST":
            cur.execute(
                """
                INSERT INTO activities (name, execution_type, description, priority)
                VALUES (?, ?, ?, ?)
                """,
                (
                    data.get("name"),
                    data.get("execution_type"),
                    data.get("description"),
                    data.get("priority", 0),
                ),
            )
            activity_id = cur.lastrowid

            # Optional: domains
            for domain_id in data.get("domain_ids", []):
                cur.execute(
                    "INSERT INTO activity_domains (activity_id, domain_id) VALUES (?, ?)",
                    (activity_id, domain_id),
                )

            # Optional: moods
            for mood in data.get("moods", []):
                cur.execute(
                    "INSERT INTO activity_moods (activity_id, mood_id, weight) VALUES (?, ?, ?)",
                    (activity_id, mood["mood_id"], mood["weight"]),
                )

            # Optional: filters
            cur.execute(
                """
                INSERT INTO activity_filters (
                    activity_id, min_time, max_time, min_budget, max_budget,
                    energy_level, location_type, distance_type, social_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    activity_id,
                    data.get("min_time"),
                    data.get("max_time"),
                    data.get("min_budget"),
                    data.get("max_budget"),
                    data.get("energy_level"),
                    data.get("location_type"),
                    data.get("distance_type"),
                    data.get("social_type"),
                ),
            )

            conn.commit()

            # Return the new activity for frontend refresh
            cur.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
            new_activity = dict(cur.fetchone())
            return jsonify({"message": "Activity created", "activity": new_activity}), 201

        # PUT: Update activity
        if request.method == "PUT":
            activity_id = data.get("activity_id")
            if not activity_id:
                return jsonify({"error": "activity_id required"}), 400

            cur.execute(
                """
                UPDATE activities
                SET name = ?, execution_type = ?, description = ?, priority = ?
                WHERE id = ?
                """,
                (
                    data.get("name"),
                    data.get("execution_type"),
                    data.get("description"),
                    data.get("priority", 0),
                    activity_id,
                ),
            )

            # Reset domains
            cur.execute("DELETE FROM activity_domains WHERE activity_id = ?", (activity_id,))
            for domain_id in data.get("domain_ids", []):
                cur.execute(
                    "INSERT INTO activity_domains (activity_id, domain_id) VALUES (?, ?)",
                    (activity_id, domain_id),
                )

            # Reset moods
            cur.execute("DELETE FROM activity_moods WHERE activity_id = ?", (activity_id,))
            for mood in data.get("moods", []):
                cur.execute(
                    "INSERT INTO activity_moods (activity_id, mood_id, weight) VALUES (?, ?, ?)",
                    (activity_id, mood["mood_id"], mood["weight"]),
                )

            # Update filters
            cur.execute(
                """
                UPDATE activity_filters
                SET min_time = ?, max_time = ?, min_budget = ?, max_budget = ?,
                    energy_level = ?, location_type = ?, distance_type = ?, social_type = ?
                WHERE activity_id = ?
                """,
                (
                    data.get("min_time"),
                    data.get("max_time"),
                    data.get("min_budget"),
                    data.get("max_budget"),
                    data.get("energy_level"),
                    data.get("location_type"),
                    data.get("distance_type"),
                    data.get("social_type"),
                    activity_id,
                ),
            )

            conn.commit()

            cur.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
            updated = dict(cur.fetchone() or {})
            return jsonify({"message": "Activity updated", "activity": updated})

        # PATCH: Toggle active status
        if request.method == "PATCH":
            activity_id = data.get("activity_id")
            is_active = data.get("is_active")

            if not activity_id or is_active is None:
                return jsonify({"error": "activity_id and is_active required"}), 400

            cur.execute(
                "UPDATE activities SET is_active = ? WHERE id = ?",
                (is_active, activity_id),
            )
            conn.commit()
            return jsonify({"message": "Activity status updated"})

    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    finally:
        conn.close()