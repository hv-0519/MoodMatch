PRAGMA foreign_keys = ON;

-- DROP OLD TABLES
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS user_history;
DROP TABLE IF EXISTS user_preferences;
DROP TABLE IF EXISTS user_saved_files;
DROP TABLE IF EXISTS user_writings;
DROP TABLE IF EXISTS user_drawings;
DROP TABLE IF EXISTS game_rules;
DROP TABLE IF EXISTS game_tutorials;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS activity_steps;
DROP TABLE IF EXISTS travel_places;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

PRAGMA foreign_keys = ON;

-- USERS
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone_number TEXT,
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    date_of_birth DATE,
    street_address TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT,
    profile_picture TEXT,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users ADD COLUMN username TEXT;
ALTER TABLE users ADD COLUMN reset_code TEXT;

CREATE TABLE admins(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password_hash TEXT NOT NULL
);

CREATE TABLE interest_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);


CREATE TABLE interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES interest_categories(id)
);

CREATE TABLE user_interests (
    user_id INTEGER NOT NULL,
    interest_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, interest_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
);



-- 1. DOMAINS
CREATE TABLE domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- 2. MOODS
CREATE TABLE moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- 3. ACTIVITIES (MASTER TABLE)
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    execution_type TEXT NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. ACTIVITY ↔ DOMAIN (MANY TO MANY)
CREATE TABLE activity_domains (
    activity_id INTEGER,
    domain_id INTEGER,
    PRIMARY KEY (activity_id, domain_id),
    FOREIGN KEY (activity_id) REFERENCES activities(id),
    FOREIGN KEY (domain_id) REFERENCES domains(id)
);

-- 5. ACTIVITY ↔ MOOD (WEIGHTED)
CREATE TABLE activity_moods (
    activity_id INTEGER,
    mood_id INTEGER,
    weight INTEGER NOT NULL,
    PRIMARY KEY (activity_id, mood_id),
    FOREIGN KEY (activity_id) REFERENCES activities(id),
    FOREIGN KEY (mood_id) REFERENCES moods(id)
);

-- 6. ACTIVITY FILTERS
CREATE TABLE activity_filters (
    activity_id INTEGER PRIMARY KEY,
    min_time INTEGER,
    max_time INTEGER,
    min_budget INTEGER,
    max_budget INTEGER,
    energy_level TEXT,
    location_type TEXT,
    distance_type TEXT,
    social_type TEXT,
    FOREIGN KEY (activity_id) REFERENCES activities(id)
);

-- 7. ACTIVITY STEPS (COOKING / DIY / PHOTOGRAPHY)
CREATE TABLE activity_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER,
    step_number INTEGER,
    step_text TEXT,
    video_link TEXT,
    FOREIGN KEY (activity_id) REFERENCES activities(id)
);

-- 8. ACTIVITY RESOURCES (READING / LEARNING)
CREATE TABLE activity_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER,
    title TEXT,
    resource_type TEXT,
    link TEXT,
    difficulty TEXT,
    FOREIGN KEY (activity_id) REFERENCES activities(id)
);

-- 9. ACTIVITY RULES (GAMES / SPORTS)
CREATE TABLE activity_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER,
    rule_text TEXT,
    FOREIGN KEY (activity_id) REFERENCES activities(id)
);

-- 10. ACTIVITY PLACES (TRAVEL)
CREATE TABLE activity_places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER,
    name TEXT,
    distance_km INTEGER,
    days_required INTEGER,
    budget_estimate INTEGER,
    description TEXT,
    FOREIGN KEY (activity_id) REFERENCES activities(id)
);

-- 11. user_writings
CREATE TABLE user_writings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id)
);


-- ========= CORE LOOKUPS =========

-- Activities (active + priority based fetch)
CREATE INDEX idx_activities_active_priority
ON activities (is_active, priority);

-- Activities by execution type (writing, reading, travel, etc.)
CREATE INDEX idx_activities_execution_type
ON activities (execution_type);


-- ========= DOMAIN & MOOD MAPPING =========

-- Fast domain → activities lookup
CREATE INDEX idx_activity_domains_domain
ON activity_domains (domain_id);

-- Fast activity → domains lookup
CREATE INDEX idx_activity_domains_activity
ON activity_domains (activity_id);

-- Fast mood → activities lookup (MOST IMPORTANT for recommendations)
CREATE INDEX idx_activity_moods_mood
ON activity_moods (mood_id);

-- Ranking activities by mood weight
CREATE INDEX idx_activity_moods_weight
ON activity_moods (mood_id, weight DESC);


-- ========= FILTERING PERFORMANCE =========

-- Energy / location / distance filtering
CREATE INDEX idx_activity_filters_energy
ON activity_filters (energy_level);

CREATE INDEX idx_activity_filters_location
ON activity_filters (location_type);

CREATE INDEX idx_activity_filters_distance
ON activity_filters (distance_type);

CREATE INDEX idx_activity_filters_social
ON activity_filters (social_type);

-- Time & budget range filtering
CREATE INDEX idx_activity_filters_time
ON activity_filters (min_time, max_time);

CREATE INDEX idx_activity_filters_budget
ON activity_filters (min_budget, max_budget);


-- ========= CONTENT TABLES =========

-- Steps lookup
CREATE INDEX idx_activity_steps_activity
ON activity_steps (activity_id);

-- Resources lookup
CREATE INDEX idx_activity_resources_activity
ON activity_resources (activity_id);

-- Rules lookup
CREATE INDEX idx_activity_rules_activity
ON activity_rules (activity_id);

-- Travel places lookup
CREATE INDEX idx_activity_places_activity
ON activity_places (activity_id);
