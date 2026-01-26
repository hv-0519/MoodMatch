"""
MoodMatch - User Routes
Clean Flask route definitions for rendering user templates.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import login_required, current_user
import sqlite3

user_bp = Blueprint("user", __name__)

DB_PATH = "models/mood.db"


# ===============================
# DB helper
# ===============================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ===============================
# PAGE ROUTES (Template Rendering Only)
# ===============================

@user_bp.route("/user_dashboard")
@login_required
def user_dashboard():
    """Render the main user dashboard"""
    return render_template("user/user_dashboard.html")


@user_bp.route("/activity/search")
@login_required
def activity_search():
    """Render the activity search page"""
    return render_template("user/activity_search.html")


@user_bp.route("/recommend/results", methods=["GET", "POST"])
@login_required
def recommend_results():
    """Render the recommendation results page"""
    return render_template("user/recommend_results.html")


@user_bp.route("/editor")
@login_required
def editor():
    """Render the writing editor page"""
    return render_template("user/editor.html")


@user_bp.route("/reading")
@login_required
def reading():
    """Render the reading resources page"""
    return render_template("user/reading.html")


@user_bp.route("/cooking")
@login_required
def cooking():
    """Render the cooking recipes page"""
    return render_template("user/cooking.html")


@user_bp.route("/game")
@login_required
def game():
    """Render the games page"""
    return render_template("user/game.html")


@user_bp.route("/travel")
@login_required
def travel():
    """Render the travel destinations page"""
    return render_template("user/travel.html")


@user_bp.route("/favorites")
@login_required
def favorites():
    """Render the favorites page"""
    return render_template("user/favorites.html")


@user_bp.route("/history")
@login_required
def history():
    """Render the activity history page"""
    return render_template("user/history.html")


# ===============================
# EXISTING API ROUTES (Keep as-is)
# ===============================

@user_bp.route("/activities")
@login_required
def activities_page():
    """Render the activities selection page"""
    return render_template("user/activities.html", user=current_user)


@user_bp.route("/recommend", methods=["POST"])
@login_required
def recommend_activity():
    """
    UPDATED: Now redirects to activity page instead of returning JSON
    Can be called with form data or JSON
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    if not data or "mood_id" not in data:
        flash("Please provide mood information", "error")
        return redirect(url_for("user.activities_page"))

    mood_id = data["mood_id"]

    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT
            a.id,
            a.name,
            a.execution_type,
            a.description,
            (am.weight * 10 + a.priority) AS score
        FROM activities a
        JOIN activity_moods am ON a.id = am.activity_id
        JOIN activity_filters af ON a.id = af.activity_id
        WHERE a.is_active = 1
          AND am.mood_id = ?
    """
    params = [mood_id]

    if data.get("energy_level"):
        query += " AND af.energy_level = ?"
        params.append(data["energy_level"])

    if data.get("location_type"):
        query += " AND af.location_type IN (?, 'Both')"
        params.append(data["location_type"])

    if data.get("distance_type"):
        query += " AND af.distance_type = ?"
        params.append(data["distance_type"])

    if data.get("social_type"):
        query += " AND af.social_type IN (?, 'Both')"
        params.append(data["social_type"])

    if data.get("time") is not None:
        query += " AND af.min_time <= ? AND af.max_time >= ?"
        params.extend([data["time"], data["time"]])

    query += " ORDER BY score DESC LIMIT 10"

    cur.execute(query, params)
    results = [dict(row) for row in cur.fetchall()]
    conn.close()

    if not results:
        flash("No matching activities found. Try a different mood or filters!", "warning")
        return redirect(url_for("user.activities_page"))

    top_activity = results[0]
    execution_type = top_activity["execution_type"]

    session["recommended_activity"] = top_activity

    route_map = {
        "writing": "activities.writing_editor",
        "reading": "activities.reading_resources",
        "cooking": "activities.cooking_steps",
        "games": "activities.games_details",
        "travel": "activities.travel_places",
    }

    target_route = route_map.get(execution_type, "user.user_dashboard")

    flash(f"We found the perfect activity for you: {top_activity['name']}!", "success")
    return redirect(url_for(target_route))


@user_bp.route("/api/recommend", methods=["POST"])
@login_required
def api_recommend_activity():
    """JSON API endpoint for getting recommendations"""
    data = request.get_json(silent=True)

    if not data or "mood_id" not in data:
        return jsonify({"error": "mood_id required"}), 400

    mood_id = data["mood_id"]

    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT
            a.id,
            a.name,
            a.execution_type,
            a.description,
            (am.weight * 10 + a.priority) AS score
        FROM activities a
        JOIN activity_moods am ON a.id = am.activity_id
        JOIN activity_filters af ON a.id = af.activity_id
        WHERE a.is_active = 1
          AND am.mood_id = ?
    """
    params = [mood_id]

    if data.get("energy_level"):
        query += " AND af.energy_level = ?"
        params.append(data["energy_level"])

    if data.get("location_type"):
        query += " AND af.location_type IN (?, 'Both')"
        params.append(data["location_type"])

    if data.get("distance_type"):
        query += " AND af.distance_type = ?"
        params.append(data["distance_type"])

    if data.get("social_type"):
        query += " AND af.social_type IN (?, 'Both')"
        params.append(data["social_type"])

    if data.get("time") is not None:
        query += " AND af.min_time <= ? AND af.max_time >= ?"
        params.extend([data["time"], data["time"]])

    query += " ORDER BY score DESC LIMIT 10"

    cur.execute(query, params)
    results = [dict(row) for row in cur.fetchall()]
    conn.close()

    return jsonify(results)


# ===============================
# EDITOR API ROUTES
# ===============================

@user_bp.route("/editor/save", methods=["POST"])
@login_required
def save_writing():
    data = request.get_json(silent=True)

    if not data or "activity_id" not in data or "content" not in data:
        return jsonify({"error": "activity_id and content required"}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO user_writings (user_id, activity_id, title, content)
        VALUES (?, ?, ?, ?)
        """,
        (
            current_user.id,
            data["activity_id"],
            data.get("title"),
            data["content"],
        ),
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Writing saved"}), 201


@user_bp.route("/editor/update", methods=["PUT"])
@login_required
def update_writing():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    writing_id = data.get("writing_id")
    content = data.get("content")

    if not writing_id or not content:
        return jsonify({"error": "writing_id and content required"}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id FROM user_writings
        WHERE id = ? AND user_id = ?
        """,
        (writing_id, current_user.id),
    )

    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Not authorized or writing not found"}), 403

    cur.execute(
        """
        UPDATE user_writings
        SET title = ?, content = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            data.get("title"),
            content,
            writing_id,
            current_user.id,
        ),
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Writing updated successfully"})


@user_bp.route("/editor/delete", methods=["DELETE"])
@login_required
def delete_writing():
    data = request.get_json(silent=True)

    if not data or "writing_id" not in data:
        return jsonify({"error": "writing_id required"}), 400

    writing_id = data["writing_id"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id FROM user_writings
        WHERE id = ? AND user_id = ?
        """,
        (writing_id, current_user.id),
    )

    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Not authorized or writing not found"}), 403

    cur.execute(
        "DELETE FROM user_writings WHERE id = ? AND user_id = ?",
        (writing_id, current_user.id),
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Writing deleted successfully"})


@user_bp.route("/editor/list", methods=["GET"])
@login_required
def list_writings():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, title, content
        FROM user_writings
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (current_user.id,),
    )

    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@user_bp.route("/editor/<int:writing_id>", methods=["GET"])
@login_required
def get_writing(writing_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, title, content
        FROM user_writings
        WHERE id = ? AND user_id = ?
        """,
        (writing_id, current_user.id),
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Not found"}), 404

    return jsonify(dict(row))
