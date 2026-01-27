"""
MoodMatch - User Routes
Clean Flask route definitions for rendering user templates.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash,
)
from flask_login import login_required, current_user
import sqlite3
from datetime import datetime

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
# PAGE ROUTES (Template Rendering)
# ===============================


@user_bp.route("/user_dashboard")
@login_required
def user_dashboard():
    """Render the main user dashboard"""
    return render_template("user/user_dashboard.html")


# @user_bp.route("/activity/search", methods=["GET"])
# @login_required
# def activity_search():
#     """Render the activity search / recommendation input page"""
#     return render_template("user/activity_search.html")


# @user_bp.route("/recommend/results", methods=["GET", "POST"])
# @login_required
# def recommend_results():
#     """Render the recommendation results page"""
#     return render_template("user/recommend_results.html")


# # ─── Editor ────────────────────────────────────────────────


# @user_bp.route("/editor")
# @login_required
# def editor():
#     """Legacy / basic writing editor page"""
#     return render_template("user/editor.html")


# @user_bp.route("/editor/new-page")
# @login_required
# def editor_new_page():
#     """Page for creating a new writing"""
#     return render_template("user/editor_new.html")


# @user_bp.route("/editor/list-page")
# @login_required
# def editor_list_page():
#     """Render list of user's writings"""
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         SELECT id, title, content, created_at, updated_at
#         FROM user_writings
#         WHERE user_id = ?
#         ORDER BY COALESCE(updated_at, created_at) DESC
#     """,
#         (current_user.id,),
#     )

#     writings = [dict(row) for row in cur.fetchall()]
#     conn.close()

#     return render_template("user/editor_list.html", writings=writings)


# @user_bp.route("/editor/<int:writing_id>/page")
# @login_required
# def get_writing_page(writing_id):
#     """View a single writing"""
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         SELECT id, title, content, created_at, updated_at
#         FROM user_writings
#         WHERE id = ? AND user_id = ?
#     """,
#         (writing_id, current_user.id),
#     )

#     row = cur.fetchone()
#     conn.close()

#     if not row:
#         flash("Writing not found or you don't have permission to view it.", "error")
#         return redirect(url_for("user.editor_list_page"))

#     return render_template("user/editor_view.html", writing=dict(row))


# @user_bp.route("/editor/<int:writing_id>/edit-page")
# @login_required
# def edit_writing_page(writing_id):
#     """Edit a single writing"""
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         SELECT id, title, content, created_at, updated_at
#         FROM user_writings
#         WHERE id = ? AND user_id = ?
#     """,
#         (writing_id, current_user.id),
#     )

#     row = cur.fetchone()
#     conn.close()

#     if not row:
#         flash("Writing not found or you don't have permission to edit it.", "error")
#         return redirect(url_for("user.editor_list_page"))

#     return render_template("user/editor_update.html", writing=dict(row))


# @user_bp.route("/reading")
# @login_required
# def reading():
#     return render_template("user/reading.html")


# @user_bp.route("/cooking")
# @login_required
# def cooking():
#     return render_template("user/cooking.html")


# @user_bp.route("/game")
# @login_required
# def game():
#     return render_template("user/game.html")


# @user_bp.route("/travel")
# @login_required
# def travel():
#     return render_template("user/travel.html")


# @user_bp.route("/favorites")
# @login_required
# def favorites():
#     return render_template("user/favorites.html")


# @user_bp.route("/history")
# @login_required
# def history():
#     return render_template("user/history.html")


# # ===============================
# # API / ACTION ROUTES
# # ===============================


# @user_bp.route("/activities")
# @login_required
# def activities_page():
#     """Render activities selection page"""
#     return render_template("user/activities.html", user=current_user)


# @user_bp.route("/recommend", methods=["POST"])
# @login_required
# def recommend_activity():
#     """
#     Process recommendation request and redirect to appropriate page
#     """
#     if request.is_json:
#         data = request.get_json()
#     else:
#         data = request.form.to_dict()

#     if not data or "mood_id" not in data:
#         flash("Please select a mood.", "error")
#         return redirect(url_for("user.activities_page"))

#     mood_id = data["mood_id"]

#     conn = get_db()
#     cur = conn.cursor()

#     query = """
#         SELECT
#             a.id,
#             a.name,
#             a.execution_type,
#             a.description,
#             (am.weight * 10 + a.priority) AS score
#         FROM activities a
#         JOIN activity_moods am ON a.id = am.activity_id
#         JOIN activity_filters af ON a.id = af.activity_id
#         WHERE a.is_active = 1
#           AND am.mood_id = ?
#     """
#     params = [mood_id]

#     if data.get("energy_level"):
#         query += " AND af.energy_level = ?"
#         params.append(data["energy_level"])

#     if data.get("location_type"):
#         query += " AND af.location_type IN (?, 'Both')"
#         params.append(data["location_type"])

#     if data.get("distance_type"):
#         query += " AND af.distance_type = ?"
#         params.append(data["distance_type"])

#     if data.get("social_type"):
#         query += " AND af.social_type IN (?, 'Both')"
#         params.append(data["social_type"])

#     if data.get("time") is not None:
#         query += " AND af.min_time <= ? AND af.max_time >= ?"
#         params.extend([data["time"], data["time"]])

#     query += " ORDER BY score DESC LIMIT 10"

#     cur.execute(query, params)
#     results = [dict(row) for row in cur.fetchall()]
#     conn.close()

#     if not results:
#         flash("No matching activities found for your mood and filters.", "warning")
#         return redirect(url_for("user.activity_search"))

#     # For now we take the top result
#     top = results[0]
#     session["recommended_activity"] = top

#     # Map execution_type → route (you may need to adjust these)
#     route_map = {
#         "writing": "user.editor_new_page",
#         "reading": "user.reading",
#         "cooking": "user.cooking",
#         "game": "user.game",
#         "travel": "user.travel",
#     }

#     target = route_map.get(top["execution_type"].lower(), "user.recommend_results")

#     flash(f"Recommended: {top['name']}", "success")
#     return redirect(url_for(target))


# # ─── Editor API Endpoints ───────────────────────────────────


# @user_bp.route("/editor/save", methods=["POST"])
# # @login_required
# def save_writing():
#     print(">>>Writing Saved!!!<<<")
#     data = request.get_json(silent=True) or {}
#     if "content" not in data or not data["content"].strip():
#         return jsonify({"error": "Content is required"}), 400

#     conn = get_db()
#     cur = conn.cursor()

#     now = datetime.utcnow().isoformat()

#     cur.execute(
#         """
#         INSERT INTO user_writings
#             (user_id, activity_id, title, content, created_at, updated_at)
#         VALUES (?, ?, ?, ?, ?, ?)
#     """,
#         (
#             current_user.id,
#             data.get("activity_id", 1),  # assuming 1 = writing activity
#             data.get("title"),
#             data["content"],
#             now,
#             now,
#         ),
#     )

#     conn.commit()
#     conn.close()

#     return jsonify({"message": "Writing saved"}), 201


# @user_bp.route("/editor/update", methods=["PUT"])
# @login_required
# def update_writing():
#     data = request.get_json(silent=True) or {}
#     writing_id = data.get("writing_id")
#     if not writing_id or "content" not in data:
#         return jsonify({"error": "writing_id and content required"}), 400

#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         SELECT 1 FROM user_writings
#         WHERE id = ? AND user_id = ?
#     """,
#         (writing_id, current_user.id),
#     )

#     if not cur.fetchone():
#         conn.close()
#         return jsonify({"error": "Not found or not authorized"}), 403

#     now = datetime.utcnow().isoformat()

#     cur.execute(
#         """
#         UPDATE user_writings
#         SET title = ?, content = ?, updated_at = ?
#         WHERE id = ? AND user_id = ?
#     """,
#         (data.get("title"), data["content"], now, writing_id, current_user.id),
#     )

#     conn.commit()
#     conn.close()

#     return jsonify({"message": "Updated successfully"})


# @user_bp.route("/editor/delete", methods=["DELETE"])
# @login_required
# def delete_writing():
#     data = request.get_json(silent=True) or {}
#     writing_id = data.get("writing_id")
#     if not writing_id:
#         return jsonify({"error": "writing_id required"}), 400

#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         DELETE FROM user_writings
#         WHERE id = ? AND user_id = ?
#     """,
#         (writing_id, current_user.id),
#     )

#     if cur.rowcount == 0:
#         conn.close()
#         return jsonify({"error": "Not found or not authorized"}), 403

#     conn.commit()
#     conn.close()

#     return jsonify({"message": "Deleted successfully"})


# @user_bp.route("/editor/list", methods=["GET"])
# @login_required
# def list_writings():
#     """JSON list of writings – used by frontend"""
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         SELECT id, title, content, created_at, updated_at
#         FROM user_writings
#         WHERE user_id = ?
#         ORDER BY COALESCE(updated_at, created_at) DESC
#     """,
#         (current_user.id,),
#     )

#     rows = cur.fetchall()
#     conn.close()

#     return jsonify([dict(r) for r in rows])


# @user_bp.route("/editor/<int:writing_id>", methods=["GET"])
# @login_required
# def get_writing(writing_id):
#     """JSON – single writing"""
#     conn = get_db()
#     cur = conn.cursor()

#     cur.execute(
#         """
#         SELECT id, title, content, created_at, updated_at
#         FROM user_writings
#         WHERE id = ? AND user_id = ?
#     """,
#         (writing_id, current_user.id),
#     )

#     row = cur.fetchone()
#     conn.close()

#     if not row:
#         return jsonify({"error": "Not found"}), 404

#     return jsonify(dict(row))
