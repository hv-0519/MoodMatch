import csv
import sqlite3
from io import StringIO
from datetime import date, timedelta, datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    make_response,
)
from flask_login import login_required

admin_bp = Blueprint("admin", __name__)

DB_PATH = "models/instance/moodmatch.db"


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
    try:
        admins = get_admin_name(cursor)

        # Stats
        cursor.execute("SELECT COUNT(*) from users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM activities")
        total_activities = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM categories")
        total_categories = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_history")
        total_history = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')"
        )
        registered_today = cursor.fetchone()[0]

        # Growth Chart (Last 7 days)
        cursor.execute(
            """
            SELECT DATE(created_at) as reg_date, COUNT(id) as user_count
            FROM users WHERE created_at >= DATE('now', '-6 days')
            GROUP BY reg_date ORDER BY reg_date ASC
        """
        )
        reg_stats = {row["reg_date"]: row["user_count"] for row in cursor.fetchall()}
        chart_labels, chart_data = [], []
        for i in range(6, -1, -1):
            day = date.today() - timedelta(days=i)
            chart_labels.append(day.strftime("%d %b"))
            chart_data.append(reg_stats.get(day.isoformat(), 0))

        # ============================================
        # NEW: User Interests Chart Data (Real-time)
        # ============================================
        cursor.execute(
            """
            SELECT 
                i.name as interest_name,
                COUNT(DISTINCT ui.user_id) as user_count
            FROM interests i
            LEFT JOIN user_interests ui ON i.id = ui.interest_id
            GROUP BY i.id, i.name
            HAVING user_count > 0
            ORDER BY user_count DESC
            LIMIT 10
        """
        )
        interests_data = cursor.fetchall()

        # Prepare data for Chart.js
        interest_labels = [row["interest_name"].capitalize() for row in interests_data]
        interest_counts = [row["user_count"] for row in interests_data]

        # Beautiful gradient colors for the doughnut chart
        interest_colors = [
            "#8ec5fc",  # Blue
            "#e0c3fc",  # Purple
            "#fbc2eb",  # Pink
            "#a6c1ee",  # Light Blue
            "#fccb90",  # Orange
            "#d4fc79",  # Green
            "#96e6a1",  # Mint
            "#ffeaa7",  # Yellow
            "#fab1a0",  # Coral
            "#fd79a8",  # Rose
        ]

        # Recent Users (for table)
        cursor.execute(
            "SELECT id, username, email, created_at, profile_picture FROM users ORDER BY created_at DESC LIMIT 5"
        )
        users = [dict(row) for row in cursor.fetchall()]

        return render_template(
            "admin/admin_dashboard.html",
            admins=admins,
            total_users=total_users,
            total_activities=total_activities,
            total_categories=total_categories,
            total_history=total_history,
            registered_today=registered_today,
            users=users,
            chart_labels=chart_labels,
            chart_data=chart_data,
            # NEW: Interest chart data
            interest_labels=interest_labels,
            interest_counts=interest_counts,
            interest_colors=interest_colors,
        )
    finally:
        conn.close()


# ===============================
# Manage Users
# ===============================
@admin_bp.route("/manage_users")
@login_required
def manage_users():
    conn = get_db()
    cursor = conn.cursor()
    try:
        admins = get_admin_name(cursor)
        cursor.execute(
            """
            SELECT 
                u.id, u.username, u.first_name, u.last_name, u.email, 
                u.phone_number, u.gender, u.date_of_birth, u.created_at, 
                u.profile_picture, u.street_address, u.city, u.state, 
                u.postal_code, u.country,
                GROUP_CONCAT(i.name, ', ') AS user_interests,
                CASE 
                    WHEN u.created_at > DATE('now', '-7 days') THEN 'New'
                    ELSE 'Active'
                END AS status_tag
            FROM users u
            LEFT JOIN user_interests ui ON u.id = ui.user_id
            LEFT JOIN interests i ON ui.interest_id = i.id
            GROUP BY u.id
            ORDER BY u.created_at
        """
        )
        users = [dict(row) for row in cursor.fetchall()]

        return render_template(
            "admin/manage_users.html",
            users=users,
            admins=admins,
            current_time=datetime.now().strftime("%d-%m-%Y %H:%M IST"),
        )
    finally:
        conn.close()


# ===============================
# Manage Activities (CRUD) - IMPROVED WITH CATEGORY INFO
# ===============================
@admin_bp.route("/manage_activity", methods=["GET", "POST"])
@login_required
def manage_activity():
    conn = get_db()
    cursor = conn.cursor()

    # ===================== POST =====================
    if request.method == "POST":
        action = request.form.get("action")

        # DEBUG LOGGING
        print(f"\n{'='*60}")
        print("POST REQUEST RECEIVED")
        print("Action:", action)
        print("Form Data:", dict(request.form))
        print(f"{'='*60}\n")

        try:
            # ---------- ADD ----------
            if action == "add":
                name = request.form.get("name", "").strip()
                ex_type = request.form.get("execution_type", "").strip()
                desc = request.form.get("description", "").strip()
                mood_tags = request.form.get("mood_tags", "").strip()
                energy_level = request.form.get("energy_level", "").strip()
                location_type = request.form.get("location_type", "").strip()
                social_type = request.form.get("social_type", "").strip()
                min_time = request.form.get("min_time", "").strip()
                max_time = request.form.get("max_time", "").strip()
                min_budget = request.form.get("min_budget", "").strip()
                max_budget = request.form.get("max_budget", "").strip()
                prio = int(request.form.get("priority") or 0)

                # ✅ category_id must be INTEGER
                category_id = request.form.get("category_id")
                if not category_id:
                    flash("Category is required", "error")
                    return redirect(url_for("admin.manage_activity"))
                category_id = int(category_id)

                # ✅ is_active from checkbox
                is_active = 1 if request.form.get("is_active") else 0

                if not name or not ex_type or not mood_tags:
                    flash("Name, Execution Type, and Mood Tags are required", "error")
                    return redirect(url_for("admin.manage_activity"))

                cursor.execute(
                    """
                    INSERT INTO activities (
                        name,
                        execution_type,
                        description,
                        priority,
                        category_id,
                        is_active,
                        mood_tags,
                        energy_level,
                        location_type,
                        social_type,
                        min_time,
                        max_time,
                        min_budget,
                        max_budget
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        ex_type,
                        desc,
                        prio,
                        category_id,
                        is_active,
                        mood_tags,
                        energy_level,
                        location_type,
                        social_type,
                        int(min_time) if min_time else None,
                        int(max_time) if max_time else None,
                        int(min_budget) if min_budget else None,
                        int(max_budget) if max_budget else None,
                    ),
                )
                conn.commit()
                print(f"✓ Activity inserted successfully! ID={cursor.lastrowid}")
                flash("Activity added successfully!", "success")

            # ---------- EDIT ----------
            elif action == "edit":
                act_id = request.form.get("activity_id")
                name = request.form.get("name", "").strip()
                ex_type = request.form.get("execution_type", "").strip()
                desc = request.form.get("description", "").strip()
                mood_tags = request.form.get("mood_tags", "").strip()
                energy_level = request.form.get("energy_level", "").strip()
                location_type = request.form.get("location_type", "").strip()
                social_type = request.form.get("social_type", "").strip()
                min_time = request.form.get("min_time", "").strip()
                max_time = request.form.get("max_time", "").strip()
                min_budget = request.form.get("min_budget", "").strip()
                max_budget = request.form.get("max_budget", "").strip()

                # Use 0 or a default if priority is empty
                prio_raw = request.form.get("priority")
                prio = int(prio_raw) if prio_raw and prio_raw.isdigit() else 0

                cat_id_raw = request.form.get("category_id")
                category_id = (
                    int(cat_id_raw) if cat_id_raw and cat_id_raw.isdigit() else None
                )

                # ✅ is_active from checkbox
                is_active = 1 if request.form.get("is_active") else 0

                if not act_id or not name:
                    flash("Record ID and Name are required", "error")
                else:
                    cursor.execute(
                        """
                        UPDATE activities
                        SET name=?, 
                            execution_type=?, 
                            description=?, 
                            priority=?, 
                            category_id=?,
                            is_active=?,
                            mood_tags=?,
                            energy_level=?,
                            location_type=?,
                            social_type=?,
                            min_time=?,
                            max_time=?,
                            min_budget=?,
                            max_budget=?
                        WHERE id=?
                        """,
                        (
                            name,
                            ex_type,
                            desc,
                            prio,
                            category_id,
                            is_active,
                            mood_tags,
                            energy_level,
                            location_type,
                            social_type,
                            int(min_time) if min_time else None,
                            int(max_time) if max_time else None,
                            int(min_budget) if min_budget else None,
                            int(max_budget) if max_budget else None,
                            act_id,
                        ),
                    )
                    conn.commit()
                    flash("Activity updated successfully!", "success")

            # ---------- DELETE ----------
            elif action == "delete":
                act_id = request.form.get("activity_id")
                cursor.execute("DELETE FROM activities WHERE id=?", (act_id,))
                conn.commit()
                flash("Activity deleted successfully!", "success")

        except sqlite3.Error as e:
            conn.rollback()
            print("✗ DATABASE ERROR:", e)
            flash(f"Database error: {e}", "error")

        return redirect(url_for("admin.manage_activity"))

    # ===================== GET =====================
    try:
        admins = get_admin_name(cursor)

        # ✅ Categories for dropdown (with icons)
        cursor.execute("SELECT id, name, icon FROM categories ORDER BY name")
        categories = [dict(row) for row in cursor.fetchall()]

        # ✅ Activities list WITH category info JOIN
        cursor.execute(
            """
            SELECT 
                a.*,
                c.name as category_name,
                c.icon as category_icon
            FROM activities a
            LEFT JOIN categories c ON a.category_id = c.id
            ORDER BY a.created_at
        """
        )
        activities_list = [dict(row) for row in cursor.fetchall()]

        # UI index
        for i, item in enumerate(activities_list, start=1):
            item["ui_id"] = i

        return render_template(
            "admin/manage_activities.html",
            activities=activities_list,
            categories=categories,
            admins=admins,
        )

    finally:
        conn.close()


@admin_bp.route("/manage_categories", methods=["GET", "POST"])
@login_required
def manage_categories():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        try:
            if action == "add":
                name = request.form.get("name", "").strip()
                description = request.form.get("description", "").strip()
                icon = request.form.get("icon", "").strip()

                if not name:
                    flash("Category name is required", "error")
                    return redirect(url_for("admin.manage_categories"))

                cursor.execute(
                    "INSERT INTO categories (name, description, icon) VALUES (?, ?, ?)",
                    (name, description, icon),
                )
                conn.commit()
                flash("Category added successfully!", "success")

            elif action == "edit":
                cat_id = request.form.get("category_id")
                name = request.form.get("name", "").strip()
                description = request.form.get("description", "").strip()
                icon = request.form.get("icon", "").strip()

                if not name or not cat_id:
                    flash("Invalid request", "error")
                    return redirect(url_for("admin.manage_categories"))

                cursor.execute(
                    "UPDATE categories SET name=?, description=?, icon=? WHERE id=?",
                    (name, description, icon, cat_id),
                )
                conn.commit()
                flash("Category updated successfully!", "success")

            elif action == "delete":
                cat_id = request.form.get("category_id")
                if not cat_id:
                    flash("Invalid request", "error")
                    return redirect(url_for("admin.manage_categories"))

                cursor.execute("DELETE FROM categories WHERE id=?", (cat_id,))
                conn.commit()
                flash("Category deleted successfully!", "success")

        except sqlite3.Error as e:
            conn.rollback()
            flash(f"Database error: {e}", "error")

        return redirect(url_for("admin.manage_categories"))

    # GET
    try:
        admins = get_admin_name(cursor)
        cursor.execute("SELECT * FROM categories ORDER BY name")
        categories = [dict(row) for row in cursor.fetchall()]

        return render_template(
            "admin/manage_categories.html",
            categories=categories,
            admins=admins,
        )
    finally:
        conn.close()


# ===============================
# Reports (unchanged)
# ===============================
@admin_bp.route("/export_users_report")
@login_required
def export_users_report():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, username, email, created_at FROM users ORDER BY created_at DESC"
        )
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(["User ID", "Username", "Email", "Joined Date"])
        for row in cursor.fetchall():
            cw.writerow([row["id"], row["username"], row["email"], row["created_at"]])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=users_report.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    finally:
        conn.close()


@admin_bp.route("/export_activities_report")
@login_required
def export_activities_report():
    """Export all activities to CSV"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, name, execution_type, description, priority, is_active, created_at 
            FROM activities ORDER BY created_at DESC
        """
        )
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(
            [
                "Activity ID",
                "Name",
                "Type",
                "Description",
                "Priority",
                "Active",
                "Created Date",
            ]
        )
        for row in cursor.fetchall():
            cw.writerow(
                [
                    row["id"],
                    row["name"],
                    row["execution_type"],
                    row["description"] or "",
                    row["priority"],
                    "Yes" if row["is_active"] else "No",
                    row["created_at"],
                ]
            )

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = (
            "attachment; filename=activities_report.csv"
        )
        output.headers["Content-type"] = "text/csv"
        return output
    finally:
        conn.close()


@admin_bp.route("/export_user_interests_report")
@login_required
def export_user_interests_report():
    """Export user interests mapping to CSV"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT 
                u.id as user_id,
                u.username,
                u.email,
                GROUP_CONCAT(i.name, ', ') as interests
            FROM users u
            LEFT JOIN user_interests ui ON u.id = ui.user_id
            LEFT JOIN interests i ON ui.interest_id = i.id
            GROUP BY u.id
            ORDER BY u.username
        """
        )
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(["User ID", "Username", "Email", "Interests"])
        for row in cursor.fetchall():
            cw.writerow(
                [
                    row["user_id"],
                    row["username"],
                    row["email"],
                    row["interests"] if row["interests"] else "No interests",
                ]
            )

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = (
            "attachment; filename=user_interests_report.csv"
        )
        output.headers["Content-type"] = "text/csv"
        return output
    finally:
        conn.close()


@admin_bp.route("/export_moods_report")
@login_required
def export_moods_report():
    """Export mood and activity mapping to CSV"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT 
                m.id as mood_id,
                m.name as mood_name,
                COUNT(DISTINCT am.activity_id) as activity_count
            FROM moods m
            LEFT JOIN activity_moods am ON m.id = am.mood_id
            GROUP BY m.id
            ORDER BY activity_count DESC
        """
        )
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(["Mood ID", "Mood Name", "Activities Count"])
        for row in cursor.fetchall():
            cw.writerow([row["mood_id"], row["mood_name"], row["activity_count"]])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=moods_report.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    finally:
        conn.close()


@admin_bp.route("/export_summary_report")
@login_required
def export_summary_report():
    """Export comprehensive summary report"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Gather statistics
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM activities")
        total_activities = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM moods")
        total_moods = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM domains")
        total_domains = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) as total FROM users WHERE DATE(created_at) >= DATE('now', '-7 days')"
        )
        users_last_week = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) as total FROM users WHERE DATE(created_at) >= DATE('now', '-30 days')"
        )
        users_last_month = cursor.fetchone()["total"]

        # Create report
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(["MoodMatch Platform Summary Report"])
        cw.writerow(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        cw.writerow([])
        cw.writerow(["Metric", "Value"])
        cw.writerow(["Total Users", total_users])
        cw.writerow(["Total Activities", total_activities])
        cw.writerow(["Total Moods", total_moods])
        cw.writerow(["Total Domains", total_domains])
        cw.writerow(["New Users (Last 7 Days)", users_last_week])
        cw.writerow(["New Users (Last 30 Days)", users_last_month])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = (
            "attachment; filename=summary_report.csv"
        )
        output.headers["Content-type"] = "text/csv"
        return output
    finally:
        conn.close()


# ===============================
# VIEW ANALYTICS (ADD THIS TO YOUR admin.py)
# ===============================
@admin_bp.route("/view_analytics")
@login_required
def view_analytics():
    conn = get_db()
    cursor = conn.cursor()
    try:
        admins = get_admin_name(cursor)

        # ============================================
        # 1. ACTIVITY METRICS
        # ============================================

        # Most Recommended Activities (from user_history)
        cursor.execute(
            """
            SELECT 
                a.name,
                COUNT(uh.id) as recommendation_count
            FROM user_history uh
            JOIN activities a ON uh.activity_id = a.id
            GROUP BY uh.activity_id
            ORDER BY recommendation_count DESC
            LIMIT 10
        """
        )
        most_recommended = [dict(row) for row in cursor.fetchall()]

        # Most Favorited Activities
        cursor.execute(
            """
            SELECT 
                a.name,
                COUNT(f.id) as favorite_count
            FROM favorites f
            JOIN activities a ON f.activity_id = a.id
            GROUP BY f.activity_id
            ORDER BY favorite_count DESC
            LIMIT 10
        """
        )
        most_favorited = [dict(row) for row in cursor.fetchall()]

        # Activity Completion Rates (based on feedback_rating presence)
        cursor.execute(
            """
            SELECT 
                a.name,
                COUNT(CASE WHEN uh.feedback_rating IS NOT NULL THEN 1 END) as completed,
                COUNT(uh.id) as total,
                ROUND(CAST(COUNT(CASE WHEN uh.feedback_rating IS NOT NULL THEN 1 END) AS FLOAT) / COUNT(uh.id) * 100, 1) as completion_rate
            FROM user_history uh
            JOIN activities a ON uh.activity_id = a.id
            GROUP BY uh.activity_id
            HAVING total > 0
            ORDER BY completion_rate DESC
            LIMIT 10
        """
        )
        completion_rates = [dict(row) for row in cursor.fetchall()]

        # Activities by Category Usage
        cursor.execute(
            """
            SELECT 
                c.name as category_name,
                c.icon as category_icon,
                COUNT(uh.id) as usage_count
            FROM user_history uh
            JOIN activities a ON uh.activity_id = a.id
            JOIN categories c ON a.category_id = c.id
            GROUP BY c.id
            ORDER BY usage_count DESC
        """
        )
        category_usage = [dict(row) for row in cursor.fetchall()]

        # Prepare for Chart.js
        category_labels = [row["category_name"] for row in category_usage]
        category_counts = [row["usage_count"] for row in category_usage]

        # Least Used Activities (to improve/remove)
        cursor.execute(
            """
            SELECT 
                a.name,
                COALESCE(COUNT(uh.id), 0) as usage_count
            FROM activities a
            LEFT JOIN user_history uh ON a.id = uh.activity_id
            WHERE a.is_active = 1
            GROUP BY a.id
            ORDER BY usage_count ASC
            LIMIT 10
        """
        )
        least_used = [dict(row) for row in cursor.fetchall()]

        # ============================================
        # 2. MOOD ANALYTICS
        # ============================================

        # Mood Distribution (positive/negative/neutral based on sentiment_score)
        cursor.execute(
            """
            SELECT 
                CASE 
                    WHEN sentiment_score >= 0.2 THEN 'positive'
                    WHEN sentiment_score <= -0.2 THEN 'negative'
                    ELSE 'neutral'
                END as mood_type,
                COUNT(*) as count
            FROM user_history
            WHERE sentiment_score IS NOT NULL
            GROUP BY mood_type
        """
        )
        mood_dist = cursor.fetchall()
        mood_distribution = {"positive": 0, "negative": 0, "neutral": 0}
        for row in mood_dist:
            mood_distribution[row["mood_type"]] = row["count"]

        # Mood Trends Over Time (last 7 days)
        cursor.execute(
            """
            SELECT 
                DATE(created_at) as date,
                CASE 
                    WHEN sentiment_score >= 0.2 THEN 'positive'
                    WHEN sentiment_score <= -0.2 THEN 'negative'
                    ELSE 'neutral'
                END as mood_type,
                COUNT(*) as count
            FROM user_history
            WHERE created_at >= DATE('now', '-6 days')
            AND sentiment_score IS NOT NULL
            GROUP BY date, mood_type
            ORDER BY date ASC
        """
        )
        mood_trends_raw = cursor.fetchall()

        # Format for Chart.js (last 7 days)
        mood_trend_labels = []
        mood_trend_positive = []
        mood_trend_negative = []
        mood_trend_neutral = []

        for i in range(6, -1, -1):
            day = date.today() - timedelta(days=i)
            mood_trend_labels.append(day.strftime("%d %b"))

            day_data = {"positive": 0, "negative": 0, "neutral": 0}
            for row in mood_trends_raw:
                if row["date"] == day.isoformat():
                    day_data[row["mood_type"]] = row["count"]

            mood_trend_positive.append(day_data["positive"])
            mood_trend_negative.append(day_data["negative"])
            mood_trend_neutral.append(day_data["neutral"])

        # Most Common Mood Inputs (top mood keywords)
        cursor.execute(
            """
            SELECT 
                mood_input,
                COUNT(*) as frequency
            FROM user_history
            WHERE mood_input IS NOT NULL AND mood_input != ''
            GROUP BY mood_input
            ORDER BY frequency DESC
            LIMIT 10
        """
        )
        common_moods = [dict(row) for row in cursor.fetchall()]

        # Mood → Activity → Feedback Correlation
        cursor.execute(
            """
            SELECT 
                CASE 
                    WHEN sentiment_score >= 0.2 THEN 'Positive'
                    WHEN sentiment_score <= -0.2 THEN 'Negative'
                    ELSE 'Neutral'
                END as mood,
                a.name as activity,
                AVG(COALESCE(feedback_rating, 0)) as avg_rating,
                COUNT(*) as try_count
            FROM user_history uh
            JOIN activities a ON uh.activity_id = a.id
            WHERE sentiment_score IS NOT NULL
            GROUP BY mood, uh.activity_id
            HAVING try_count >= 2
            ORDER BY avg_rating DESC
            LIMIT 15
        """
        )
        mood_activity_correlation = [dict(row) for row in cursor.fetchall()]

        # ============================================
        # 3. ENGAGEMENT METRICS
        # ============================================

        # Average Activities Tried Per User
        cursor.execute(
            """
            SELECT 
                AVG(activity_count) as avg_activities
            FROM (
                SELECT user_id, COUNT(DISTINCT activity_id) as activity_count
                FROM user_history
                GROUP BY user_id
            )
        """
        )
        avg_activities_per_user = cursor.fetchone()["avg_activities"] or 0

        # Total User History Records
        cursor.execute("SELECT COUNT(*) as total FROM user_history")
        total_history_records = cursor.fetchone()["total"]

        # Feedback Ratings Distribution
        cursor.execute(
            """
            SELECT 
                feedback_rating,
                COUNT(*) as count
            FROM user_history
            WHERE feedback_rating IS NOT NULL
            GROUP BY feedback_rating
            ORDER BY feedback_rating DESC
        """
        )
        feedback_dist_raw = cursor.fetchall()
        feedback_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for row in feedback_dist_raw:
            feedback_distribution[row["feedback_rating"]] = row["count"]

        # Average Feedback Rating
        cursor.execute(
            """
            SELECT AVG(feedback_rating) as avg_rating
            FROM user_history
            WHERE feedback_rating IS NOT NULL
        """
        )
        avg_feedback_rating = cursor.fetchone()["avg_rating"] or 0

        # ============================================
        # 4. INTEREST ANALYTICS
        # ============================================

        # Top 10 Interests (same as dashboard)
        cursor.execute(
            """
            SELECT 
                i.name as interest_name,
                COUNT(DISTINCT ui.user_id) as user_count
            FROM interests i
            LEFT JOIN user_interests ui ON i.id = ui.interest_id
            GROUP BY i.id, i.name
            HAVING user_count > 0
            ORDER BY user_count DESC
            LIMIT 10
        """
        )
        top_interests = [dict(row) for row in cursor.fetchall()]

        # Interest Category Distribution
        cursor.execute(
            """
            SELECT 
                ic.name as category_name,
                COUNT(DISTINCT ui.user_id) as user_count
            FROM interest_categories ic
            JOIN interests i ON ic.id = i.category_id
            LEFT JOIN user_interests ui ON i.id = ui.interest_id
            GROUP BY ic.id
            ORDER BY user_count DESC
        """
        )
        interest_category_dist = [dict(row) for row in cursor.fetchall()]

        # Interests vs Activities Correlation (which interests lead to more activity usage)
        cursor.execute(
            """
            SELECT 
                i.name as interest_name,
                COUNT(DISTINCT uh.id) as activity_tries
            FROM interests i
            JOIN user_interests ui ON i.id = ui.interest_id
            JOIN user_history uh ON ui.user_id = uh.user_id
            GROUP BY i.id
            ORDER BY activity_tries DESC
            LIMIT 10
        """
        )
        interest_activity_correlation = [dict(row) for row in cursor.fetchall()]

        # ============================================
        # 5. RECENT ACTIVITY FEED (Last 20 activities)
        # ============================================

        recent_activities = []

        # Get recent user registrations
        cursor.execute(
            """
            SELECT 
                'user_registered' as activity_type,
                first_name || ' ' || last_name as user_name,
                username,
                created_at as timestamp
            FROM users
            ORDER BY created_at DESC
            LIMIT 10
        """
        )
        recent_activities.extend([dict(row) for row in cursor.fetchall()])

        # Get recent activity additions/updates
        cursor.execute(
            """
            SELECT 
                'activity_added' as activity_type,
                name as activity_name,
                created_at as timestamp
            FROM activities
            ORDER BY created_at DESC
            LIMIT 10
        """
        )
        recent_activities.extend([dict(row) for row in cursor.fetchall()])

        # Get recent user activity tries
        cursor.execute(
            """
            SELECT 
                'activity_tried' as activity_type,
                u.first_name || ' ' || u.last_name as user_name,
                a.name as activity_name,
                uh.created_at as timestamp
            FROM user_history uh
            JOIN users u ON uh.user_id = u.id
            JOIN activities a ON uh.activity_id = a.id
            ORDER BY uh.created_at DESC
            LIMIT 10
        """
        )
        recent_activities.extend([dict(row) for row in cursor.fetchall()])

        # Sort all recent activities by timestamp
        recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activities = recent_activities[:20]  # Keep only top 20

        return render_template(
            "admin/view_analytics.html",
            admins=admins,
            # Activity Metrics
            most_recommended=most_recommended,
            most_favorited=most_favorited,
            completion_rates=completion_rates,
            category_labels=category_labels,
            category_counts=category_counts,
            least_used=least_used,
            # Mood Analytics
            mood_distribution=mood_distribution,
            mood_trend_labels=mood_trend_labels,
            mood_trend_positive=mood_trend_positive,
            mood_trend_negative=mood_trend_negative,
            mood_trend_neutral=mood_trend_neutral,
            common_moods=common_moods,
            mood_activity_correlation=mood_activity_correlation,
            # Engagement Metrics
            avg_activities_per_user=round(avg_activities_per_user, 1),
            total_history_records=total_history_records,
            feedback_distribution=feedback_distribution,
            avg_feedback_rating=round(avg_feedback_rating, 2),
            # Interest Analytics
            top_interests=top_interests,
            interest_category_dist=interest_category_dist,
            interest_activity_correlation=interest_activity_correlation,
            # Recent Activity Feed
            recent_activities=recent_activities,
        )
    finally:
        conn.close()


# ===============================
# Admin Profile
# ===============================
@admin_bp.route("/admin_profile")
@login_required
def admin_profile():
    conn = get_db()
    cursor = conn.cursor()
    try:
        admins = get_admin_name(cursor)

        # Get admin details
        cursor.execute("SELECT * FROM admins LIMIT 1")
        row = cursor.fetchone()
        admin = dict(row) if row else None

        # Stats for activity summary
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM activities")
        total_activities = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM categories")
        total_categories = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_history")
        total_history = cursor.fetchone()[0]

        return render_template(
            "admin/admin_profile.html",
            admins=admins,
            admin=admin,
            total_users=total_users,
            total_activities=total_activities,
            total_categories=total_categories,
            total_history=total_history,
        )
    finally:
        conn.close()


# ===============================
# Admin Settings
# ===============================
@admin_bp.route("/admin_settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        try:
            # Update Profile
            if action == "update_profile":
                username = request.form.get("username", "").strip()
                email = request.form.get("email", "").strip()

                if username:
                    cursor.execute(
                        "UPDATE admins SET username = ?, email = ? WHERE id = 1",
                        (username, email),
                    )
                    conn.commit()
                    flash("Profile updated successfully!", "success")
                else:
                    flash("Username cannot be empty", "error")

            # Change Password
            elif action == "change_password":
                current_pwd = request.form.get("current_password")
                new_pwd = request.form.get("new_password")
                confirm_pwd = request.form.get("confirm_password")

                # Verify current password
                cursor.execute("SELECT password FROM admins WHERE id = 1")
                db_pwd = cursor.fetchone()[0]

                if current_pwd != db_pwd:
                    flash("Current password is incorrect", "error")
                elif new_pwd != confirm_pwd:
                    flash("New passwords do not match", "error")
                elif len(new_pwd) < 6:
                    flash("Password must be at least 6 characters", "error")
                else:
                    cursor.execute(
                        "UPDATE admins SET password = ? WHERE id = 1", (new_pwd,)
                    )
                    conn.commit()
                    flash("Password changed successfully!", "success")

        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        finally:
            conn.close()
            return redirect(url_for("admin.admin_settings"))

    # GET request
    try:
        admins = get_admin_name(cursor)
        cursor.execute("SELECT * FROM admins LIMIT 1")
        row = cursor.fetchone()
        admin = dict(row) if row else None

        return render_template(
            "admin/admin_settings.html", admins=admins, admin=admin, last_backup="Never"
        )
    finally:
        conn.close()


# Add these imports at the top of admin.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ===============================
# Generate Reports
# ===============================
@admin_bp.route("/generate_reports", methods=["GET", "POST"])
@login_required
def generate_reports():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        report_type = request.form.get("report_type")
        format_type = request.form.get("format")

        try:
            # Users Report
            if report_type == "users":
                cursor.execute(
                    """
                    SELECT id, username, first_name, last_name, email, phone_number, 
                           gender, date_of_birth, created_at, city, state, country
                    FROM users ORDER BY created_at DESC
                """
                )
                data = cursor.fetchall()
                headers = [
                    "ID",
                    "Username",
                    "First Name",
                    "Last Name",
                    "Email",
                    "Phone",
                    "Gender",
                    "DOB",
                    "Registered",
                    "City",
                    "State",
                    "Country",
                ]
                filename = "users_database"
                title = "Users Database Report"

            # User Interests Report
            elif report_type == "interests":
                cursor.execute(
                    """
                    SELECT i.name as interest, COUNT(ui.user_id) as user_count
                    FROM interests i
                    LEFT JOIN user_interests ui ON i.id = ui.interest_id
                    GROUP BY i.id, i.name
                    ORDER BY user_count DESC
                """
                )
                data = cursor.fetchall()
                headers = ["Interest", "User Count"]
                filename = "user_interests"
                title = "User Interests Report"

            # Activities Report
            elif report_type == "activities":
                cursor.execute(
                    """
                    SELECT a.id, a.name, c.name as category, a.execution_type, 
                           a.mood_tags, a.priority, a.is_active, a.created_at
                    FROM activities a
                    LEFT JOIN categories c ON a.category_id = c.id
                    ORDER BY a.created_at DESC
                """
                )
                data = cursor.fetchall()
                headers = [
                    "ID",
                    "Activity",
                    "Category",
                    "Type",
                    "Mood Tags",
                    "Priority",
                    "Active",
                    "Created",
                ]
                filename = "activities_tasks"
                title = "Activities & Tasks Report"

            # Categories Report
            elif report_type == "categories":
                cursor.execute(
                    """
                    SELECT id, name, icon, description, created_at
                    FROM categories ORDER BY name
                """
                )
                data = cursor.fetchall()
                headers = ["ID", "Name", "Icon", "Description", "Created"]
                filename = "categories_overview"
                title = "Categories Overview Report"

            # Activity Analytics Report
            elif report_type == "activity_analytics":
                cursor.execute(
                    """
                    SELECT a.name, 
                           COUNT(uh.id) as tries,
                           COUNT(DISTINCT uh.user_id) as unique_users,
                           AVG(COALESCE(uh.feedback_rating, 0)) as avg_rating,
                           SUM(CASE WHEN uh.completion_status = 'completed' THEN 1 ELSE 0 END) as completed
                    FROM activities a
                    LEFT JOIN user_history uh ON a.id = uh.activity_id
                    GROUP BY a.id, a.name
                    ORDER BY tries DESC
                """
                )
                data = cursor.fetchall()
                headers = [
                    "Activity",
                    "Total Tries",
                    "Unique Users",
                    "Avg Rating",
                    "Completed",
                ]
                filename = "activity_analytics"
                title = "Activity Analytics Report"

            # Platform Summary Report
            elif report_type == "platform":
                cursor.execute("SELECT COUNT(*) as total FROM users")
                total_users = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM activities")
                total_activities = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM categories")
                total_categories = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM user_history")
                total_history = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE('now', '-30 days')"
                )
                new_users_30d = cursor.fetchone()[0]

                data = [
                    ["Total Users", total_users],
                    ["Total Activities", total_activities],
                    ["Total Categories", total_categories],
                    ["Total Interactions", total_history],
                    ["New Users (30d)", new_users_30d],
                ]
                headers = ["Metric", "Value"]
                filename = "platform_summary"
                title = "Platform Summary Report"

            # Mood Analytics Report
            elif report_type == "mood_analytics":
                cursor.execute(
                    """
                    SELECT 
                        CASE 
                            WHEN sentiment_score >= 0.2 THEN 'Positive'
                            WHEN sentiment_score <= -0.2 THEN 'Negative'
                            ELSE 'Neutral'
                        END as mood,
                        COUNT(*) as count,
                        AVG(sentiment_score) as avg_score
                    FROM user_history
                    WHERE sentiment_score IS NOT NULL
                    GROUP BY mood
                """
                )
                data = cursor.fetchall()
                headers = ["Mood", "Count", "Avg Score"]
                filename = "mood_analytics"
                title = "Mood Analytics Report"

            # Feedback Report
            elif report_type == "feedback":
                cursor.execute(
                    """
                    SELECT feedback_rating, COUNT(*) as count
                    FROM user_history
                    WHERE feedback_rating IS NOT NULL
                    GROUP BY feedback_rating
                    ORDER BY feedback_rating DESC
                """
                )
                data = cursor.fetchall()
                headers = ["Rating", "Count"]
                filename = "feedback_report"
                title = "Feedback Report"

            else:
                flash("Invalid report type", "error")
                return redirect(url_for("admin.generate_reports"))

            # Generate PDF
            if format_type == "pdf":
                from io import BytesIO

                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()

                # Title
                title_style = ParagraphStyle(
                    "CustomTitle",
                    parent=styles["Heading1"],
                    fontSize=24,
                    textColor=colors.HexColor("#be123c"),
                    alignment=TA_CENTER,
                    spaceAfter=30,
                )
                elements.append(Paragraph(title, title_style))
                elements.append(Spacer(1, 0.3 * inch))

                # Table
                table_data = [headers]
                for row in data:
                    table_data.append(
                        [str(val) if val is not None else "N/A" for val in row]
                    )

                table = Table(table_data, repeatRows=1)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#be123c")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 11),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )

                elements.append(table)
                doc.build(elements)

                buffer.seek(0)
                response = make_response(buffer.getvalue())
                response.headers["Content-Type"] = "application/pdf"
                response.headers["Content-Disposition"] = (
                    f"attachment; filename={filename}.pdf"
                )
                return response

            # Generate CSV
            elif format_type == "csv":
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(headers)
                for row in data:
                    writer.writerow(row)

                response = make_response(output.getvalue())
                response.headers["Content-Type"] = "text/csv"
                response.headers["Content-Disposition"] = (
                    f"attachment; filename={filename}.csv"
                )
                return response

        except Exception as e:
            flash(f"Error generating report: {str(e)}", "error")
            return redirect(url_for("admin.generate_reports"))
        finally:
            if conn:
                conn.close()

    # GET request - show the page
    try:
        admins = get_admin_name(cursor)

        # Get stats
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM activities")
        total_activities = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM categories")
        total_categories = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_history")
        total_history = cursor.fetchone()[0]

        return render_template(
            "admin/generate_reports.html",
            admins=admins,
            total_users=total_users,
            total_activities=total_activities,
            total_categories=total_categories,
            total_history=total_history,
        )
    finally:
        conn.close()
