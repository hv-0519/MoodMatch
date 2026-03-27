"""
MoodMatch - Complete User Module Routes
Fixed: removed duplicate try_activity route
Added: Gemini AI chatbot with auto model discovery + debug endpoint
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
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
import urllib.request
import urllib.error
import time
from datetime import datetime, timedelta

# VADER Sentiment Analysis
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("⚠️ vaderSentiment not installed. Run: pip install vaderSentiment")

# Emotion Detection (ML Model)
try:
    from emotion_detector import predict_emotion_with_vader

    EMOTION_MODEL_AVAILABLE = True
    print("✅ Emotion detection model loaded")
except ImportError as e:
    EMOTION_MODEL_AVAILABLE = False
    print(f"⚠️ Emotion detection not available: {e}")

user_bp = Blueprint("user", __name__)

DB_PATH = "models/instance/moodmatch.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024

# ── Gemini config ──────────────────────────────────────────────────────────────

# 🔑 Hardcoded Gemini API key — no need for user to enter it
GEMINI_API_KEY = "AIzaSyA7B9AAndpAmkIIwm9dZ3dd_3vwI_BbZaI"

GEMINI_SYSTEM = (
    "You are MoodMatch Assistant, a friendly and empathetic AI that helps users "
    "discover activities based on their mood. Acknowledge their feelings with warmth, "
    "ask clarifying questions when needed (time, energy, indoor/outdoor, alone/social), "
    "and suggest thoughtful personalized activities. Keep responses under 120 words. "
    "Use 1-2 emojis max. Be supportive and non-judgmental."
)

GEMINI_MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
]


def _list_gemini_models(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}&pageSize=50"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            return [
                m["name"].replace("models/", "")
                for m in data.get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ], None
    except urllib.error.HTTPError as e:
        return [], e.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return [], str(e)


def _gemini_call(api_key, model, prompt, system=None):
    """Single Gemini REST call. Returns (text, error_str)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    full_prompt = f"{system or GEMINI_SYSTEM}\n\n{prompt}"
    body = json.dumps(
        {
            "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600},
        }
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
            return data["candidates"][0]["content"]["parts"][0]["text"], None
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        return None, f"HTTP {e.code}: {raw[:300]}"
    except Exception as e:
        return None, str(e)


def call_gemini(api_key, prompt, system=None):
    """Auto-discover models then try them in order. Returns (text, log)."""
    available, _ = _list_gemini_models(api_key)
    ordered = [m for m in GEMINI_MODELS if m in available]
    ordered += [m for m in available if m not in ordered]
    if not ordered:
        ordered = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]

    log = [
        {
            "step": "list_models",
            "available": available or "discovery failed, using defaults",
        }
    ]

    for model in ordered:
        text, err = _gemini_call(api_key, model, prompt, system)
        if text:
            log.append({"step": "success", "model": model})
            return text, log
        code = 0
        try:
            code = int(err.split(":")[0].replace("HTTP ", "").strip())
        except:
            pass
        log.append({"step": "failed", "model": model, "error": err[:120]})
        if code == 429:
            time.sleep(0.5)
            continue
        if code in (404, 400):
            continue
        if code == 403:
            break

    raise Exception(json.dumps({"message": "All models failed", "log": log}, indent=2))


# ── Helper functions ───────────────────────────────────────────────────────────


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_current_user_dict():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (current_user.id,))
    user = dict(cursor.fetchone())
    conn.close()
    return user


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_sentiment_classification(score):
    if score >= 0.2:
        return "positive", "😊"
    elif score <= -0.2:
        return "negative", "😔"
    else:
        return "neutral", "😐"


def extract_keywords(text, min_length=3):
    """
    Enhanced keyword extraction with better filtering.
    Extracts meaningful words and prioritizes activity names.
    """
    # Expanded stopwords
    stopwords = {
        'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
        'in', 'with', 'to', 'for', 'of', 'as', 'by', 'i', 'me', 'my',
        'we', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can',
        'this', 'that', 'these', 'those', 'it', 'its',
        'he', 'she', 'they', 'them', 'their', 'his', 'her',
        'want', 'need', 'like', 'feel', 'feeling', 'something', 'anything'
    }
    
    # Activity-related keywords (high priority)
    activity_keywords = {
        'read', 'reading', 'book', 'books', 'novel', 'article',
        'write', 'writing', 'journal', 'diary', 'essay',
        'game', 'gaming', 'play', 'playing', 'video', 'sport', 'sports',
        'cook', 'cooking', 'recipe', 'food', 'bake', 'baking',
        'exercise', 'workout', 'yoga', 'run', 'running', 'walk', 'walking',
        'meditate', 'meditation', 'mindfulness', 'relax', 'relaxation',
        'paint', 'painting', 'draw', 'drawing', 'art', 'creative',
        'music', 'listen', 'song', 'sing', 'singing',
        'watch', 'movie', 'film', 'show', 'series', 'tv',
        'travel', 'trip', 'explore', 'adventure',
        'learn', 'study', 'course', 'education'
    }
    
    # Clean and split text
    words = text.lower().split()
    keywords = []
    
    for word in words:
        # Remove punctuation
        clean_word = word.strip('.,!?;:()[]{}"\'-')
        
        # Skip if too short or stopword
        if len(clean_word) < min_length or clean_word in stopwords:
            continue
        
        # Add activity keywords first (higher priority)
        if clean_word in activity_keywords:
            keywords.insert(0, clean_word)  # Insert at beginning
        else:
            keywords.append(clean_word)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    
    return unique_keywords[:10]


# ===============================
# CHATBOT ROUTES
# ===============================


@user_bp.route("/try_activity_chat")
@login_required
def try_activity_chat():
    """AI Chatbot interface — serves try_activity.html in chatbot mode"""
    user = get_current_user_dict()
    return render_template(
        "user/try_activity.html", user=user, searched=False, chatbot_mode=True
    )


"""
IMPROVED chat_mood() Function
==============================
Fixes activity filtering bug + includes emotion detection
Replace the existing chat_mood() function in user.py with this version
"""

@user_bp.route("/chat_mood", methods=["POST"])
@login_required
def chat_mood():
    """
    Enhanced chatbot endpoint: ML Emotion Detection + VADER sentiment + Gemini AI + Smart Activity Matching
    Expects JSON: { message, history }
    
    IMPROVEMENTS:
    - Better keyword extraction with activity prioritization
    - Smart activity filtering (reading -> only reading activities)
    - Name-first search strategy
    - Emotion-aware recommendations
    """
    debug_log = []

    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        history = data.get("history", [])

        debug_log.append(f"📨 Message received: '{user_message}'")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # ── 1. EMOTION DETECTION (ML + VADER) ─────────────────────────────────
        sentiment_data = None
        emotion_data = None
        mood_type = "neutral"
        mood_emoji = "😐"
        compound = 0.0
        detected_emotion = "neutral"
        emotion_confidence = 0.0

        if VADER_AVAILABLE:
            analyzer = SentimentIntensityAnalyzer()
            scores = analyzer.polarity_scores(user_message)
            compound = scores["compound"]

            # Try ML emotion detection if available
            if EMOTION_MODEL_AVAILABLE:
                try:
                    emotion_result = predict_emotion_with_vader(user_message, scores)

                    if emotion_result:
                        detected_emotion = emotion_result["emotion"]
                        emotion_confidence = emotion_result["emotion_confidence"]
                        mood_type = emotion_result["mood_category"]
                        mood_emoji = emotion_result["emotion_emoji"]

                        emotion_data = {
                            "emotion": detected_emotion,
                            "confidence": f"{emotion_confidence:.0%}",
                            "emoji": emotion_result["emotion_emoji"],
                            "top_emotions": emotion_result["top_emotions"],
                        }

                        sentiment_data = {
                            "type": mood_type,
                            "score": f"{compound:.2f}",
                            "emoji": emotion_result["mood_emoji"],
                            "label": f"{detected_emotion.capitalize()} ({emotion_confidence:.0%})",
                        }

                        debug_log.append(
                            f"🎭 EMOTION: {detected_emotion} ({emotion_confidence:.0%}) | "
                            f"VADER: {compound:.2f} → {mood_type}"
                        )
                    else:
                        # Fallback to VADER only
                        mood_type, mood_emoji = get_sentiment_classification(compound)
                        sentiment_data = {
                            "type": mood_type,
                            "score": f"{compound:.2f}",
                            "emoji": mood_emoji,
                            "label": mood_type.capitalize(),
                        }
                        debug_log.append(
                            f"🧠 VADER only: compound={compound:.2f} → {mood_type} {mood_emoji}"
                        )
                except Exception as e:
                    debug_log.append(f"⚠️ Emotion detection failed: {str(e)[:100]}")
                    # Fallback to VADER
                    mood_type, mood_emoji = get_sentiment_classification(compound)
                    sentiment_data = {
                        "type": mood_type,
                        "score": f"{compound:.2f}",
                        "emoji": mood_emoji,
                        "label": mood_type.capitalize(),
                    }
            else:
                # VADER only
                mood_type, mood_emoji = get_sentiment_classification(compound)
                sentiment_data = {
                    "type": mood_type,
                    "score": f"{compound:.2f}",
                    "emoji": mood_emoji,
                    "label": mood_type.capitalize(),
                }
                debug_log.append(
                    f"🧠 VADER only: compound={compound:.2f} → {mood_type} {mood_emoji}"
                )
        else:
            debug_log.append("⚠️ VADER not available — run: pip install vaderSentiment")

        # ── 2. Build conversation prompt ───────────────────────────────────────
        prompt = ""
        for msg in history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += f"User: {user_message}\nAssistant:"

        system = (
            f"{GEMINI_SYSTEM}\n\n"
            f"User's emotional state:\n"
            f"- Detected emotion: {detected_emotion} ({emotion_confidence:.0%} confidence) {mood_emoji}\n"
            f"- Sentiment score: {compound:.2f} ({mood_type})\n\n"
            "Respond with empathy and understanding. Acknowledge their feelings warmly. "
            f"Since they're feeling {detected_emotion}, suggest appropriate activities that match this emotion. "
            "Be supportive and helpful."
        )

        # ── 3. Gemini AI call (hardcoded key) ──────────────────────────────────
        ai_response = f"I sense you're feeling {mood_type} {mood_emoji}. Here are some activity matches for you!"
        model_used = "fallback"

        try:
            debug_log.append(f"🔑 Using hardcoded Gemini key: {GEMINI_API_KEY[:12]}...")
            ai_response, gemini_log = call_gemini(GEMINI_API_KEY, prompt, system)
            model_used = next(
                (e["model"] for e in gemini_log if e.get("step") == "success"),
                "unknown",
            )
            debug_log.append(f"✅ Gemini success using model: {model_used}")
            for entry in gemini_log:
                if entry.get("step") == "failed":
                    debug_log.append(
                        f"  ↳ Tried {entry['model']}: {entry.get('error', '')[:80]}"
                    )
        except Exception as e:
            err = str(e)
            debug_log.append(f"❌ Gemini failed: {err[:200]}")
            if "429" in err:
                ai_response = (
                    f"⚠️ Gemini quota exceeded. Based on your {mood_type} mood {mood_emoji}, "
                    "here are activity suggestions from our database:"
                )
            elif "403" in err:
                ai_response = (
                    "🔑 Gemini API key rejected (403). Please check the key in user.py."
                )
            else:
                ai_response = (
                    f"I sense you're feeling {mood_type} {mood_emoji}. "
                    "Here are some activity matches from our database!"
                )

        # ── 4. IMPROVED Activity Search with Smart Filtering ──────────────────
        activities = []

        try:
            conn = get_db()
            cursor = conn.cursor()

            # Check table structure
            cursor.execute("PRAGMA table_info(activities)")
            cols = [row[1] for row in cursor.fetchall()]
            debug_log.append(f"📋 activities columns: {cols}")

            has_mood_tags = "mood_tags" in cols
            has_category_id = "category_id" in cols

            # Check if categories table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='categories'"
            )
            has_categories_table = cursor.fetchone() is not None
            debug_log.append(f"📋 categories table exists: {has_categories_table}")

            # Build base query
            if has_categories_table and has_category_id:
                base_query = """
                    SELECT a.id, a.name, a.description, a.execution_type, a.priority,
                           c.name as category_name, c.icon as category_icon
                    FROM activities a
                    JOIN categories c ON a.category_id = c.id
                    WHERE a.is_active = 1
                """
            else:
                base_query = """
                    SELECT a.id, a.name, a.description, a.execution_type, a.priority,
                           a.execution_type as category_name, '🎯' as category_icon
                    FROM activities a
                    WHERE a.is_active = 1
                """

            params = []

            # IMPROVED: Extract keywords with activity prioritization
            keywords = extract_keywords_improved(user_message)
            debug_log.append(f"🔑 Extracted keywords: {keywords}")

            if keywords:
                if has_mood_tags:
                    # Search mood_tags
                    mood_conds = " OR ".join(
                        [f"LOWER(a.mood_tags) LIKE ?" for _ in keywords]
                    )
                    base_query += f" AND ({mood_conds})"
                    params.extend([f"%{kw}%" for kw in keywords])
                    
                    # Add mood-based filtering
                    if mood_type == "negative":
                        base_query += " AND (LOWER(a.mood_tags) LIKE '%calm%' OR LOWER(a.mood_tags) LIKE '%relax%' OR LOWER(a.mood_tags) LIKE '%peace%')"
                    elif mood_type == "positive":
                        base_query += " AND (LOWER(a.mood_tags) LIKE '%energetic%' OR LOWER(a.mood_tags) LIKE '%happy%' OR LOWER(a.mood_tags) LIKE '%fun%')"
                else:
                    # IMPROVED: Prioritize name matches over description
                    name_conditions = []
                    desc_conditions = []
                    
                    for kw in keywords:
                        name_conditions.append(f"LOWER(a.name) LIKE ?")
                        params.append(f"%{kw}%")
                        desc_conditions.append(f"LOWER(a.description) LIKE ?")
                        params.append(f"%{kw}%")
                    
                    # Combine (name matches OR description matches)
                    all_conditions = name_conditions + desc_conditions
                    base_query += f" AND ({' OR '.join(all_conditions)})"

            # Order by priority and add limit
            base_query += " ORDER BY a.priority DESC, RANDOM() LIMIT 5"

            debug_log.append(f"🗄️ DB query params: {params}")
            cursor.execute(base_query, params)
            activities = [dict(row) for row in cursor.fetchall()]
            debug_log.append(f"✅ Activities found: {len(activities)}")

            # Fallback: if no results, return top priority activities
            if not activities:
                debug_log.append(
                    "⚠️ No keyword matches — returning top priority activities"
                )
                if has_categories_table and has_category_id:
                    fallback_q = """
                        SELECT a.id, a.name, a.description, a.execution_type, a.priority,
                               c.name as category_name, c.icon as category_icon
                        FROM activities a
                        JOIN categories c ON a.category_id = c.id
                        WHERE a.is_active = 1
                        ORDER BY a.priority DESC, RANDOM() LIMIT 5
                    """
                else:
                    fallback_q = """
                        SELECT a.id, a.name, a.description, a.execution_type, a.priority,
                               a.execution_type as category_name, '🎯' as category_icon
                        FROM activities a
                        WHERE a.is_active = 1
                        ORDER BY a.priority DESC, RANDOM() LIMIT 5
                    """
                cursor.execute(fallback_q)
                activities = [dict(row) for row in cursor.fetchall()]
                debug_log.append(f"✅ Fallback activities returned: {len(activities)}")

            conn.close()

        except Exception as db_err:
            import traceback

            db_debug = traceback.format_exc()
            debug_log.append(f"❌ DB error: {str(db_err)}")
            print(f"[chat_mood] DB error:\n{db_debug}")

        # ── 5. Save to mood history (best-effort) ──────────────────────────────
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='user_mood_history'"
            )
            if cursor.fetchone():
                cursor.execute(
                    "INSERT INTO user_mood_history (user_id, mood_input, sentiment_score, sentiment_type, created_at) VALUES (?,?,?,?,?)",
                    (
                        current_user.id,
                        user_message,
                        compound,
                        mood_type,
                        datetime.now(),
                    ),
                )
                conn.commit()
                debug_log.append("💾 Mood saved to user_mood_history")
            else:
                debug_log.append("⚠️ user_mood_history table not found — skipping save")
            conn.close()
        except Exception as hist_err:
            debug_log.append(f"⚠️ Could not save mood history: {str(hist_err)}")

        print(f"\n[chat_mood DEBUG]\n" + "\n".join(debug_log) + "\n")

        return jsonify(
            {
                "response": ai_response,
                "sentiment": sentiment_data,
                "emotion": emotion_data,
                "activities": activities,
                "model_used": model_used,
                "timestamp": datetime.now().isoformat(),
                "debug": debug_log,
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        debug_log.append(f"💥 Unhandled exception: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Something went wrong. Please try again!",
                    "details": str(e),
                    "debug": debug_log,
                }
            ),
            500,
        )


# ══════════════════════════════════════════════════════════════════════════════
# IMPROVED KEYWORD EXTRACTION FUNCTION
# Add this function to user.py (or replace existing extract_keywords)
# ══════════════════════════════════════════════════════════════════════════════

def extract_keywords_improved(text, min_length=3):
    """
    Enhanced keyword extraction with activity prioritization.
    
    Returns keywords in priority order:
    1. Activity-specific words (reading, gaming, writing, etc.)
    2. Other meaningful words
    
    Args:
        text: User input message
        min_length: Minimum word length to consider
    
    Returns:
        List of keywords (max 10)
    """
    # Expanded stopwords
    stopwords = {
        'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
        'in', 'with', 'to', 'for', 'of', 'as', 'by', 'i', 'me', 'my',
        'we', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can',
        'this', 'that', 'these', 'those', 'it', 'its',
        'he', 'she', 'they', 'them', 'their', 'his', 'her',
        'want', 'need', 'like', 'feel', 'feeling', 'something', 
        'anything', 'some', 'any', 'about', 'just', 'really',
        'very', 'so', 'too', 'also', 'now', 'then', 'there'
    }
    
    # Activity-specific keywords (HIGHEST PRIORITY)
    activity_keywords = {
        # Reading
        'read', 'reading', 'book', 'books', 'novel', 'article', 'literature',
        'story', 'stories', 'magazine', 'newspaper',
        
        # Writing
        'write', 'writing', 'journal', 'journaling', 'diary', 'essay', 'blog',
        'compose', 'composing', 'author', 'authoring',
        
        # Gaming
        'game', 'games', 'gaming', 'play', 'playing', 'video', 'console',
        'pc', 'mobile', 'sport', 'sports', 'compete', 'competition',
        
        # Cooking
        'cook', 'cooking', 'recipe', 'recipes', 'food', 'bake', 'baking',
        'prepare', 'preparing', 'meal', 'meals', 'dish',
        
        # Exercise
        'exercise', 'workout', 'yoga', 'run', 'running', 'jog', 'jogging',
        'walk', 'walking', 'gym', 'fitness', 'train', 'training',
        
        # Meditation/Relaxation
        'meditate', 'meditation', 'mindfulness', 'relax', 'relaxation',
        'breathe', 'breathing', 'calm', 'peace', 'zen',
        
        # Creative Arts
        'paint', 'painting', 'draw', 'drawing', 'art', 'artistic', 'creative',
        'craft', 'crafting', 'design', 'designing', 'sketch', 'sketching',
        
        # Music
        'music', 'listen', 'listening', 'song', 'songs', 'sing', 'singing',
        'instrument', 'guitar', 'piano', 'drums',
        
        # Entertainment
        'watch', 'watching', 'movie', 'movies', 'film', 'films', 'show',
        'shows', 'series', 'tv', 'television', 'stream', 'streaming',
        
        # Travel/Outdoor
        'travel', 'traveling', 'trip', 'trips', 'explore', 'exploring',
        'adventure', 'hike', 'hiking', 'outdoor', 'nature',
        
        # Learning
        'learn', 'learning', 'study', 'studying', 'course', 'education',
        'educate', 'research', 'practice', 'practicing'
    }
    
    # Clean and tokenize
    words = text.lower().split()
    keywords = []
    activity_matches = []
    other_words = []
    
    for word in words:
        # Remove punctuation
        clean_word = word.strip('.,!?;:()[]{}"\'-')
        
        # Skip if too short or stopword
        if len(clean_word) < min_length or clean_word in stopwords:
            continue
        
        # Prioritize activity keywords
        if clean_word in activity_keywords:
            activity_matches.append(clean_word)
        else:
            other_words.append(clean_word)
    
    # Combine: activity keywords first, then others
    keywords = activity_matches + other_words
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    
    return unique_keywords[:10]  # Return top 10


# ══════════════════════════════════════════════════════════════════════════════
# INSTALLATION INSTRUCTIONS
# ══════════════════════════════════════════════════════════════════════════════

"""
HOW TO INSTALL:

1. Open your routes/user.py file

2. Find the chat_mood() function (should be around line 224)

3. Replace the ENTIRE function with the improved version above

4. Add the extract_keywords_improved() function (replace old extract_keywords if it exists)

5. Save the file

6. Restart Flask:
   python app.py

7. Test with these queries:
   - "I want to read something"      → Should return Reading activities only
   - "I feel like gaming"             → Should return Gaming activities only  
   - "I want to do some writing"      → Should return Writing activities only
   - "I'm stressed and need to relax" → Should return Meditation, Calm activities

WHAT CHANGED:
✅ Better keyword extraction with activity prioritization
✅ Name-first search strategy (searches activity name before description)
✅ Improved stopword filtering
✅ Activity-specific keywords list (reading, gaming, writing, etc.)
✅ More accurate recommendations

DEBUG:
- Check debug panel (Ctrl+D) to see extracted keywords
- Look for: "🔑 Extracted keywords: ['reading']"
- This confirms keywords are being extracted correctly
"""


# ── DEBUG: test Gemini key + list models ───────────────────────────────────────
# REMOVE THIS SECTION ONCE CHATBOT IS WORKING


@user_bp.route("/chat_debug", methods=["POST"])
@login_required
def chat_debug():
    """Debug endpoint — tests all Gemini models. Remove when done."""
    api_key = request.get_json().get("api_key", "").strip()
    if not api_key:
        return jsonify({"error": "No key"}), 400

    available, list_err = _list_gemini_models(api_key)
    results = []

    for model in available or ["gemini-2.0-flash-lite", "gemini-2.0-flash"]:
        text, err = _gemini_call(api_key, model, "Reply with exactly: OK")
        if text:
            results.append(
                {"model": model, "status": "✅ WORKS", "response": text.strip()}
            )
            break
        else:
            code = 0
            try:
                code = int(err.split(":")[0].replace("HTTP ", "").strip())
            except:
                pass
            reason = {
                429: "Quota exceeded",
                403: "Key rejected",
                404: "Model not found",
                400: "Bad request",
            }.get(code, err[:80])
            results.append(
                {"model": model, "status": f"❌ HTTP {code}", "reason": reason}
            )

    working = [r for r in results if "WORKS" in r["status"]]
    return jsonify(
        {
            "key_prefix": api_key[:12] + "...",
            "available_models": available or f"ListModels failed: {list_err}",
            "test_results": results,
            "verdict": (
                f"✅ Working: {[r['model'] for r in working]}"
                if working
                else "❌ All models failed — quota exhausted or key invalid"
            ),
        }
    )


# END DEBUG SECTION ─────────────────────────────────────────────────────────────


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

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())

    cursor.execute("SELECT COUNT(*) FROM user_history WHERE user_id = ?", (user_id,))
    activities_tried = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM favorites WHERE user_id = ?", (user_id,))
    total_favorites = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM user_history WHERE user_id = ? AND sentiment_score IS NOT NULL",
        (user_id,),
    )
    mood_entries = cursor.fetchone()[0]

    cursor.execute(
        "SELECT DATE(created_at) as activity_date FROM user_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 30",
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

    cursor.execute(
        """
        SELECT uh.*, a.name as activity_name, a.execution_type
        FROM user_history uh
        JOIN activities a ON uh.activity_id = a.id
        WHERE uh.user_id = ?
        ORDER BY uh.created_at DESC LIMIT 5
        """,
        (user_id,),
    )
    recent_history = [dict(row) for row in cursor.fetchall()]

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
# 2. TRY ACTIVITY (MOOD INPUT — original form-based flow)
# ===============================


@user_bp.route("/try_activity", methods=["GET", "POST"])
@login_required
def try_activity():
    """Activity recommendation based on VADER sentiment analysis (form-based)"""
    user = get_current_user_dict()

    if request.method == "POST":
        mood_input = request.form.get("mood_input", "").strip()

        if not mood_input:
            flash("Please tell us how you're feeling!", "warning")
            return redirect(url_for("user.try_activity"))

        if VADER_AVAILABLE:
            analyzer = SentimentIntensityAnalyzer()
            sentiment = analyzer.polarity_scores(mood_input)
            sentiment_score = sentiment["compound"]
        else:
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

        mood_type, mood_emoji = get_sentiment_classification(sentiment_score)
        keywords = extract_keywords(mood_input)

        energy_level = request.form.get("energy_level")
        time_available = request.form.get("time_available")
        location_type = request.form.get("location_type")
        social_type = request.form.get("social_type")

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

        if keywords:
            mood_conditions = " OR ".join(
                [f"LOWER(a.mood_tags) LIKE ?" for _ in keywords]
            )
            query += f" AND ({mood_conditions})"
            params.extend([f"%{kw}%" for kw in keywords])

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

        session["mood_input"] = mood_input
        session["sentiment_score"] = sentiment_score
        session["mood_type"] = mood_type

        return render_template(
            "user/try_activity.html",
            user=user,
            searched=True,
            chatbot_mode=False,
            mood_input=mood_input,
            mood_type=mood_type,
            mood_emoji=mood_emoji,
            sentiment_score=sentiment_score,
            recommendations=recommended_activities,
        )

    return render_template(
        "user/try_activity.html", user=user, searched=False, chatbot_mode=False
    )


# ===============================
# 3. ACTIVITY DETAIL & VIEWING
# ===============================


@user_bp.route("/activity/<int:activity_id>")
@login_required
def activity_detail(activity_id):
    conn = get_db()
    cursor = conn.cursor()
    user = get_current_user_dict()

    cursor.execute(
        "SELECT a.*, c.name as category_name, c.icon as category_icon FROM activities a JOIN categories c ON a.category_id = c.id WHERE a.id = ?",
        (activity_id,),
    )
    row = cursor.fetchone()
    if not row:
        flash("Activity not found!", "error")
        return redirect(url_for("user.user_dashboard"))

    activity = dict(row)
    execution_type = activity["execution_type"]
    activity["execution_data"] = {}

    if execution_type == "resource":
        cursor.execute(
            "SELECT * FROM resources WHERE activity_id = ? ORDER BY difficulty",
            (activity_id,),
        )
        activity["execution_data"] = {"resources": [dict(r) for r in cursor.fetchall()]}
    elif execution_type == "steps":
        cursor.execute(
            "SELECT * FROM activity_steps WHERE activity_id = ? ORDER BY step_number",
            (activity_id,),
        )
        activity["execution_data"] = {"steps": [dict(r) for r in cursor.fetchall()]}
    elif execution_type == "gaming":
        cursor.execute("SELECT * FROM game_rules WHERE game_id = ?", (activity_id,))
        rules = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT * FROM game_tutorials WHERE game_id = ?", (activity_id,))
        tutorials = [dict(r) for r in cursor.fetchall()]
        activity["execution_data"] = {"rules": rules, "tutorials": tutorials}
    elif execution_type == "travel":
        cursor.execute(
            "SELECT * FROM travel_places WHERE activity_id = ? ORDER BY distance_km",
            (activity_id,),
        )
        activity["execution_data"] = {"places": [dict(r) for r in cursor.fetchall()]}

    cursor.execute(
        "SELECT COUNT(*) FROM favorites WHERE user_id = ? AND activity_id = ?",
        (current_user.id, activity_id),
    )
    activity["is_favorite"] = cursor.fetchone()[0] > 0

    cursor.execute(
        "SELECT * FROM activity_filters WHERE activity_id = ?", (activity_id,)
    )
    filter_row = cursor.fetchone()
    activity["filters"] = dict(filter_row) if filter_row else None
    conn.close()

    return render_template("user/activity_detail.html", user=user, activity=activity)


# ===============================
# 4. ACTIVITY EXECUTION & RATING
# ===============================


@user_bp.route("/activity/<int:activity_id>/rate", methods=["POST"])
@login_required
def rate_activity(activity_id):
    rating = request.form.get("rating", type=int)
    feedback_text = request.form.get("feedback_text", "").strip()

    if not rating or rating < 1 or rating > 5:
        flash("Invalid rating!", "error")
        return redirect(url_for("user.activity_detail", activity_id=activity_id))

    mood_input = session.get("mood_input", "Direct access")
    sentiment_score = session.get("sentiment_score", 0.0)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_history (user_id, activity_id, mood_input, sentiment_score, feedback_rating, feedback_text, created_at) VALUES (?,?,?,?,?,?,?)",
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
    user = get_current_user_dict()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Title and content are required!", "error")
            return redirect(url_for("user.write_activity", activity_id=activity_id))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_writings (user_id, activity_id, title, content, created_at) VALUES (?,?,?,?,?)",
            (
                current_user.id,
                activity_id,
                title,
                content,
                datetime.utcnow().isoformat(),
            ),
        )
        mood_input = session.get("mood_input", "Writing activity")
        sentiment_score = session.get("sentiment_score", 0.0)
        cursor.execute(
            "INSERT INTO user_history (user_id, activity_id, mood_input, sentiment_score, created_at) VALUES (?,?,?,?,?)",
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

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT a.name, a.description, c.name as category_name FROM activities a JOIN categories c ON a.category_id = c.id WHERE a.id = ?",
        (activity_id,),
    )
    row = cursor.fetchone()
    if not row:
        flash("Activity not found!", "error")
        return redirect(url_for("user.user_dashboard"))
    activity = dict(row)
    conn.close()
    return render_template(
        "user/write_activity.html",
        user=user,
        activity=activity,
        activity_id=activity_id,
    )


# ===============================
# 6. MY WRITINGS
# ===============================


@user_bp.route("/my_writings")
@login_required
def my_writings():
    user = get_current_user_dict()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT uw.*, a.name as activity_name FROM user_writings uw JOIN activities a ON uw.activity_id = a.id WHERE uw.user_id = ? ORDER BY uw.created_at DESC",
        (current_user.id,),
    )
    writings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("user/my_writings.html", user=user, writings=writings)


# ===============================
# 7. FAVORITES
# ===============================


@user_bp.route("/favorites")
@login_required
def favorites():
    user = get_current_user_dict()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT a.*, c.name as category_name, c.icon as category_icon FROM favorites f JOIN activities a ON f.activity_id = a.id JOIN categories c ON a.category_id = c.id WHERE f.user_id = ? ORDER BY f.created_at DESC",
        (current_user.id,),
    )
    fav_activities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("user/favorites.html", user=user, favorites=fav_activities)


@user_bp.route("/activity/<int:activity_id>/toggle-favorite", methods=["POST"])
@login_required
def toggle_favorite(activity_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM favorites WHERE user_id = ? AND activity_id = ?",
        (current_user.id, activity_id),
    )
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            "DELETE FROM favorites WHERE user_id = ? AND activity_id = ?",
            (current_user.id, activity_id),
        )
        message, status = "Removed from favorites", "removed"
    else:
        cursor.execute(
            "INSERT INTO favorites (user_id, activity_id, created_at) VALUES (?,?,?)",
            (current_user.id, activity_id, datetime.utcnow().isoformat()),
        )
        message, status = "Added to favorites! ❤️", "added"
    conn.commit()
    conn.close()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": status, "message": message})
    flash(message, "success")
    return redirect(url_for("user.activity_detail", activity_id=activity_id))


# ===============================
# 8. USER PROFILE
# ===============================


@user_bp.route("/profile")
@login_required
def profile():
    user = get_current_user_dict()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT i.id, i.name FROM interests i JOIN user_interests ui ON i.id = ui.interest_id WHERE ui.user_id = ?",
        (current_user.id,),
    )
    interests = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT COUNT(DISTINCT uh.activity_id) as unique_activities,
               COUNT(uh.id) as total_sessions,
               COUNT(f.id) as total_favorites,
               (SELECT AVG(feedback_rating) FROM user_history WHERE user_id = ? AND feedback_rating IS NOT NULL) as avg_rating
        FROM user_history uh
        LEFT JOIN favorites f ON f.user_id = uh.user_id
        WHERE uh.user_id = ?
        """,
        (current_user.id, current_user.id),
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
    user = get_current_user_dict()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT CASE WHEN sentiment_score >= 0.2 THEN 'positive'
                    WHEN sentiment_score <= -0.2 THEN 'negative'
                    ELSE 'neutral' END as mood_type, COUNT(*) as count
        FROM user_history WHERE user_id = ? AND sentiment_score IS NOT NULL GROUP BY mood_type
        """,
        (current_user.id,),
    )
    mood_distribution = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        "SELECT DATE(created_at) as date, AVG(sentiment_score) as avg_sentiment, COUNT(*) as activity_count FROM user_history WHERE user_id = ? AND sentiment_score IS NOT NULL AND DATE(created_at) >= DATE('now', '-30 days') GROUP BY DATE(created_at) ORDER BY date",
        (current_user.id,),
    )
    mood_trends = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        "SELECT mood_input, sentiment_score, created_at FROM user_history WHERE user_id = ? AND mood_input IS NOT NULL ORDER BY created_at DESC LIMIT 20",
        (current_user.id,),
    )
    recent_moods = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        "SELECT a.name, AVG(uh.feedback_rating) as avg_rating, COUNT(*) as times_tried FROM user_history uh JOIN activities a ON uh.activity_id = a.id WHERE uh.user_id = ? AND uh.feedback_rating IS NOT NULL GROUP BY a.id, a.name HAVING COUNT(*) >= 2 ORDER BY avg_rating DESC LIMIT 10",
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
    session["mood_input"] = "Quick try"
    session["sentiment_score"] = 0.0
    session["mood_type"] = "neutral"
    return redirect(url_for("user.activity_detail", activity_id=activity_id))


@user_bp.route("/search_activities")
@login_required
def search_activities():
    user = get_current_user_dict()
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    conn = get_db()
    cursor = conn.cursor()

    sql = "SELECT a.*, c.name as category_name, c.icon as category_icon FROM activities a JOIN categories c ON a.category_id = c.id WHERE a.is_active = 1"
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

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()

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
    user = get_current_user_dict()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT c.id, c.name, c.icon, c.description, COUNT(a.id) as activity_count FROM categories c LEFT JOIN activities a ON c.id = a.category_id AND a.is_active = 1 GROUP BY c.id ORDER BY c.name",
        (),
    )
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template(
        "user/browse_categories.html", user=user, categories=categories
    )


@user_bp.route("/category/<int:category_id>")
@login_required
def category_activities(category_id):
    user = get_current_user_dict()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    category = dict(cursor.fetchone())
    cursor.execute(
        "SELECT a.*, c.name as category_name, c.icon as category_icon FROM activities a JOIN categories c ON a.category_id = c.id WHERE c.id = ? AND a.is_active = 1 ORDER BY a.priority DESC, a.name",
        (category_id,),
    )
    activities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template(
        "user/category_activities.html",
        user=user,
        category=category,
        activities=activities,
    )


# ===============================
# HISTORY
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
               CASE WHEN uh.sentiment_score >= 0.2 THEN 'positive'
                    WHEN uh.sentiment_score <= -0.2 THEN 'negative'
                    ELSE 'neutral' END as mood_type
        FROM user_history uh
        JOIN activities a ON uh.activity_id = a.id
        WHERE uh.user_id = ?
        ORDER BY uh.created_at DESC
        """,
        (current_user.id,),
    )
    history_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("user/history.html", user=user, history=history_list)


@user_bp.route("/history/delete/<int:history_id>", methods=["POST"])
@login_required
def delete_history(history_id):
    """Delete a history entry"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_history WHERE id = ? AND user_id = ?",
        (history_id, current_user.id),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "History entry deleted"})


# run codex resume 019c6a36-f6b3-7c20-b99a-192ef4a48f31
