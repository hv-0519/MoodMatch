import sqlite3

DB_PATH = "models/mood.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ===============================
    # CORE TABLES (SAFE CREATE)
    # ===============================

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        execution_type TEXT NOT NULL,
        description TEXT,
        priority INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS activity_moods (
        activity_id INTEGER,
        mood_id INTEGER,
        weight INTEGER
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS activity_filters (
        activity_id INTEGER,
        min_time INTEGER,
        max_time INTEGER,
        min_budget INTEGER,
        max_budget INTEGER,
        energy_level TEXT,
        location_type TEXT,
        distance_type TEXT,
        social_type TEXT
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS activity_domains (
        activity_id INTEGER,
        domain_id INTEGER
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER,
        title TEXT,
        resource_type TEXT,
        link TEXT,
        difficulty TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS activity_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER,
        step_number INTEGER,
        step_text TEXT,
        video_link TEXT
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS game_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        rule_text TEXT
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS game_tutorials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        tutorial_link TEXT
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS travel_places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER,
        place_name TEXT,
        distance_km INTEGER,
        budget TEXT,
        description TEXT
    )
    """
    )

    # ===============================
    # WRITING (EDITOR)
    # ===============================
    cur.execute(
        """
    INSERT INTO activities (name, execution_type, description, priority, is_active)
    VALUES ('Writing', 'editor', 'Free writing activity', 5, 1)
    """
    )
    writing_id = cur.lastrowid

    cur.execute(
        """
    INSERT INTO activity_moods (activity_id, mood_id, weight)
    VALUES (?, ?, ?)
    """,
        (writing_id, 1, 9),
    )

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
        (writing_id, 15, 180, None, None, "Low", "Indoor", "Home", "Solo"),
    )

    # ===============================
    # READING (RESOURCE)
    # ===============================
    cur.execute(
        """
    INSERT INTO activities (name, execution_type, description, priority, is_active)
    VALUES ('Reading', 'resource', 'Recommended books/articles based on mood', 4, 1)
    """
    )
    reading_id = cur.lastrowid

    cur.execute(
        """
    INSERT INTO activity_moods (activity_id, mood_id, weight)
    VALUES (?, ?, ?)
    """,
        (reading_id, 1, 8),
    )

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
        (reading_id, 15, 120, None, None, "Low", "Indoor", "Home", "Solo"),
    )

    cur.execute(
        """
    INSERT INTO resources (activity_id, title, resource_type, link, difficulty)
    VALUES (?, ?, ?, ?, ?)
    """,
        (
            reading_id,
            "Atomic Habits",
            "Book",
            "https://example.com/atomic-habits",
            "Easy",
        ),
    )

    # ===============================
    # COOKING (STEPS)
    # ===============================
    cur.execute(
        """
    INSERT INTO activities (name, execution_type, description, priority, is_active)
    VALUES ('Cooking', 'steps', 'Cook a dish step by step', 4, 1)
    """
    )
    cooking_id = cur.lastrowid

    cur.execute(
        """
    INSERT INTO activity_steps
    (activity_id, step_number, step_text, video_link)
    VALUES (?, ?, ?, ?)
    """,
        (cooking_id, 1, "Prepare ingredients", None),
    )

    cur.execute(
        """
    INSERT INTO activity_steps
    (activity_id, step_number, step_text, video_link)
    VALUES (?, ?, ?, ?)
    """,
        (cooking_id, 2, "Heat pan and start cooking", None),
    )

    cur.execute(
        """
    INSERT INTO activity_steps
    (activity_id, step_number, step_text, video_link)
    VALUES (?, ?, ?, ?)
    """,
        (cooking_id, 3, "Serve hot", None),
    )

    # ===============================
    # GAME / SPORTS
    # ===============================
    cur.execute(
        """
    INSERT INTO activities (name, execution_type, description, priority, is_active)
    VALUES ('Badminton', 'game', 'Indoor/Outdoor sport', 3, 1)
    """
    )
    game_id = cur.lastrowid

    cur.execute(
        """
    INSERT INTO game_rules (game_id, rule_text)
    VALUES (?, ?)
    """,
        (game_id, "Score 21 points to win"),
    )

    cur.execute(
        """
    INSERT INTO game_rules (game_id, rule_text)
    VALUES (?, ?)
    """,
        (game_id, "Shuttle must pass over the net"),
    )

    cur.execute(
        """
    INSERT INTO game_tutorials (game_id, tutorial_link)
    VALUES (?, ?)
    """,
        (game_id, "https://youtube.com/badminton-tutorial"),
    )

    # ===============================
    # TRAVEL
    # ===============================
    cur.execute(
        """
    INSERT INTO activities (name, execution_type, description, priority, is_active)
    VALUES ('Travel', 'travel', 'Explore nearby places', 3, 1)
    """
    )
    travel_id = cur.lastrowid

    cur.execute(
        """
    INSERT INTO travel_places
    (activity_id, place_name, distance_km, budget, description)
    VALUES (?, ?, ?, ?, ?)
    """,
        (travel_id, "Lonavala", 90, "Medium", "Hill station near the city"),
    )

    cur.execute(
        """
INSERT INTO user_writings (user_id, activity_id, title, content)
VALUES (?, ?, ?, ?)
""",
        (
            1,  # 👈 test user_id (MUST match logged-in user)
            writing_id,  # Writing activity you already created
            "Initial Test Writing",
            "This writing is created by bootstrap for backend testing.",
        ),
    )

    conn.commit()
    conn.close()

    print("✅ MoodMatch DB bootstrap completed successfully")


if __name__ == "__main__":
    main()
