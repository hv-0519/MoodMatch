"""
MoodMatch - Complete User Module Routes (FIXED)
All routes for user functionality with VADER sentiment analysis
Fixed: Added 'user' variable to all render_template calls
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
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import sqlite3
import os
from datetime import datetime, timedelta

# VADER Sentiment Analysis
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("⚠️ WARNING: vaderSentiment not installed. Run: pip install vaderSentiment")

user_bp = Blueprint("user", __name__)

# Configuration
DB_PATH = "models/instance/moodmatch.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


# ===============================
# HELPER FUNCTIONS
# ===============================


def get_db():
    """Get database connection with Row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_current_user_dict():
    """Helper function to get current user data as dictionary"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (current_user.id,))
    user = dict(cursor.fetchone())
    conn.close()
    return user


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_sentiment_classification(score):
    """Classify sentiment score into positive/neutral/negative"""
    if score >= 0.2:
        return "positive", "😊"
    elif score <= -0.2:
        return "negative", "😔"
    else:
        return "neutral", "😐"


def extract_keywords(text, min_length=3):
    """Extract meaningful keywords from text"""
    stop_words = {
        "the",
        "and",
        "for",
        "are",
        "but",
        "not",
        "you",
        "all",
        "can",
        "her",
        "was",
        "one",
        "our",
        "out",
        "day",
        "get",
        "has",
        "him",
        "his",
        "how",
        "man",
        "new",
        "now",
        "old",
        "see",
        "two",
        "way",
        "who",
        "boy",
        "did",
        "its",
        "let",
        "put",
        "say",
        "she",
        "too",
        "use",
    }
    words = text.lower().split()
    keywords = [
        word for word in words if len(word) >= min_length and word not in stop_words
    ]
    return keywords


# ===============================
# 1. USER DASHBOARD
# ===============================


@user_bp.route("/user_dashboard")
@login_required
def user_dashboard():
    """Main user dashboard with stats and recommendations"""
    user_id = current_user.id
    conn = get_db()
    cursor = conn.cursor()

    # Get user info
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())

    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM user_history WHERE user_id = ?", (user_id,))
    activities_tried = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM favorites WHERE user_id = ?", (user_id,))
    total_favorites = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM user_history 
        WHERE user_id = ? AND sentiment_score IS NOT NULL
    """,
        (user_id,),
    )
    mood_entries = cursor.fetchone()[0]

    # Calculate streak (consecutive days with activities)
    cursor.execute(
        """
        SELECT DATE(created_at) as activity_date 
        FROM user_history 
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 30
    """,
        (user_id,),
    )

    dates = [row[0] for row in cursor.fetchall()]
    streak_days = 0
    if dates:
        current_date = datetime.now().date()
        for i, date_str in enumerate(dates):
            activity_date = datetime.fromisoformat(date_str).date()
            if (current_date - activity_date).days == i:
                streak_days += 1
            else:
                break

    # Get recent history (last 5 activities)
    cursor.execute(
        """
        SELECT uh.*, a.name as activity_name, a.execution_type
        FROM user_history uh
        JOIN activities a ON uh.activity_id = a.id
        WHERE uh.user_id = ?
        ORDER BY uh.created_at DESC
        LIMIT 5
    """,
        (user_id,),
    )
    recent_history = [dict(row) for row in cursor.fetchall()]

    # Get recommended activities (based on user interests and popularity)
    cursor.execute(
        """
        SELECT DISTINCT a.id, a.name, a.description, a.execution_type, 
               c.name as category_name, c.icon
        FROM activities a
        JOIN categories c ON a.category_id = c.id
        LEFT JOIN user_interests ui ON ui.user_id = ?
        LEFT JOIN interests i ON ui.interest_id = i.id
        WHERE a.is_active = 1
        ORDER BY CASE WHEN i.id IS NOT NULL THEN 0 ELSE 1 END, a.priority DESC
        LIMIT 6
    """,
        (user_id,),
    )
    recommended = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "user/user_dashboard.html",
        user=user,
        activities_tried=activities_tried,
        total_favorites=total_favorites,
        mood_entries=mood_entries,
        streak_days=streak_days,
        recent_history=recent_history,
        recommended=recommended,
    )


# ===============================
# 2. TRY ACTIVITY (MOOD INPUT & RECOMMENDATIONS)
# ===============================


@user_bp.route("/try_activity", methods=["GET", "POST"])
@login_required
def try_activity():
    """Activity recommendation based on VADER sentiment analysis"""

    # Get user data for the template
    user = get_current_user_dict()

    if request.method == "POST":
        mood_input = request.form.get("mood_input", "").strip()

        if not mood_input:
            flash("Please tell us how you're feeling!", "warning")
            return redirect(url_for("user.try_activity"))

        # VADER Sentiment Analysis
        if VADER_AVAILABLE:
            analyzer = SentimentIntensityAnalyzer()
            sentiment = analyzer.polarity_scores(mood_input)
            sentiment_score = sentiment["compound"]
        else:
            # Fallback: Simple keyword matching
            sentiment_score = 0.0
            negative_keywords = [
                "sad",
                "angry",
                "stressed",
                "anxious",
                "depressed",
                "tired",
                "bored",
                "lonely",
                "frustrated",
                "overwhelmed",
            ]
            positive_keywords = [
                "happy",
                "excited",
                "energetic",
                "motivated",
                "calm",
                "peaceful",
                "joyful",
                "confident",
            ]

            mood_lower = mood_input.lower()
            for word in negative_keywords:
                if word in mood_lower:
                    sentiment_score -= 0.3
            for word in positive_keywords:
                if word in mood_lower:
                    sentiment_score += 0.3

            sentiment_score = max(-1.0, min(1.0, sentiment_score))

        # Get mood classification
        mood_type, mood_emoji = get_sentiment_classification(sentiment_score)

        # Extract keywords for matching
        keywords = extract_keywords(mood_input)

        # Get optional filters
        energy_level = request.form.get("energy_level")
        time_available = request.form.get("time_available")
        location_type = request.form.get("location_type")
        social_type = request.form.get("social_type")

        # Build query
        conn = get_db()
        cursor = conn.cursor()

        query = """
            SELECT a.id, a.name, a.description, a.execution_type, a.priority,
                   c.name as category_name, c.icon as category_icon
            FROM activities a
            JOIN categories c ON a.category_id = c.id
            WHERE a.is_active = 1
        """
        params = []

        # Mood-based filtering (keyword matching in mood_tags)
        if keywords:
            mood_conditions = " OR ".join(
                [f"LOWER(a.mood_tags) LIKE ?" for _ in keywords]
            )
            query += f" AND ({mood_conditions})"
            params.extend([f"%{kw}%" for kw in keywords])

        # Apply activity_filters if they exist
        if energy_level or time_available or location_type or social_type:
            query += " AND a.id IN (SELECT activity_id FROM activity_filters WHERE 1=1"

            if energy_level:
                query += " AND energy_level = ?"
                params.append(energy_level)

            if time_available:
                time_mins = int(time_available)
                query += " AND min_time <= ? AND max_time >= ?"
                params.extend([time_mins, time_mins])

            if location_type:
                query += " AND location_type = ?"
                params.append(location_type)

            if social_type:
                query += " AND social_type = ?"
                params.append(social_type)

            query += ")"

        query += " ORDER BY a.priority DESC, RANDOM() LIMIT 10"

        cursor.execute(query, params)
        recommended_activities = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Store mood in session for activity tracking
        session["mood_input"] = mood_input
        session["sentiment_score"] = sentiment_score
        session["mood_type"] = mood_type

        return render_template(
            "user/try_activity.html",
            user=user,
            searched=True,
            mood_input=mood_input,
            mood_type=mood_type,
            mood_emoji=mood_emoji,
            sentiment_score=sentiment_score,
            recommendations=recommended_activities,
        )

    # GET request - show mood input form
    return render_template("user/try_activity.html", user=user, searched=False)


# ===============================
# 3. ACTIVITY DETAIL & VIEWING
# ===============================


@user_bp.route("/activity/<int:activity_id>")
@login_required
def activity_detail(activity_id):
    """View activity details with execution content"""
    conn = get_db()
    cursor = conn.cursor()

    # Get user data for the template - THIS WAS MISSING!
    user = get_current_user_dict()

    # Get activity basic info
    cursor.execute(
        """
        SELECT a.*, c.name as category_name, c.icon as category_icon
        FROM activities a
        JOIN categories c ON a.category_id = c.id
        WHERE a.id = ?
    """,
        (activity_id,),
    )

    row = cursor.fetchone()
    if not row:
        flash("Activity not found!", "error")
        return redirect(url_for("user.user_dashboard"))

    activity = dict(row)
    execution_type = activity["execution_type"]

    # Initialize execution_data
    activity["execution_data"] = {}

    # Get execution-specific data
    if execution_type == "resource":
        # Resource-based activity (videos, articles, etc.)
        cursor.execute(
            """
            SELECT * FROM resources 
            WHERE activity_id = ?
            ORDER BY difficulty
        """,
            (activity_id,),
        )
        resources = [dict(row) for row in cursor.fetchall()]
        activity["execution_data"] = {"resources": resources}

    elif execution_type == "steps":
        # Cooking/Steps type
        cursor.execute(
            """
            SELECT * FROM activity_steps 
            WHERE activity_id = ?
            ORDER BY step_number
        """,
            (activity_id,),
        )
        steps = [dict(row) for row in cursor.fetchall()]
        activity["execution_data"] = {"steps": steps}

    elif execution_type == "gaming":
        # Physical/Gaming type
        cursor.execute(
            """
            SELECT * FROM game_rules 
            WHERE game_id = ?
        """,
            (activity_id,),
        )
        rules = [dict(row) for row in cursor.fetchall()]

        cursor.execute(
            """
            SELECT * FROM game_tutorials 
            WHERE game_id = ?
        """,
            (activity_id,),
        )
        tutorials = [dict(row) for row in cursor.fetchall()]

        activity["execution_data"] = {"rules": rules, "tutorials": tutorials}

    elif execution_type == "travel":
        # Travel type
        cursor.execute(
            """
            SELECT * FROM travel_places 
            WHERE activity_id = ?
            ORDER BY distance_km
        """,
            (activity_id,),
        )
        places = [dict(row) for row in cursor.fetchall()]
        activity["execution_data"] = {"places": places}

    # Check if already in favorites
    cursor.execute(
        """
        SELECT COUNT(*) FROM favorites 
        WHERE user_id = ? AND activity_id = ?
    """,
        (current_user.id, activity_id),
    )
    activity["is_favorite"] = cursor.fetchone()[0] > 0

    # Get activity filters
    cursor.execute(
        """
        SELECT * FROM activity_filters 
        WHERE activity_id = ?
    """,
        (activity_id,),
    )
    filter_row = cursor.fetchone()
    activity["filters"] = dict(filter_row) if filter_row else None

    conn.close()

    # FIXED: Added user variable here
    return render_template("user/activity_detail.html", user=user, activity=activity)


# ===============================
# 4. ACTIVITY EXECUTION & RATING
# ===============================


@user_bp.route("/activity/<int:activity_id>/rate", methods=["POST"])
@login_required
def rate_activity(activity_id):
    """Record activity rating and feedback"""
    rating = request.form.get("rating", type=int)
    feedback_text = request.form.get("feedback_text", "").strip()

    if not rating or rating < 1 or rating > 5:
        flash("Invalid rating!", "error")
        return redirect(url_for("user.activity_detail", activity_id=activity_id))

    # Get mood data from session
    mood_input = session.get("mood_input", "Direct access")
    sentiment_score = session.get("sentiment_score", 0.0)

    conn = get_db()
    cursor = conn.cursor()

    # Insert into user_history
    cursor.execute(
        """
        INSERT INTO user_history (
            user_id, activity_id, mood_input, sentiment_score, 
            feedback_rating, feedback_text, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            current_user.id,
            activity_id,
            mood_input,
            sentiment_score,
            rating,
            feedback_text,
            datetime.utcnow().isoformat(),
        ),
    )

    conn.commit()
    conn.close()

    # Clear session data
    session.pop("mood_input", None)
    session.pop("sentiment_score", None)
    session.pop("mood_type", None)

    flash(f"Thank you for your feedback! {'⭐' * rating}", "success")
    return redirect(url_for("user.activity_detail", activity_id=activity_id))


# ===============================
# 5. WRITING/EDITOR ACTIVITY
# ===============================


@user_bp.route("/activity/<int:activity_id>/write", methods=["GET", "POST"])
@login_required
def write_activity(activity_id):
    """Writing/Journaling activity with editor"""

    user = get_current_user_dict()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Title and content are required!", "error")
            return redirect(url_for("user.write_activity", activity_id=activity_id))

        conn = get_db()
        cursor = conn.cursor()

        # Save writing
        cursor.execute(
            """
            INSERT INTO user_writings (
                user_id, activity_id, title, content, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                current_user.id,
                activity_id,
                title,
                content,
                datetime.utcnow().isoformat(),
            ),
        )

        # Also add to history
        mood_input = session.get("mood_input", "Writing activity")
        sentiment_score = session.get("sentiment_score", 0.0)

        cursor.execute(
            """
            INSERT INTO user_history (
                user_id, activity_id, mood_input, sentiment_score, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                current_user.id,
                activity_id,
                mood_input,
                sentiment_score,
                datetime.utcnow().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        flash("Your writing has been saved! ✍️", "success")
        return redirect(url_for("user.my_writings"))

    # GET - Show editor
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT a.name, a.description, c.name as category_name
        FROM activities a
        JOIN categories c ON a.category_id = c.id
        WHERE a.id = ?
    """,
        (activity_id,),
    )

    row = cursor.fetchone()
    if not row:
        flash("Activity not found!", "error")
        return redirect(url_for("user.user_dashboard"))

    activity = dict(row)
    activity["id"] = activity_id
    conn.close()

    return render_template("user/write_activity.html", user=user, activity=activity)


@user_bp.route("/writings")
@login_required
def my_writings():
    """View user's saved writings"""
    user = get_current_user_dict()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT w.*, a.name as activity_name
        FROM user_writings w
        JOIN activities a ON w.activity_id = a.id
        WHERE w.user_id = ?
        ORDER BY w.created_at DESC
    """,
        (current_user.id,),
    )

    writings = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template("user/my_writings.html", user=user, writings=writings)


# ===============================
# 6. FAVORITES MANAGEMENT
# ===============================


@user_bp.route("/favorites")
@login_required
def favorites():
    """View user's favorite activities"""
    user = get_current_user_dict()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT a.*, c.name as category_name, c.icon as category_icon, 
               f.created_at as favorited_at
        FROM favorites f
        JOIN activities a ON f.activity_id = a.id
        JOIN categories c ON a.category_id = c.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    """,
        (current_user.id,),
    )

    favorites_list = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # FIXED: Added user variable here
    return render_template("user/favorites.html", user=user, favorites=favorites_list)


@user_bp.route("/favorite/<int:activity_id>", methods=["POST"])
@login_required
def toggle_favorite(activity_id):
    """Toggle favorite status (AJAX endpoint)"""
    conn = get_db()
    cursor = conn.cursor()

    # Check if already favorited
    cursor.execute(
        """
        SELECT COUNT(*) FROM favorites 
        WHERE user_id = ? AND activity_id = ?
    """,
        (current_user.id, activity_id),
    )

    is_favorited = cursor.fetchone()[0] > 0

    if is_favorited:
        # Remove from favorites
        cursor.execute(
            """
            DELETE FROM favorites 
            WHERE user_id = ? AND activity_id = ?
        """,
            (current_user.id, activity_id),
        )
        message = "Removed from favorites"
        favorited = False
    else:
        # Add to favorites
        try:
            cursor.execute(
                """
                INSERT INTO favorites (user_id, activity_id, created_at)
                VALUES (?, ?, ?)
            """,
                (current_user.id, activity_id, datetime.utcnow().isoformat()),
            )
            message = "Added to favorites! ⭐"
            favorited = True
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"success": False, "message": "Already in favorites"})

    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": message, "favorited": favorited})


# ===============================
# 7. ACTIVITY HISTORY
# ===============================


@user_bp.route("/history")
@login_required
def history():
    """Show user's activity history with mood tracking"""
    user = get_current_user_dict()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT uh.*, a.name as activity_name, a.execution_type,
               CASE 
                   WHEN uh.sentiment_score >= 0.2 THEN 'positive'
                   WHEN uh.sentiment_score <= -0.2 THEN 'negative'
                   ELSE 'neutral'
               END as mood_type
        FROM user_history uh
        JOIN activities a ON uh.activity_id = a.id
        WHERE uh.user_id = ?
        ORDER BY uh.created_at DESC
    """,
        (current_user.id,),
    )

    history_list = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # FIXED: Added user variable here
    return render_template("user/history.html", user=user, history=history_list)


@user_bp.route("/history/delete/<int:history_id>", methods=["POST"])
@login_required
def delete_history(history_id):
    """Delete a history entry"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM user_history 
        WHERE id = ? AND user_id = ?
    """,
        (history_id, current_user.id),
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "History entry deleted"})


# ===============================
# 8. USER PROFILE & SETTINGS
# ===============================


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile and settings management"""

    if request.method == "POST":
        # Handle profile picture upload
        if "profile_picture" in request.files:
            file = request.files["profile_picture"]

            if file and file.filename and allowed_file(file.filename):
                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                if file_size > MAX_FILE_SIZE:
                    flash("File size exceeds 5MB limit!", "error")
                    return redirect(url_for("user.profile"))
                file.seek(0)

                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"user_{current_user.id}_{timestamp}_{filename}"

                os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                # Update database
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE users 
                    SET profile_picture = ? 
                    WHERE id = ?
                """,
                    (filename, current_user.id),
                )
                conn.commit()
                conn.close()

                flash("Profile picture updated! 📸", "success")
                return redirect(url_for("user.profile"))

        # Handle profile update (name, bio, etc.)
        if "first_name" in request.form:
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            bio = request.form.get("bio", "").strip()

            if not first_name:
                flash("First name is required!", "error")
                return redirect(url_for("user.profile"))

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users 
                SET first_name = ?, last_name = ?, bio = ? 
                WHERE id = ?
            """,
                (first_name, last_name, bio, current_user.id),
            )
            conn.commit()
            conn.close()

            flash("Profile updated successfully! ✨", "success")
            return redirect(url_for("user.profile"))

        # Handle interests update
        if "interests" in request.form:
            interest_ids = request.form.getlist("interests")

            conn = get_db()
            cursor = conn.cursor()

            # Clear existing interests
            cursor.execute(
                "DELETE FROM user_interests WHERE user_id = ?", (current_user.id,)
            )

            # Add new interests
            for interest_id in interest_ids:
                cursor.execute(
                    """
                    INSERT INTO user_interests (user_id, interest_id)
                    VALUES (?, ?)
                """,
                    (current_user.id, int(interest_id)),
                )

            conn.commit()
            conn.close()

            flash("Interests updated! 🎯", "success")
            return redirect(url_for("user.profile"))

        # Handle password change
        if "new_password" in request.form:
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if new_password != confirm_password:
                flash("Passwords don't match!", "error")
                return redirect(url_for("user.profile"))

            if len(new_password) < 6:
                flash("Password must be at least 6 characters!", "error")
                return redirect(url_for("user.profile"))

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users 
                SET password_hash = ? 
                WHERE id = ?
            """,
                (generate_password_hash(new_password), current_user.id),
            )
            conn.commit()
            conn.close()

            flash("Password changed successfully! 🔒", "success")
            return redirect(url_for("user.profile"))

    # GET - Load profile data
    conn = get_db()
    cursor = conn.cursor()

    # Get user info
    cursor.execute("SELECT * FROM users WHERE id = ?", (current_user.id,))
    user = dict(cursor.fetchone())

    # Get all interests with user's selections
    cursor.execute(
        """
        SELECT i.id, i.name, c.name as category_name,
               CASE WHEN ui.user_id IS NOT NULL THEN 1 ELSE 0 END as selected
        FROM interests i
        JOIN categories c ON i.category_id = c.id
        LEFT JOIN user_interests ui ON i.id = ui.interest_id AND ui.user_id = ?
        ORDER BY c.name, i.name
    """,
        (current_user.id,),
    )

    interests = [dict(row) for row in cursor.fetchall()]

    # Get user statistics for profile
    cursor.execute(
        """
        SELECT 
            (SELECT COUNT(*) FROM user_history WHERE user_id = ?) as total_activities,
            (SELECT COUNT(*) FROM favorites WHERE user_id = ?) as total_favorites,
            (SELECT COUNT(*) FROM user_writings WHERE user_id = ?) as total_writings,
            (SELECT AVG(feedback_rating) FROM user_history WHERE user_id = ? AND feedback_rating IS NOT NULL) as avg_rating
    """,
        (current_user.id, current_user.id, current_user.id, current_user.id),
    )

    stats = dict(cursor.fetchone())

    conn.close()

    return render_template(
        "user/profile.html", user=user, interests=interests, stats=stats
    )


# ===============================
# 9. MOOD ANALYTICS & INSIGHTS
# ===============================


@user_bp.route("/mood_insights")
@login_required
def mood_insights():
    """Personal mood analytics and insights"""
    user = get_current_user_dict()

    conn = get_db()
    cursor = conn.cursor()

    # Get mood distribution
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
        WHERE user_id = ? AND sentiment_score IS NOT NULL
        GROUP BY mood_type
    """,
        (current_user.id,),
    )

    mood_distribution = [dict(row) for row in cursor.fetchall()]

    # Get mood trends over time (last 30 days)
    cursor.execute(
        """
        SELECT DATE(created_at) as date, 
               AVG(sentiment_score) as avg_sentiment,
               COUNT(*) as activity_count
        FROM user_history
        WHERE user_id = ? AND sentiment_score IS NOT NULL
        AND DATE(created_at) >= DATE('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date
    """,
        (current_user.id,),
    )

    mood_trends = [dict(row) for row in cursor.fetchall()]

    # Get most common moods (keywords)
    cursor.execute(
        """
        SELECT mood_input, sentiment_score, created_at
        FROM user_history
        WHERE user_id = ? AND mood_input IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 20
    """,
        (current_user.id,),
    )

    recent_moods = [dict(row) for row in cursor.fetchall()]

    # Get activity effectiveness (highest rated activities)
    cursor.execute(
        """
        SELECT a.name, AVG(uh.feedback_rating) as avg_rating, COUNT(*) as times_tried
        FROM user_history uh
        JOIN activities a ON uh.activity_id = a.id
        WHERE uh.user_id = ? AND uh.feedback_rating IS NOT NULL
        GROUP BY a.id, a.name
        HAVING COUNT(*) >= 2
        ORDER BY avg_rating DESC
        LIMIT 10
    """,
        (current_user.id,),
    )

    top_activities = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "user/mood_insights.html",
        user=user,
        mood_distribution=mood_distribution,
        mood_trends=mood_trends,
        recent_moods=recent_moods,
        top_activities=top_activities,
    )


# ===============================
# 10. QUICK ACTIONS & UTILITIES
# ===============================


@user_bp.route("/activity/<int:activity_id>/quick-try", methods=["POST"])
@login_required
def quick_try_activity(activity_id):
    """Quick try activity without mood input"""
    session["mood_input"] = "Quick try"
    session["sentiment_score"] = 0.0
    session["mood_type"] = "neutral"

    return redirect(url_for("user.activity_detail", activity_id=activity_id))


@user_bp.route("/search_activities")
@login_required
def search_activities():
    """Search activities page with filters"""
    user = get_current_user_dict()

    query = request.args.get("q", "").strip()
    category = request.args.get("category", "")

    conn = get_db()
    cursor = conn.cursor()

    sql = """
        SELECT a.*, c.name as category_name, c.icon as category_icon
        FROM activities a
        JOIN categories c ON a.category_id = c.id
        WHERE a.is_active = 1
    """
    params = []

    if query:
        sql += " AND (LOWER(a.name) LIKE ? OR LOWER(a.description) LIKE ?)"
        params.extend([f"%{query.lower()}%", f"%{query.lower()}%"])

    if category:
        sql += " AND c.id = ?"
        params.append(category)

    sql += " ORDER BY a.priority DESC, a.name"

    cursor.execute(sql, params)
    activities = [dict(row) for row in cursor.fetchall()]

    # Get all categories for filter
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = [dict(row) for row in cursor.fetchall()]

    conn.close()

    # FIXED: Added user variable here
    return render_template(
        "user/search_activities.html",
        user=user,
        activities=activities,
        categories=categories,
        search_query=query,
    )


@user_bp.route("/categories")
@login_required
def browse_categories():
    """Browse activities by category"""
    user = get_current_user_dict()

    conn = get_db()
    cursor = conn.cursor()

    # Get all categories with activity counts
    cursor.execute(
        """
        SELECT c.id, c.name, c.icon, c.description,
               COUNT(a.id) as activity_count
        FROM categories c
        LEFT JOIN activities a ON c.id = a.category_id AND a.is_active = 1
        GROUP BY c.id
        ORDER BY c.name
    """,
        (),
    )

    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # FIXED: Added user variable here
    return render_template(
        "user/browse_categories.html", user=user, categories=categories
    )


@user_bp.route("/category/<int:category_id>")
@login_required
def category_activities(category_id):
    """View all activities in a category"""
    user = get_current_user_dict()

    conn = get_db()
    cursor = conn.cursor()

    # Get category info
    cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    category = dict(cursor.fetchone())

    # Get activities in this category
    cursor.execute(
        """
        SELECT a.*, c.name as category_name, c.icon as category_icon
        FROM activities a
        JOIN categories c ON a.category_id = c.id
        WHERE c.id = ? AND a.is_active = 1
        ORDER BY a.priority DESC, a.name
    """,
        (category_id,),
    )

    activities = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # FIXED: Added user variable here
    return render_template(
        "user/category_activities.html",
        user=user,
        category=category,
        activities=activities,
    )
