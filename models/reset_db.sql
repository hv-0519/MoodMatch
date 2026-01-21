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



-- -- CATEGORIES
-- CREATE TABLE categories (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     domain TEXT NOT NULL
-- );

-- -- ACTIVITIES
-- CREATE TABLE activities (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     category_id INTEGER,
--     mood TEXT,
--     time_required TEXT,
--     budget TEXT,
--     energy_level TEXT,
--     location_type TEXT,
--     distance TEXT,
--     description TEXT,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (category_id) REFERENCES categories(id)
-- );

-- -- STEP BASED CONTENT (photography, video editing, cooking)
-- CREATE TABLE activity_steps (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     activity_id INTEGER,
--     step_number INTEGER,
--     step_text TEXT,
--     video_link TEXT,
--     FOREIGN KEY (activity_id) REFERENCES activities(id)
-- );

-- -- GAMES
-- CREATE TABLE games (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     category_id INTEGER,
--     FOREIGN KEY (category_id) REFERENCES categories(id)
-- );

-- CREATE TABLE game_rules (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     game_id INTEGER,
--     rule_text TEXT,
--     FOREIGN KEY (game_id) REFERENCES games(id)
-- );

-- CREATE TABLE game_tutorials (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     game_id INTEGER,
--     tutorial_link TEXT,
--     FOREIGN KEY (game_id) REFERENCES games(id)
-- );

-- -- TRAVEL
-- CREATE TABLE travel_places (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT,
--     trip_type TEXT,
--     distance_km INTEGER,
--     days_required INTEGER,
--     description TEXT
-- );

-- -- INTELLECTUAL RESOURCES
-- CREATE TABLE resources (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     category_id INTEGER,
--     title TEXT,
--     resource_type TEXT,
--     link TEXT,
--     difficulty TEXT,
--     FOREIGN KEY (category_id) REFERENCES categories(id)
-- );

-- -- USER GENERATED CONTENT
-- CREATE TABLE user_writings (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER,
--     title TEXT,
--     content TEXT,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES users(id)
-- );

-- CREATE TABLE user_drawings (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER,
--     file_path TEXT,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES users(id)
-- );

-- -- USER PREFERENCES
-- CREATE TABLE user_preferences (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER,
--     preference_key TEXT,
--     preference_value TEXT,
--     FOREIGN KEY (user_id) REFERENCES users(id)
-- );

-- -- USER HISTORY
-- CREATE TABLE user_history (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER,
--     activity_type TEXT,
--     reference_id INTEGER,
--     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES users(id)
-- );

-- -- FAVORITES
-- CREATE TABLE favorites (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER,
--     item_type TEXT,
--     item_id INTEGER,
--     added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES users(id)
-- );

-- -- USER SAVED FILES
-- CREATE TABLE user_saved_files (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER,
--     file_type TEXT,
--     file_path TEXT,
--     saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES users(id)
-- );
