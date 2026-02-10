"""
MoodMatch - User Routes
Complete Flask route definitions for the user module with VADER sentiment analysis.
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
import sqlite3
import os
from datetime import datetime

# VADER Sentiment Analysis
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("WARNING: vaderSentiment not installed. Install with: pip install vaderSentiment")

user_bp = Blueprint("user", __name__)

DB_PATH = "models/instance/moodmatch.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


# ===============================
# HELPER FUNCTIONS
# ===============================

def get_db():
    """Get database connection with Row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===============================
# MAIN DASHBOARD
# ===============================

@user_bp.route("/user_dashboard")
@login_required
def user_dashboard():
    """Render the main user dashboard with stats and recommendations"""
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
    
    cursor.execute("""
        SELECT COUNT(*) FROM user_history 
        WHERE user_id = ? AND sentiment_score IS NOT NULL
    """, (user_id,))
    mood_entries = cursor.fetchone()[0]
    
    # Get recent history (last 5 activities)
    cursor.execute("""
        SELECT uh.*, a.name as activity_name, a.execution_type
        FROM user_history uh
        JOIN activities a ON uh.activity_id = a.id
        WHERE uh.user_id = ?
        ORDER BY uh.created_at DESC
        LIMIT 5
    """, (user_id,))
    recent_history = [dict(row) for row in cursor.fetchall()]
    
    # Get recommended activities (based on user interests)
    cursor.execute("""
        SELECT DISTINCT a.id, a.name, a.description, a.execution_type, 
               c.name as category_name, c.icon
        FROM activities a
        JOIN categories c ON a.category_id = c.id
        LEFT JOIN user_interests ui ON ui.user_id = ?
        LEFT JOIN interests i ON ui.interest_id = i.id AND i.category_id = c.id
        WHERE a.is_active = 1
        ORDER BY CASE WHEN i.id IS NOT NULL THEN 0 ELSE 1 END, a.priority DESC
        LIMIT 6
    """, (user_id,))
    recommended = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template(
        'user/user_dashboard.html',
        user=user,
        activities_tried=activities_tried,
        total_favorites=total_favorites,
        mood_entries=mood_entries,
        recent_history=recent_history,
        recommended=recommended
    )


# ===============================
# TRY ACTIVITY (VADER MOOD INPUT)
# ===============================

@user_bp.route("/try_activity", methods=["GET", "POST"])
@login_required
def try_activity():
    """Activity recommendation based on VADER sentiment analysis"""
    
    if request.method == "POST":
        mood_input = request.form.get("mood_input", "").strip()
        
        if not mood_input:
            flash("Please tell us how you're feeling!", "error")
            return redirect(url_for('user.try_activity'))
        
        # VADER Sentiment Analysis
        if VADER_AVAILABLE:
            analyzer = SentimentIntensityAnalyzer()
            sentiment = analyzer.polarity_scores(mood_input)
            sentiment_score = sentiment['compound']
        else:
            # Fallback: Simple keyword matching
            sentiment_score = 0.0
            negative_keywords = ['sad', 'angry', 'stressed', 'anxious', 'depressed', 'tired', 'bored']
            positive_keywords = ['happy', 'excited', 'energetic', 'motivated', 'calm', 'peaceful']
            
            mood_lower = mood_input.lower()
            for word in negative_keywords:
                if word in mood_lower:
                    sentiment_score -= 0.3
            for word in positive_keywords:
                if word in mood_lower:
                    sentiment_score += 0.3
            
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        # Extract keywords for matching
        keywords = [word.lower() for word in mood_input.split() if len(word) > 3]
        
        # Get optional filters
        energy_level = request.form.get("energy_level")
        time_available = request.form.get("time_available")
        location_type = request.form.get("location_type")
        social_type = request.form.get("social_type")
        
        # Build query
        conn = get_db()
        cursor = conn.cursor()
        
        query = """
            SELECT a.*, c.name as category_name, c.icon as category_icon
            FROM activities a
            JOIN categories c ON a.category_id = c.id
            WHERE a.is_active = 1
        """
        params = []
        
        # Mood-based filtering
        if keywords:
            mood_conditions = " OR ".join([f"LOWER(a.mood_tags) LIKE ?" for _ in keywords])
            query += f" AND ({mood_conditions})"
            params.extend([f"%{kw}%" for kw in keywords])
        
        # Apply filters
        if energy_level:
            query += " AND a.energy_level = ?"
            params.append(energy_level)
        
        if time_available:
            query += " AND a.min_time <= ? AND a.max_time >= ?"
            params.extend([int(time_available), int(time_available)])
        
        if location_type:
            query += " AND a.location_type IN (?, 'Both')"
            params.append(location_type)
        
        if social_type:
            query += " AND a.social_type IN (?, 'Both')"
            params.append(social_type)
        
        query += " ORDER BY a.priority DESC LIMIT 10"
        
        cursor.execute(query, params)
        recommendations = [dict(row) for row in cursor.fetchall()]
        
        # If no results with filters, try without filters
        if not recommendations and (energy_level or time_available or location_type or social_type):
            query = """
                SELECT a.*, c.name as category_name, c.icon as category_icon
                FROM activities a
                JOIN categories c ON a.category_id = c.id
                WHERE a.is_active = 1
                ORDER BY a.priority DESC
                LIMIT 10
            """
            cursor.execute(query)
            recommendations = [dict(row) for row in cursor.fetchall()]
            flash("No exact matches found. Here are some general recommendations!", "info")
        
        conn.close()
        
        # Store in session for activity execution
        session['mood_input'] = mood_input
        session['sentiment_score'] = sentiment_score
        
        return render_template(
            'user/try_activity.html',
            mood_input=mood_input,
            sentiment_score=sentiment_score,
            recommendations=recommendations,
            searched=True
        )
    
    # GET request - show input form
    return render_template('user/try_activity.html', searched=False)


# ===============================
# ACTIVITY DETAIL & EXECUTION
# ===============================

@user_bp.route("/activity/<int:activity_id>", methods=["GET", "POST"])
@login_required
def activity_detail(activity_id):
    """View and execute an activity"""
    
    if request.method == "POST":
        # User completed activity and is rating it
        rating = request.form.get("rating")
        mood_input = session.get('mood_input', '')
        sentiment_score = session.get('sentiment_score', 0.0)
        
        if not rating:
            flash("Please provide a rating!", "error")
            return redirect(url_for('user.activity_detail', activity_id=activity_id))
        
        # Save to user_history
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_history 
            (user_id, activity_id, mood_input, sentiment_score, feedback_rating, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            current_user.id,
            activity_id,
            mood_input,
            sentiment_score,
            int(rating),
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Clear session
        session.pop('mood_input', None)
        session.pop('sentiment_score', None)
        
        flash("Activity completed! Thanks for your feedback. 🎉", "success")
        return redirect(url_for('user.user_dashboard'))
    
    # GET - Show activity details
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.*, c.name as category_name, c.icon as category_icon
        FROM activities a
        JOIN categories c ON a.category_id = c.id
        WHERE a.id = ?
    """, (activity_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        flash("Activity not found!", "error")
        return redirect(url_for('user.user_dashboard'))
    
    activity = dict(row)
    
    # Get execution-specific data based on execution_type
    if activity['execution_type'] == 'steps':
        cursor.execute("""
            SELECT * FROM activity_steps 
            WHERE activity_id = ? 
            ORDER BY step_number
        """, (activity_id,))
        steps = [dict(r) for r in cursor.fetchall()]
        activity['steps'] = steps
    
    elif activity['execution_type'] == 'resource':
        cursor.execute("""
            SELECT * FROM activity_resources 
            WHERE activity_id = ?
        """, (activity_id,))
        resources = [dict(r) for r in cursor.fetchall()]
        activity['resources'] = resources
    
    # Check if already favorited
    cursor.execute("""
        SELECT id FROM favorites 
        WHERE user_id = ? AND activity_id = ?
    """, (current_user.id, activity_id))
    
    activity['is_favorited'] = cursor.fetchone() is not None
    
    conn.close()
    
    return render_template('user/activity_detail.html', activity=activity)


# ===============================
# FAVORITES
# ===============================

@user_bp.route("/favorites")
@login_required
def favorites():
    """Show user's favorite activities"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.*, c.name as category_name, c.icon as category_icon, 
               f.created_at as favorited_at
        FROM favorites f
        JOIN activities a ON f.activity_id = a.id
        JOIN categories c ON a.category_id = c.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    """, (current_user.id,))
    
    favorites_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('main/favorites.html', favorites=favorites_list)


@user_bp.route("/favorites/add/<int:activity_id>", methods=["POST"])
@login_required
def add_favorite(activity_id):
    """Add activity to favorites"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO favorites (user_id, activity_id, created_at)
            VALUES (?, ?, ?)
        """, (current_user.id, activity_id, datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Added to favorites!'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Already in favorites'})


@user_bp.route("/favorites/remove/<int:activity_id>", methods=["POST"])
@login_required
def remove_favorite(activity_id):
    """Remove activity from favorites"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM favorites 
        WHERE user_id = ? AND activity_id = ?
    """, (current_user.id, activity_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Removed from favorites'})


# ===============================
# HISTORY
# ===============================

@user_bp.route("/history")
@login_required
def history():
    """Show user's activity history"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
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
    """, (current_user.id,))
    
    history_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('user/history.html', history=history_list)


# ===============================
# PROFILE & SETTINGS
# ===============================

@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile and settings"""
    
    if request.method == "POST":
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid overwriting
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{current_user.id}_{timestamp}_{filename}"
                
                # Create upload folder if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Update database
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET profile_picture = ? 
                    WHERE id = ?
                """, (filename, current_user.id))
                conn.commit()
                conn.close()
                
                flash("Profile picture updated successfully! 📸", "success")
                return redirect(url_for('user.profile'))
        
        # Handle interests update
        if 'interests' in request.form:
            selected_interests = request.form.getlist('interests')
            
            conn = get_db()
            cursor = conn.cursor()
            
            # Delete existing interests
            cursor.execute("""
                DELETE FROM user_interests WHERE user_id = ?
            """, (current_user.id,))
            
            # Insert new interests
            for interest_id in selected_interests:
                cursor.execute("""
                    INSERT INTO user_interests (user_id, interest_id)
                    VALUES (?, ?)
                """, (current_user.id, int(interest_id)))
            
            conn.commit()
            conn.close()
            
            flash("Interests updated successfully! 🎯", "success")
            return redirect(url_for('user.profile'))
        
        # Handle password change
        if 'new_password' in request.form:
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password != confirm_password:
                flash("Passwords don't match!", "error")
                return redirect(url_for('user.profile'))
            
            if len(new_password) < 6:
                flash("Password must be at least 6 characters!", "error")
                return redirect(url_for('user.profile'))
            
            # Hash password (assuming you have werkzeug.security)
            from werkzeug.security import generate_password_hash
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET password_hash = ? 
                WHERE id = ?
            """, (generate_password_hash(new_password), current_user.id))
            conn.commit()
            conn.close()
            
            flash("Password changed successfully! 🔒", "success")
            return redirect(url_for('user.profile'))
    
    # GET - Load profile data
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute("SELECT * FROM users WHERE id = ?", (current_user.id,))
    user = dict(cursor.fetchone())
    
    # Get all interests with user's selections
    cursor.execute("""
        SELECT i.id, i.name, c.name as category_name,
               CASE WHEN ui.user_id IS NOT NULL THEN 1 ELSE 0 END as selected
        FROM interests i
        JOIN categories c ON i.category_id = c.id
        LEFT JOIN user_interests ui ON i.id = ui.interest_id AND ui.user_id = ?
        ORDER BY c.name, i.name
    """, (current_user.id,))
    
    interests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('user/profile.html', user=user, interests=interests)


# ===============================
# QUICK ACTIONS
# ===============================

@user_bp.route("/activity/<int:activity_id>/quick-try", methods=["POST"])
@login_required
def quick_try_activity(activity_id):
    """Quick try activity without mood input"""
    # Set default mood values
    session['mood_input'] = 'Quick try'
    session['sentiment_score'] = 0.0
    
    return redirect(url_for('user.activity_detail', activity_id=activity_id))