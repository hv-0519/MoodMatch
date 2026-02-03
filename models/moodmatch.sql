-- ============================================
-- MOODMATCH DATABASE SCHEMA
-- Simple ML (VADER) Ready
-- Keeps existing essential tables + adds new ones
-- ============================================

PRAGMA foreign_keys = ON;

-- ============================================
-- DROP OLD TABLES (Clean slate)
-- ============================================
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS user_history;
DROP TABLE IF EXISTS user_content;
DROP TABLE IF EXISTS user_writings;
DROP TABLE IF EXISTS activity_places;
DROP TABLE IF EXISTS activity_rules;
DROP TABLE IF EXISTS activity_resources;
DROP TABLE IF EXISTS activity_steps;
DROP TABLE IF EXISTS user_interests;
DROP TABLE IF EXISTS interests;
DROP TABLE IF EXISTS interest_categories;
DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS users;

-- Remove complex tables we don't need for SIMPLE ML
DROP TABLE IF EXISTS domains;
DROP TABLE IF EXISTS moods;
DROP TABLE IF EXISTS activity_domains;
DROP TABLE IF EXISTS activity_moods;
DROP TABLE IF EXISTS activity_filters;

PRAGMA foreign_keys = ON;

-- ============================================
-- CORE TABLES (Your existing 6 tables - KEPT AS-IS)
-- ============================================

-- 1. USERS TABLE
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
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
    profile_picture TEXT DEFAULT 'default.png',
    password_hash TEXT NOT NULL,
    reset_code TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. ADMINS TABLE
CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. INTEREST CATEGORIES (for user registration)
CREATE TABLE interest_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- 4. INTERESTS (specific interests under categories)
CREATE TABLE interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES interest_categories(id) ON DELETE CASCADE
);

-- 5. USER INTERESTS (junction table)
CREATE TABLE user_interests (
    user_id INTEGER NOT NULL,
    interest_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, interest_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
);

-- 6. ACTIVITIES (Master activity table with VADER mood tags)
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    execution_type TEXT NOT NULL, -- 'writing', 'reading', 'gaming', 'cooking', 'travel', etc.
    description TEXT,
    mood_tags TEXT NOT NULL, -- 'happy,energetic' or 'sad,calm,anxious' (for VADER matching)
    
    -- Filters for activity recommendations
    energy_level TEXT, -- 'low', 'medium', 'high'
    location_type TEXT, -- 'indoor', 'outdoor', 'both'
    social_type TEXT, -- 'solo', 'group', 'both'
    min_time INTEGER, -- minutes
    max_time INTEGER,
    min_budget INTEGER, -- in rupees or dollars
    max_budget INTEGER,
    
    is_active INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- ============================================
-- NEW TABLES (Added for better organization)
-- ============================================

-- 7. CATEGORIES (7 Mood Categories from requirements)
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE, -- 'Creative Moods', 'Intellectual', 'Gaming', etc.
    description TEXT,
    icon TEXT, -- emoji or icon class
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. ACTIVITY STEPS (for cooking, DIY, photography with step-by-step guide)
CREATE TABLE activity_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    step_text TEXT NOT NULL,
    video_link TEXT, -- YouTube link for cooking/DIY
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- 9. ACTIVITY RESOURCES (for reading, learning - books, tutorials, courses)
CREATE TABLE activity_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    resource_type TEXT NOT NULL, -- 'book', 'article', 'course', 'tutorial', 'documentary'
    link TEXT, -- external link or 'free' if available in system
    difficulty TEXT, -- 'beginner', 'intermediate', 'advanced'
    is_free INTEGER DEFAULT 0, -- 1 = free, 0 = paid
    price INTEGER,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- 10. ACTIVITY RULES (for games, sports with rules and requirements)
CREATE TABLE activity_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    rule_type TEXT, -- 'indoor', 'outdoor', 'general'
    players_min INTEGER,
    players_max INTEGER,
    rule_text TEXT NOT NULL,
    equipment_needed TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- 11. ACTIVITY PLACES (for travel with distance and budget info)
CREATE TABLE activity_places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    place_type TEXT, -- 'cafe', 'library', 'park', 'historical', 'adventure'
    distance_type TEXT, -- 'short', 'medium', 'long'
    distance_km INTEGER,
    days_required INTEGER,
    budget_estimate INTEGER,
    description TEXT,
    location TEXT,
    google_maps_link TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- 12. USER WRITINGS (store user's written content)
CREATE TABLE user_writings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    is_public INTEGER DEFAULT 1, -- 1 = public, 0 = private
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- 13. USER CONTENT (for drawings, photos, other saved work)
CREATE TABLE user_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL, -- 'drawing', 'photography', 'design', etc.
    title TEXT,
    file_path TEXT, -- path to uploaded file
    description TEXT,
    is_public INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- 14. USER HISTORY (track what users did - for VADER and future HYBRID ML)
CREATE TABLE user_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    mood_input TEXT, -- user's original mood text ("I'm feeling sad")
    sentiment_score REAL, -- VADER compound score (-1 to +1)
    feedback_rating INTEGER, -- 1-5 stars (for future hybrid ML)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- 15. FAVORITES (user's favorite activities)
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, activity_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- ============================================
-- INDEXES (for fast queries)
-- ============================================

-- User lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Activity lookups
CREATE INDEX idx_activities_category ON activities(category_id);
CREATE INDEX idx_activities_execution_type ON activities(execution_type);
CREATE INDEX idx_activities_active_priority ON activities(is_active, priority);
CREATE INDEX idx_activities_mood_tags ON activities(mood_tags);

-- History lookups
CREATE INDEX idx_user_history_user ON user_history(user_id);
CREATE INDEX idx_user_history_activity ON user_history(activity_id);
CREATE INDEX idx_user_history_created ON user_history(created_at);

-- Content lookups
CREATE INDEX idx_activity_steps_activity ON activity_steps(activity_id);
CREATE INDEX idx_activity_resources_activity ON activity_resources(activity_id);
CREATE INDEX idx_activity_rules_activity ON activity_rules(activity_id);
CREATE INDEX idx_activity_places_activity ON activity_places(activity_id);

-- User content lookups
CREATE INDEX idx_user_writings_user ON user_writings(user_id);
CREATE INDEX idx_user_content_user ON user_content(user_id);
CREATE INDEX idx_favorites_user ON favorites(user_id);

-- ============================================
-- SEED DATA
-- ============================================

-- Insert Admin (username: admin, password: admin123)
-- Password hash for 'admin123' using werkzeug (you'll generate this in Python)
INSERT INTO admins (username, password_hash) 
VALUES ('admin', 'pbkdf2:sha256:600000$placeholder$hash_will_be_generated_in_python');

-- Insert 7 Main Categories
INSERT INTO categories (name, description, icon) VALUES 
('Creative Moods', 'Express yourself through art, writing, and creativity', '🎨'),
('Intellectual', 'Learn, read, and expand your knowledge', '📚'),
('Gaming & Entertainment', 'Play games and enjoy digital entertainment', '🎮'),
('Physical & Adventure', 'Get active with sports and outdoor activities', '🏃'),
('Travel & Exploration', 'Discover new places and experiences', '✈️'),
('Lifestyle & Productivity', 'Organize life and develop healthy habits', '🌿'),
('Social Interaction', 'Connect with friends and community', '👥');

-- Insert Interest Categories (for registration)
INSERT INTO interest_categories (name, description) VALUES 
('Creative', 'Artistic and expressive activities'),
('Lifestyle', 'Daily life and personal development'),
('Action', 'Physical and energetic activities');

-- Insert Interests (linked to interest categories)
INSERT INTO interests (category_id, name) VALUES 
(1, 'writing'), (1, 'drawing'), (1, 'photography'), (1, 'music'), (1, 'design'),
(2, 'reading'), (2, 'cooking'), (2, 'gardening'), (2, 'travel'), (2, 'journaling'),
(3, 'gaming'), (3, 'sports'), (3, 'fitness'), (3, 'hiking'), (3, 'cycling');

-- Insert Sample Activities (with VADER mood tags)

-- CREATIVE MOODS (category_id = 1)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget) VALUES
(1, 'Writing', 'writing', 'Express your thoughts through words', 'sad,calm,reflective,creative,happy', 'low', 'indoor', 'solo', 15, 120, 0, 0),
(1, 'Drawing / Art', 'drawing', 'Create visual art and illustrations', 'creative,calm,focused,happy', 'low', 'indoor', 'solo', 30, 180, 100, 5000),
(1, 'Music Creation', 'music', 'Compose or play music', 'happy,creative,energetic,calm', 'medium', 'indoor', 'both', 20, 120, 500, 50000),
(1, 'Photography', 'photography', 'Capture moments through lens', 'creative,happy,adventurous', 'medium', 'outdoor', 'solo', 30, 180, 5000, 100000),
(1, 'Journaling', 'journaling', 'Reflect and organize your thoughts', 'sad,anxious,calm,reflective', 'low', 'indoor', 'solo', 10, 60, 0, 500);

-- INTELLECTUAL (category_id = 2)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget) VALUES
(2, 'Reading', 'reading', 'Dive into books and stories', 'calm,curious,sad,happy', 'low', 'indoor', 'solo', 20, 240, 0, 2000),
(2, 'Research', 'research', 'Explore topics in depth', 'curious,focused,motivated', 'medium', 'indoor', 'solo', 30, 300, 0, 5000),
(2, 'Learning New Skills', 'learning', 'Master new abilities', 'motivated,curious,focused', 'medium', 'both', 'solo', 30, 180, 0, 10000),
(2, 'Documentaries', 'documentary', 'Watch educational content', 'curious,calm,bored', 'low', 'indoor', 'both', 45, 180, 0, 1000);

-- GAMING (category_id = 3)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget) VALUES
(3, 'Mobile Games', 'gaming_mobile', 'Play games on phone', 'bored,stressed,happy', 'low', 'indoor', 'solo', 10, 120, 0, 5000),
(3, 'PC Games', 'gaming_pc', 'Immersive computer gaming', 'excited,happy,bored,stressed', 'low', 'indoor', 'both', 30, 300, 1000, 100000),
(3, 'Board Games', 'gaming_board', 'Traditional board games', 'happy,social,bored', 'low', 'indoor', 'group', 30, 180, 500, 5000),
(3, 'Puzzles', 'puzzles', 'Solve brain teasers', 'calm,focused,bored', 'low', 'indoor', 'solo', 15, 120, 100, 2000);

-- PHYSICAL (category_id = 4)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget) VALUES
(4, 'Hiking', 'hiking', 'Explore nature trails', 'adventurous,energetic,stressed', 'high', 'outdoor', 'both', 60, 480, 0, 2000),
(4, 'Cycling', 'cycling', 'Ride a bicycle', 'energetic,happy,stressed', 'high', 'outdoor', 'both', 30, 180, 2000, 50000),
(4, 'Gym', 'gym', 'Workout and exercise', 'motivated,energetic,stressed,angry', 'high', 'indoor', 'solo', 45, 120, 500, 5000),
(4, 'Dance', 'dance', 'Move to the rhythm', 'happy,energetic,excited', 'high', 'both', 'both', 30, 120, 0, 5000),
(4, 'Sports', 'sports', 'Play team or solo sports', 'energetic,competitive,happy', 'high', 'outdoor', 'group', 60, 180, 500, 10000);

-- TRAVEL (category_id = 5)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget) VALUES
(5, 'Local Cafes', 'travel_short', 'Visit nearby cafes', 'calm,social,bored', 'low', 'outdoor', 'both', 30, 180, 200, 2000),
(5, 'Road Trips', 'travel_long', 'Long distance adventures', 'adventurous,excited,happy', 'medium', 'outdoor', 'both', 480, 4320, 5000, 50000),
(5, 'Historical Places', 'travel_medium', 'Explore heritage sites', 'curious,calm,adventurous', 'medium', 'outdoor', 'both', 120, 480, 500, 5000);

-- LIFESTYLE (category_id = 6)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget) VALUES
(6, 'Cooking', 'cooking', 'Prepare delicious meals', 'creative,happy,calm', 'medium', 'indoor', 'both', 30, 120, 200, 2000),
(6, 'Gardening', 'gardening', 'Tend to plants', 'calm,peaceful,therapeutic', 'medium', 'outdoor', 'solo', 30, 180, 500, 5000),
(6, 'Self-Care', 'selfcare', 'Pamper yourself', 'stressed,sad,anxious', 'low', 'indoor', 'solo', 30, 120, 100, 5000),
(6, 'Organizing', 'organizing', 'Declutter and clean', 'motivated,stressed,focused', 'medium', 'indoor', 'solo', 30, 240, 0, 2000);

-- SOCIAL (category_id = 7)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget) VALUES
(7, 'Meeting Friends', 'social_meetup', 'Spend time with friends', 'happy,social,lonely,sad', 'medium', 'both', 'group', 60, 300, 500, 5000),
(7, 'Local Events', 'social_events', 'Attend community events', 'social,curious,bored', 'medium', 'outdoor', 'group', 120, 360, 0, 3000),
(7, 'Volunteering', 'social_volunteer', 'Give back to community', 'motivated,compassionate,happy', 'medium', 'outdoor', 'group', 120, 480, 0, 0);

-- ============================================
-- Sample Activity Content (Rules, Steps, Resources, Places)
-- ============================================

-- WRITING: No additional tables needed (user creates content directly)

-- READING: Sample Resources
INSERT INTO activity_resources (activity_id, title, resource_type, link, difficulty, is_free, description) VALUES
(6, 'The Alchemist', 'book', 'https://www.amazon.com/Alchemist-Paulo-Coelho/dp/0062315005', 'beginner', 0, 'A philosophical novel about following your dreams'),
(6, 'Atomic Habits', 'book', 'free', 'intermediate', 1, 'Transform your life with tiny changes'),
(6, '1984', 'book', 'https://www.amazon.com/1984-Signet-Classics-George-Orwell/dp/0451524934', 'intermediate', 0, 'Dystopian classic by George Orwell');

-- COOKING: Sample Steps with YouTube
INSERT INTO activity_steps (activity_id, step_number, step_text, video_link) VALUES
(25, 1, 'Gather ingredients: pasta, tomatoes, garlic, olive oil, basil', 'https://www.youtube.com/watch?v=sample_pasta'),
(25, 2, 'Boil water and cook pasta for 8-10 minutes', NULL),
(25, 3, 'Sauté garlic in olive oil, add chopped tomatoes', NULL),
(25, 4, 'Mix cooked pasta with sauce, garnish with fresh basil', NULL);

-- BOARD GAMES: Sample Rules
INSERT INTO activity_rules (activity_id, rule_type, players_min, players_max, rule_text, equipment_needed) VALUES
(11, 'indoor', 2, 4, 'Each player draws 7 cards. First player to get rid of all cards wins!', 'UNO card deck'),
(11, 'indoor', 2, 6, 'Buy properties, build houses, bankrupt opponents to win!', 'Monopoly board, dice, tokens, money');

-- MOBILE GAMES: Sample Rules
INSERT INTO activity_rules (activity_id, rule_type, players_min, players_max, rule_text, equipment_needed) VALUES
(9, 'indoor', 1, 1, 'Match 3 or more candies to clear levels. Complete objectives before running out of moves!', 'Smartphone with game installed'),
(9, 'indoor', 1, 100, 'Build base, train troops, attack other players. Join clan for team battles!', 'Smartphone with internet');

-- HIKING: Sample Places
INSERT INTO activity_places (activity_id, name, place_type, distance_type, distance_km, days_required, budget_estimate, description, location) VALUES
(13, 'Local Park Trail', 'park', 'short', 5, 0, 0, 'Easy 3km trail perfect for beginners', 'City Park'),
(13, 'Mountain Peak Trek', 'adventure', 'long', 150, 2, 5000, 'Challenging trek with breathtaking views', 'Himalayan Region');

-- TRAVEL: Sample Places
INSERT INTO activity_places (activity_id, name, place_type, distance_type, distance_km, days_required, budget_estimate, description, location) VALUES
(21, 'Corner Cafe', 'cafe', 'short', 2, 0, 300, 'Cozy coffee shop with great ambiance', 'Downtown'),
(22, 'Goa Beach Trip', 'adventure', 'long', 500, 3, 15000, 'Relaxing beach vacation with water sports', 'Goa, India'),
(23, 'Red Fort', 'historical', 'medium', 20, 0, 200, 'Iconic Mughal architecture monument', 'Delhi, India');

-- ============================================
-- Sample Users (for testing)
-- ============================================

-- Sample User 1 (password: user123)
INSERT INTO users (username, first_name, last_name, email, phone_number, gender, date_of_birth, password_hash) 
VALUES ('user_001', 'Rahul', 'Sharma', 'rahul@example.com', '9876543210', 'male', '1995-05-15', 'pbkdf2:sha256:600000$placeholder$hash_for_user123');

-- Sample User 2 (password: user123)
INSERT INTO users (username, first_name, last_name, email, phone_number, gender, date_of_birth, password_hash) 
VALUES ('user_002', 'Priya', 'Patel', 'priya@example.com', '9876543211', 'female', '1998-08-22', 'pbkdf2:sha256:600000$placeholder$hash_for_user123');

-- Sample User 3 (password: user123)
INSERT INTO users (username, first_name, last_name, email, phone_number, gender, date_of_birth, password_hash) 
VALUES ('user_003', 'Amit', 'Kumar', 'amit@example.com', '9876543212', 'male', '2000-12-10', 'pbkdf2:sha256:600000$placeholder$hash_for_user123');

-- Assign interests to users
INSERT INTO user_interests (user_id, interest_id) VALUES 
(1, 1), (1, 6), (1, 11), -- Rahul: writing, reading, gaming
(2, 2), (2, 7), (2, 9), -- Priya: drawing, cooking, travel
(3, 11), (3, 12), (3, 14); -- Amit: gaming, sports, hiking

-- Sample User History
INSERT INTO user_history (user_id, activity_id, mood_input, sentiment_score, feedback_rating) VALUES
(1, 1, 'feeling sad and lonely', -0.65, 5),
(1, 6, 'want something relaxing', 0.10, 4),
(2, 2, 'feeling creative today', 0.75, 5),
(3, 13, 'need some adventure', 0.80, 5);

-- Sample Favorites
INSERT INTO favorites (user_id, activity_id) VALUES
(1, 1), (1, 6), -- Rahul favorites: Writing, Reading
(2, 2), (2, 25), -- Priya favorites: Drawing, Cooking
(3, 9), (3, 13); -- Amit favorites: Mobile Games, Hiking

-- Sample User Writing
INSERT INTO user_writings (user_id, activity_id, title, content, is_public) VALUES
(1, 1, 'My Journey', 'Today I realized that life is about the small moments...', 1),
(2, 1, 'Art and Soul', 'Creativity flows when the mind is at peace...', 1);

INSERT OR IGNORE INTO user_history (user_id, activity_id, mood_input, sentiment_score, feedback_rating, created_at)
VALUES 
(1, 1, 'happy excited', 0.8, 5, datetime('now', '-5 days')),
(1, 2, 'sad lonely', -0.6, 4, datetime('now', '-4 days')),
(2, 1, 'stressed anxious', -0.4, 3, datetime('now', '-3 days')),
(2, 3, 'calm peaceful', 0.3, 5, datetime('now', '-2 days')),
(3, 4, 'energetic motivated', 0.7, 5, datetime('now', '-1 day')),
(1, 5, 'tired bored', -0.2, 2, datetime('now')),
(2, 2, 'happy content', 0.6, 4, datetime('now')),
(3, 1, 'anxious worried', -0.5, 3, datetime('now'));

INSERT OR IGNORE INTO favorites (user_id, activity_id, created_at)
VALUES 
(1, 1, datetime('now', '-3 days')),
(1, 2, datetime('now', '-2 days')),
(2, 1, datetime('now', '-1 day')),
(2, 3, datetime('now')),
(3, 4, datetime('now'));

-- ============================================
-- END OF SCHEMA
-- ============================================

PRAGMA foreign_keys = ON;