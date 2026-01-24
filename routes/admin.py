from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
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
    return render_template("admin/admin_dashboard.html")


# ===============================
# Manage Activities (CRUD)
# ===============================
@admin_bp.route("/manage_activity", methods=["GET", "POST", "PUT", "PATCH"])
@login_required
def manage_activity():
    conn = get_db()
    cur = conn.cursor()

    # ---------- GET : list activities ----------
    if request.method == "GET":
        cur.execute(
            """
            SELECT id, name, execution_type, is_active, priority, created_at
            FROM activities
            ORDER BY priority DESC, created_at DESC
        """
        )
        data = [dict(row) for row in cur.fetchall()]
        conn.close()
        return jsonify(data)

    data = request.get_json(silent=True)

    # ---------- POST : create activity ----------
    if request.method == "POST":
        cur.execute(
            """
            INSERT INTO activities (name, execution_type, description, priority)
            VALUES (?, ?, ?, ?)
        """,
            (
                data["name"],
                data["execution_type"],
                data.get("description"),
                data.get("priority", 0),
            ),
        )

        activity_id = cur.lastrowid

        # domains
        for domain_id in data.get("domain_ids", []):
            cur.execute(
                """
                INSERT INTO activity_domains (activity_id, domain_id)
                VALUES (?, ?)
            """,
                (activity_id, domain_id),
            )

        # moods
        for mood in data.get("moods", []):
            cur.execute(
                """
                INSERT INTO activity_moods (activity_id, mood_id, weight)
                VALUES (?, ?, ?)
            """,
                (activity_id, mood["mood_id"], mood["weight"]),
            )

        # filters
        cur.execute(
            """
            INSERT INTO activity_filters (
                activity_id, min_time, max_time,
                min_budget, max_budget,
                energy_level, location_type,
                distance_type, social_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        conn.close()
        return jsonify({"message": "Activity created"}), 201

    # ---------- PUT : update activity ----------
    if request.method == "PUT":
        activity_id = data["activity_id"]

        cur.execute(
            """
            UPDATE activities
            SET name = ?, execution_type = ?, description = ?, priority = ?
            WHERE id = ?
        """,
            (
                data["name"],
                data["execution_type"],
                data.get("description"),
                data.get("priority", 0),
                activity_id,
            ),
        )

        # reset domains
        cur.execute(
            "DELETE FROM activity_domains WHERE activity_id = ?", (activity_id,)
        )
        for domain_id in data.get("domain_ids", []):
            cur.execute(
                """
                INSERT INTO activity_domains (activity_id, domain_id)
                VALUES (?, ?)
            """,
                (activity_id, domain_id),
            )

        # reset moods
        cur.execute("DELETE FROM activity_moods WHERE activity_id = ?", (activity_id,))
        for mood in data.get("moods", []):
            cur.execute(
                """
                INSERT INTO activity_moods (activity_id, mood_id, weight)
                VALUES (?, ?, ?)
            """,
                (activity_id, mood["mood_id"], mood["weight"]),
            )

        # update filters
        cur.execute(
            """
            UPDATE activity_filters
            SET min_time=?, max_time=?,
                min_budget=?, max_budget=?,
                energy_level=?, location_type=?,
                distance_type=?, social_type=?
            WHERE activity_id=?
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
        conn.close()
        return jsonify({"message": "Activity updated"})

    # ---------- PATCH : enable / disable ----------
    if request.method == "PATCH":
        cur.execute(
            """
            UPDATE activities
            SET is_active = ?
            WHERE id = ?
        """,
            (data["is_active"], data["activity_id"]),
        )

        conn.commit()
        conn.close()
        return jsonify({"message": "Activity status updated"})
