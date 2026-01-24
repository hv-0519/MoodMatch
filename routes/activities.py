"""
MoodMatch - Activities Blueprint
Handles all activity execution pages (Writing, Reading, Cooking, Games, Travel)
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from flask_login import login_required, current_user
import sqlite3

activities_bp = Blueprint("activities", __name__, url_prefix="/activities")

DB_PATH = "models/mood.db"


# ===============================
# DB Helper
# ===============================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ===============================
# WRITING EDITOR
# ===============================
@activities_bp.route("/writing")
@login_required
def writing_editor():
    """Display writing editor with previous writings"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get user's previous writings
    cur.execute(
        """
        SELECT id, title, content, created_at
        FROM user_writings
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
        """,
        (current_user.id,)
    )
    
    writings = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    # Get recommended activity if exists
    recommended = session.get('recommended_activity', None)
    
    return render_template(
        "activities/writing_editor.html",
        writings=writings,
        recommended=recommended
    )


# ===============================
# READING RESOURCES
# ===============================
@activities_bp.route("/reading")
@login_required
def reading_resources():
    """Display reading resources and recommendations"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get reading activities
    cur.execute(
        """
        SELECT id, name, description, resource_link, difficulty_level
        FROM activities
        WHERE execution_type = 'reading' AND is_active = 1
        ORDER BY priority DESC
        LIMIT 20
        """,
    )
    
    resources = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    recommended = session.get('recommended_activity', None)
    
    return render_template(
        "activities/reading_resources.html",
        resources=resources,
        recommended=recommended
    )


# ===============================
# COOKING STEPS
# ===============================
@activities_bp.route("/cooking")
@login_required
def cooking_steps():
    """Display cooking recipe with step-by-step instructions"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get recommended activity or latest cooking activity
    recommended = session.get('recommended_activity', None)
    
    if recommended and recommended.get('execution_type') == 'cooking':
        activity_id = recommended['id']
    else:
        # Get default cooking activity
        cur.execute(
            """
            SELECT id FROM activities
            WHERE execution_type = 'cooking' AND is_active = 1
            ORDER BY priority DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        activity_id = row['id'] if row else None
    
    recipe = None
    if activity_id:
        cur.execute(
            """
            SELECT id, name, description, cooking_time, servings, 
                   difficulty_level, video_link
            FROM activities
            WHERE id = ?
            """,
            (activity_id,)
        )
        recipe = dict(cur.fetchone()) if cur.fetchone() else None
        
        if recipe:
            # Get cooking steps
            cur.execute(
                """
                SELECT step_number, instruction
                FROM cooking_steps
                WHERE activity_id = ?
                ORDER BY step_number ASC
                """,
                (activity_id,)
            )
            recipe['steps'] = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    
    return render_template(
        "activities/cooking_steps.html",
        recipe=recipe,
        recommended=recommended
    )


# ===============================
# GAMES & SPORTS DETAILS
# ===============================
@activities_bp.route("/games")
@login_required
def games_details():
    """Display game/sport details with rules and tutorials"""
    conn = get_db()
    cur = conn.cursor()
    
    recommended = session.get('recommended_activity', None)
    
    if recommended and recommended.get('execution_type') == 'games':
        activity_id = recommended['id']
    else:
        # Get default game activity
        cur.execute(
            """
            SELECT id FROM activities
            WHERE execution_type = 'games' AND is_active = 1
            ORDER BY priority DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        activity_id = row['id'] if row else None
    
    game = None
    if activity_id:
        cur.execute(
            """
            SELECT id, name, description, tutorial_link, 
                   indoor_outdoor, difficulty_level
            FROM activities
            WHERE id = ?
            """,
            (activity_id,)
        )
        game = dict(cur.fetchone()) if cur.fetchone() else None
        
        if game:
            # Get game rules
            cur.execute(
                """
                SELECT rule_number, rule_text
                FROM game_rules
                WHERE activity_id = ?
                ORDER BY rule_number ASC
                """,
                (activity_id,)
            )
            game['rules'] = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    
    return render_template(
        "activities/games_details.html",
        game=game,
        recommended=recommended
    )


# ===============================
# TRAVEL PLACES
# ===============================
@activities_bp.route("/travel")
@login_required
def travel_places():
    """Display travel destination recommendations"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get travel activities
    cur.execute(
        """
        SELECT id, name, description, distance, budget_level,
               location_type, image_url
        FROM activities
        WHERE execution_type = 'travel' AND is_active = 1
        ORDER BY priority DESC
        LIMIT 20
        """,
    )
    
    places = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    recommended = session.get('recommended_activity', None)
    
    return render_template(
        "activities/travel_places.html",
        places=places,
        recommended=recommended
    )


# ===============================
# CLEAR RECOMMENDATION (Helper)
# ===============================
@activities_bp.route("/clear-recommendation")
@login_required
def clear_recommendation():
    """Clear recommended activity from session"""
    session.pop('recommended_activity', None)
    return redirect(url_for('user.user_dashboard'))