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
    try:
        admins = get_admin_name(cursor)

        # Stats
        cursor.execute("SELECT COUNT(*) from users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM activities")
        total_activities = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')"
        )
        registered_today = cursor.fetchone()[0]

        # Growth Chart
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

        # Mood Chart
        cursor.execute(
            """
            SELECT m.name, COUNT(am.activity_id) as count FROM moods m
            JOIN activity_moods am ON m.id = am.mood_id
            GROUP BY m.name ORDER BY count DESC LIMIT 5
        """
        )
        mood_rows = cursor.fetchall()
        mood_labels = [r[0] for r in mood_rows]
        mood_data = [r[1] for r in mood_rows]

        cursor.execute(
            "SELECT id, username, email, created_at FROM users ORDER BY created_at DESC LIMIT 5"
        )
        users = [dict(row) for row in cursor.fetchall()]

        return render_template(
            "admin/admin_dashboard.html",
            admins=admins,
            total_users=total_users,
            total_activities=total_activities,
            registered_today=registered_today,
            users=users,
            chart_labels=chart_labels,
            chart_data=chart_data,
            mood_labels=mood_labels,
            mood_data=mood_data,
            mood_colors=["#8ec5fc", "#e0c3fc", "#a8d5fc", "#ead5fc", "#cbd5e1"],
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
# Manage Activities (CRUD)
# ===============================
@admin_bp.route("/manage_activity", methods=["GET", "POST"])
@login_required
def manage_activity():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "add":
                name = request.form.get("name", "").strip()
                ex_type = request.form.get("execution_type", "").strip()
                desc = request.form.get("description", "").strip()
                prio = int(request.form.get("priority") or 0)

                if name and ex_type:
                    cursor.execute(
                        """
                        INSERT INTO activities (name, execution_type, description, priority, is_active)
                        VALUES (?, ?, ?, ?, 1)
                    """,
                        (name, ex_type, desc, prio),
                    )
                    conn.commit()
                    flash("Activity added successfully!", "success")

            elif action == "edit":
                act_id = request.form.get("activity_id")
                name = request.form.get("name", "").strip()
                ex_type = request.form.get("execution_type", "").strip()
                desc = request.form.get("description", "").strip()
                prio = int(request.form.get("priority") or 0)

                cursor.execute(
                    """
                    UPDATE activities SET name=?, execution_type=?, description=?, priority=?
                    WHERE id=?
                """,
                    (name, ex_type, desc, prio, act_id),
                )
                conn.commit()
                flash("Activity updated successfully!", "success")

            elif action == "delete":
                act_id = request.form.get("activity_id")
                cursor.execute("DELETE FROM activities WHERE id=?", (act_id,))
                conn.commit()
                flash("Activity deleted successfully!", "success")

        except sqlite3.Error as e:
            conn.rollback()
            flash(f"Database error: {str(e)}", "error")
        finally:
            conn.close()
        return redirect(url_for("admin.manage_activity"))

    # GET Request
    try:
        admins = get_admin_name(cursor)
        cursor.execute("SELECT * FROM activities ORDER BY created_at DESC")
        activities_list = [dict(row) for row in cursor.fetchall()]

        # Adding a UI display ID (sequential number)
        for i, item in enumerate(activities_list, start=1):
            item["ui_id"] = i

        return render_template(
            "admin/manage_activities.html", activities=activities_list, admins=admins
        )
    finally:
        conn.close()


# ===============================
# Reports
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
