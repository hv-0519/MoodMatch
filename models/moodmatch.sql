-- ============================================
-- MOODMATCH DATABASE SCHEMA - Complete & Clean
-- VADER Sentiment Analysis Ready
-- ============================================

PRAGMA foreign_keys = ON;

-- ============================================
-- DROP EXISTING TABLES
-- ============================================
DROP TABLE IF EXISTS user_writings;
DROP TABLE IF EXISTS user_content;
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS user_history;
DROP TABLE IF EXISTS travel_places;
DROP TABLE IF EXISTS game_tutorials;
DROP TABLE IF EXISTS game_rules;
DROP TABLE IF EXISTS activity_steps;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS activity_filters;
DROP TABLE IF EXISTS user_interests;
DROP TABLE IF EXISTS interests;
DROP TABLE IF EXISTS interest_categories;
DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS users;

-- ============================================
-- CREATE TABLES
-- ============================================

-- USERS
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT,
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    date_of_birth DATE,
    street_address TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT,
    profile_picture TEXT,
    bio TEXT,
    password_hash TEXT NOT NULL,
    reset_code TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ADMINS
CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CATEGORIES (7 main mood categories)
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- INTEREST CATEGORIES (for user registration)
CREATE TABLE interest_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- INTERESTS (specific interests under categories)
CREATE TABLE interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES interest_categories(id) ON DELETE CASCADE
);

-- USER INTERESTS (junction table)
CREATE TABLE user_interests (
    user_id INTEGER NOT NULL,
    interest_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, interest_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
);

-- ACTIVITIES (with VADER mood tags)
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    execution_type TEXT NOT NULL,
    description TEXT,
    mood_tags TEXT NOT NULL,
    energy_level TEXT,
    location_type TEXT,
    social_type TEXT,
    min_time INTEGER,
    max_time INTEGER,
    min_budget INTEGER,
    max_budget INTEGER,
    is_active INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 0,
    icon TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- ACTIVITY FILTERS (optional filters)
CREATE TABLE activity_filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    energy_level TEXT,
    min_time INTEGER,
    max_time INTEGER,
    location_type TEXT,
    social_type TEXT,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- RESOURCES (for reading/learning activities)
CREATE TABLE resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    link TEXT,
    difficulty TEXT,
    is_free INTEGER DEFAULT 0,
    price INTEGER,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- ACTIVITY STEPS (for cooking, DIY, photography)
CREATE TABLE activity_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    step_text TEXT NOT NULL,
    video_link TEXT,
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- GAME RULES (for games and sports)
CREATE TABLE game_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    rule_type TEXT,
    players_min INTEGER,
    players_max INTEGER,
    rule_text TEXT NOT NULL,
    equipment_needed TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- GAME TUTORIALS (separate from rules)
CREATE TABLE game_tutorials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    tutorial_link TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- TRAVEL PLACES (for travel activities)
CREATE TABLE travel_places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    place_name TEXT NOT NULL,
    place_type TEXT,
    distance_km INTEGER,
    distance_type TEXT,
    days_required INTEGER DEFAULT 0,
    budget TEXT,
    budget_estimate INTEGER,
    description TEXT,
    location TEXT,
    google_maps_link TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- USER HISTORY (tracks user activities with sentiment)
CREATE TABLE user_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    mood_input TEXT,
    sentiment_score REAL,
    feedback_rating INTEGER,
    feedback_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- FAVORITES (user's favorite activities)
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, activity_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- USER WRITINGS (store user's written content)
CREATE TABLE user_writings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    is_public INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- USER CONTENT (for drawings, photos, other saved work)
CREATE TABLE user_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    content_type TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    is_public INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- ============================================
-- CREATE INDEXES
-- ============================================
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_activities_category ON activities(category_id);
CREATE INDEX idx_activities_execution ON activities(execution_type);
CREATE INDEX idx_activities_active_priority ON activities(is_active, priority);
CREATE INDEX idx_activities_mood_tags ON activities(mood_tags);
CREATE INDEX idx_user_history_user ON user_history(user_id);
CREATE INDEX idx_user_history_activity ON user_history(activity_id);
CREATE INDEX idx_user_history_created ON user_history(created_at);
CREATE INDEX idx_activity_steps_activity ON activity_steps(activity_id);
CREATE INDEX idx_resources_activity ON resources(activity_id);
CREATE INDEX idx_game_rules_game ON game_rules(game_id);
CREATE INDEX idx_travel_places_activity ON travel_places(activity_id);
CREATE INDEX idx_user_writings_user ON user_writings(user_id);
CREATE INDEX idx_user_content_user ON user_content(user_id);
CREATE INDEX idx_favorites_user ON favorites(user_id);

-- ============================================
-- SEED DATA
-- ============================================

-- Insert Admin User
INSERT INTO admins (username, password_hash) VALUES
('admin', 'admin_password_placeholder'); -- Replace with actual bcrypt hash

-- Insert Categories
INSERT INTO categories (name, description, icon) VALUES 
('Creative Moods', 'Express yourself through art, writing, and creativity', '🎨'),
('Intellectual', 'Learn, read, and expand your knowledge', '📚'),
('Gaming & Entertainment', 'Play games and enjoy digital entertainment', '🎮'),
('Physical & Adventure', 'Get active with sports and outdoor activities', '🏃'),
('Travel & Exploration', 'Discover new places and experiences', '✈️'),
('Lifestyle & Productivity', 'Organize life and develop healthy habits', '🌿'),
('Social Interaction', 'Connect with friends and community', '👥');

-- Insert Interest Categories
INSERT INTO interest_categories (name, description) VALUES 
('Creative', 'Artistic and expressive activities'),
('Lifestyle', 'Daily life and personal development'),
('Action', 'Physical and energetic activities');

-- Insert Interests
INSERT INTO interests (category_id, name) VALUES 
(1, 'Writing'), (1, 'Drawing'), (1, 'Photography'), (1, 'Music'), (1, 'Design'),
(2, 'Reading'), (2, 'Cooking'), (2, 'Gardening'), (2, 'Travel'), (2, 'Journaling'),
(3, 'Gaming'), (3, 'Sports'), (3, 'Fitness'), (3, 'Hiking'), (3, 'Cycling');

-- Insert Sample Activities

-- CREATIVE MOODS (category_id = 1)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget, priority) VALUES
(1, 'Journaling', 'editor', 'Express your thoughts through personal writing', 'sad,anxious,stressed,calm,reflective', 'Low', 'Indoor', 'Solo', 10, 60, 0, 500, 90),
(1, 'Creative Writing', 'editor', 'Write stories, poems, or fiction', 'creative,happy,calm,inspired', 'Low', 'Indoor', 'Solo', 20, 120, 0, 0, 85),
(1, 'Drawing & Art', 'editor', 'Create visual art and illustrations', 'creative,calm,focused,happy', 'Low', 'Indoor', 'Solo', 30, 180, 100, 5000, 88),
(1, 'Photography', 'steps', 'Capture moments through lens', 'creative,happy,adventurous,curious', 'Medium', 'Outdoor', 'Solo', 30, 180, 5000, 100000, 82);

-- INTELLECTUAL (category_id = 2)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget, priority) VALUES
(2, 'Reading', 'resource', 'Dive into books and stories', 'calm,curious,sad,happy,bored', 'Low', 'Indoor', 'Solo', 20, 240, 0, 2000, 95),
(2, 'Meditation', 'steps', 'Find inner peace and mindfulness', 'stressed,anxious,angry,calm', 'Low', 'Indoor', 'Solo', 5, 60, 0, 0, 100),
(2, 'Research', 'resource', 'Explore topics in depth', 'curious,focused,motivated', 'Medium', 'Indoor', 'Solo', 30, 300, 0, 5000, 78),
(2, 'Documentaries', 'resource', 'Watch educational content', 'curious,calm,bored', 'Low', 'Indoor', 'Both', 45, 180, 0, 1000, 75);

-- GAMING (category_id = 3)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget, priority) VALUES
(3, 'Mobile Games', 'gaming', 'Play casual games on phone', 'bored,stressed,happy,relaxed', 'Low', 'Indoor', 'Solo', 10, 120, 0, 5000, 80),
(3, 'PC Games', 'gaming', 'Immersive computer gaming', 'excited,happy,bored,stressed', 'Low', 'Indoor', 'Both', 30, 300, 1000, 100000, 77),
(3, 'Board Games', 'gaming', 'Traditional board games', 'happy,social,bored', 'Low', 'Indoor', 'Small Group', 30, 180, 500, 5000, 78),
(3, 'Puzzles', 'gaming', 'Solve brain teasers', 'calm,focused,bored', 'Low', 'Indoor', 'Solo', 15, 120, 100, 2000, 72);

-- PHYSICAL (category_id = 4)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget, priority) VALUES
(4, 'Hiking', 'travel', 'Explore nature trails', 'adventurous,energetic,stressed,happy', 'High', 'Outdoor', 'Both', 60, 480, 0, 2000, 85),
(4, 'Cycling', 'steps', 'Ride a bicycle', 'energetic,happy,stressed,motivated', 'High', 'Outdoor', 'Both', 30, 180, 2000, 50000, 82),
(4, 'Yoga', 'steps', 'Stretch and find balance', 'stressed,tired,calm,peaceful', 'Medium', 'Indoor', 'Solo', 15, 90, 0, 5000, 88),
(4, 'Gym Workout', 'steps', 'Exercise and build strength', 'motivated,energetic,stressed,angry', 'High', 'Indoor', 'Solo', 45, 120, 500, 5000, 80),
(4, 'Dance', 'steps', 'Move to the rhythm', 'happy,energetic,excited', 'High', 'Both', 'Both', 30, 120, 0, 5000, 83);

-- TRAVEL (category_id = 5)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget, priority) VALUES
(5, 'Visit Cafes', 'travel', 'Explore local coffee spots', 'calm,social,bored,happy', 'Low', 'Outdoor', 'Both', 30, 180, 200, 2000, 85),
(5, 'Road Trips', 'travel', 'Long distance adventures', 'adventurous,excited,happy,free', 'Medium', 'Outdoor', 'Both', 480, 4320, 5000, 50000, 82),
(5, 'Historical Places', 'travel', 'Explore heritage sites', 'curious,calm,adventurous,interested', 'Medium', 'Outdoor', 'Both', 120, 480, 500, 5000, 78);

-- LIFESTYLE (category_id = 6)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget, priority) VALUES
(6, 'Cooking', 'steps', 'Prepare delicious meals', 'creative,happy,calm,focused', 'Medium', 'Indoor', 'Both', 30, 120, 200, 2000, 88),
(6, 'Gardening', 'steps', 'Tend to plants and nature', 'calm,peaceful,therapeutic,happy', 'Medium', 'Outdoor', 'Solo', 30, 180, 500, 5000, 75),
(6, 'Self-Care', 'steps', 'Pamper yourself', 'stressed,sad,anxious,tired', 'Low', 'Indoor', 'Solo', 30, 120, 100, 5000, 90),
(6, 'Organizing', 'steps', 'Declutter and clean spaces', 'motivated,stressed,focused', 'Medium', 'Indoor', 'Solo', 30, 240, 0, 2000, 70);

-- SOCIAL (category_id = 7)
INSERT INTO activities (category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, min_budget, max_budget, priority) VALUES
(7, 'Meeting Friends', 'travel', 'Spend quality time with friends', 'happy,social,lonely,sad,excited', 'Medium', 'Both', 'Small Group', 60, 300, 500, 5000, 87),
(7, 'Local Events', 'travel', 'Attend community events', 'social,curious,bored,excited', 'Medium', 'Outdoor', 'Large Group', 120, 360, 0, 3000, 76),
(7, 'Volunteering', 'travel', 'Give back to community', 'motivated,compassionate,happy,fulfilled', 'Medium', 'Outdoor', 'Large Group', 120, 480, 0, 0, 80);

-- Insert Sample Resources (for Reading activity)
INSERT INTO resources (activity_id, title, resource_type, link, difficulty, is_free, price, description) VALUES
(5, 'The Alchemist', 'book', 'https://www.amazon.com/Alchemist-Paulo-Coelho/dp/0062315005', 'beginner', 0, 299, 'A philosophical novel about following your dreams'),
(5, 'Atomic Habits', 'book', 'https://www.amazon.com/Atomic-Habits-James-Clear/dp/0735211299', 'intermediate', 0, 499, 'Transform your life with tiny changes'),
(5, '1984', 'book', 'https://www.amazon.com/1984-Signet-Classics-George-Orwell/dp/0451524934', 'intermediate', 0, 199, 'Dystopian classic by George Orwell'),
(7, 'Free Online Courses', 'course', 'https://www.coursera.org', 'beginner', 1, 0, 'Learn anything online for free');

-- Insert Sample Steps (Meditation, Yoga, Cooking)
INSERT INTO activity_steps (activity_id, step_number, step_text, video_link) VALUES
(6, 1, 'Find a quiet, comfortable space where you won''t be disturbed', NULL),
(6, 2, 'Sit in a comfortable position with your back straight', NULL),
(6, 3, 'Close your eyes and focus on your natural breathing', NULL),
(6, 4, 'When your mind wanders, gently bring focus back to your breath', NULL),
(6, 5, 'Continue for 5-20 minutes, gradually increasing duration', NULL),
(15, 1, 'Wear comfortable, stretchy clothing', NULL),
(15, 2, 'Start with Mountain Pose (Tadasana) - stand tall, feet together', NULL),
(15, 3, 'Move into Downward Dog - hands and feet on ground, hips high', NULL),
(15, 4, 'Flow through Cat-Cow poses for spine flexibility', NULL),
(15, 5, 'End with Corpse Pose (Savasana) for relaxation', NULL),
(24, 1, 'Gather ingredients: pasta, tomatoes, garlic, olive oil, basil', 'https://www.youtube.com/watch?v=sample'),
(24, 2, 'Boil salted water and cook pasta for 8-10 minutes until al dente', NULL),
(24, 3, 'In a pan, sauté minced garlic in olive oil until fragrant', NULL),
(24, 4, 'Add chopped tomatoes and cook for 15 minutes', NULL),
(24, 5, 'Toss cooked pasta with sauce, garnish with fresh basil', NULL);

-- Insert Game Rules (Board Games, Mobile Games)
INSERT INTO game_rules (game_id, rule_type, players_min, players_max, rule_text, equipment_needed) VALUES
(11, 'indoor', 2, 10, 'Match the color or number on the card. First player to discard all cards wins!', 'UNO card deck'),
(11, 'indoor', 2, 6, 'Buy properties, build houses, and bankrupt opponents to become the richest player!', 'Monopoly board set'),
(9, 'indoor', 1, 1, 'Match 3 or more items to clear levels. Complete objectives before moves run out!', 'Smartphone with game installed'),
(9, 'indoor', 1, 100, 'Build your base, train troops, and battle other players. Join clans for team wars!', 'Smartphone with internet connection');

-- Insert Game Tutorials
INSERT INTO game_tutorials (game_id, tutorial_link) VALUES
(11, 'https://www.youtube.com/watch?v=uno_tutorial'),
(11, 'https://www.youtube.com/watch?v=monopoly_tutorial'),
(9, 'https://www.youtube.com/watch?v=mobile_game_guide');

-- Insert Travel Places (Hiking, Cafes, Historical)
INSERT INTO travel_places (activity_id, place_name, place_type, distance_type, distance_km, days_required, budget_estimate, description, location, google_maps_link) VALUES
(13, 'City Park Trail', 'park', 'short', 5, 0, 0, 'Easy 3km trail perfect for beginners with scenic views', 'Local City Park', 'https://maps.google.com'),
(13, 'Mountain Peak Trek', 'adventure', 'long', 150, 2, 5000, 'Challenging trek with breathtaking mountain views', 'Himalayan Region', 'https://maps.google.com'),
(19, 'Downtown Cafe', 'cafe', 'short', 2, 0, 300, 'Cozy coffee shop with great ambiance and artisanal coffee', 'City Center', 'https://maps.google.com'),
(19, 'Rooftop Cafe', 'cafe', 'short', 5, 0, 500, 'Stunning city views with premium coffee selections', 'Downtown Area', 'https://maps.google.com'),
(19, 'Beachside Cafe', 'cafe', 'medium', 25, 0, 800, 'Relaxing ocean views with fresh seafood and coffee', 'Coastal Area', 'https://maps.google.com'),
(21, 'Red Fort', 'historical', 'medium', 20, 0, 200, 'Iconic Mughal architecture and rich historical significance', 'Delhi, India', 'https://maps.google.com'),
(21, 'Taj Mahal', 'historical', 'long', 200, 1, 3000, 'World wonder and symbol of eternal love', 'Agra, India', 'https://maps.google.com');

-- Insterting Games

-- ============================================
-- COMPREHENSIVE GAME DATA FOR MOODMATCH
-- 100+ Games Across All Categories
-- ============================================

-- First, get the Gaming category ID (should be 3)
-- We'll insert gaming activities with proper rules and tutorials

-- ============================================
-- MOBILE GAMES (Activity IDs starting from 100)
-- ============================================

INSERT INTO activities (id, category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, priority) VALUES
(100, 3, 'PUBG Mobile', 'gaming', 'Battle royale survival shooter', 'excited,competitive,stressed,focused', 'Medium', 'Indoor', 'Both', 20, 60, 85),
(101, 3, 'Free Fire', 'gaming', 'Fast-paced battle royale game', 'excited,energetic,competitive', 'Medium', 'Indoor', 'Both', 15, 40, 83),
(102, 3, 'Call of Duty Mobile', 'gaming', 'First-person shooter action', 'excited,competitive,angry', 'Medium', 'Indoor', 'Both', 15, 45, 84),
(103, 3, 'Candy Crush Saga', 'gaming', 'Match-3 puzzle game', 'calm,bored,happy', 'Low', 'Indoor', 'Solo', 5, 30, 78),
(104, 3, 'Clash of Clans', 'gaming', 'Strategy base building game', 'strategic,focused,competitive', 'Low', 'Indoor', 'Both', 10, 120, 82),
(105, 3, 'Clash Royale', 'gaming', 'Real-time strategy card game', 'competitive,excited,strategic', 'Low', 'Indoor', 'Both', 5, 20, 80),
(106, 3, 'Subway Surfers', 'gaming', 'Endless runner arcade game', 'bored,energetic,happy', 'Low', 'Indoor', 'Solo', 5, 30, 76),
(107, 3, 'Temple Run', 'gaming', 'Endless running adventure', 'excited,bored,happy', 'Low', 'Indoor', 'Solo', 5, 20, 75),
(108, 3, 'Among Us', 'gaming', 'Social deduction multiplayer', 'social,excited,strategic', 'Low', 'Indoor', 'Small Group', 10, 30, 88),
(109, 3, 'Minecraft PE', 'gaming', 'Creative building sandbox', 'creative,calm,happy', 'Low', 'Indoor', 'Both', 20, 180, 87),
(110, 3, 'Roblox', 'gaming', 'User-generated gaming platform', 'creative,social,happy', 'Low', 'Indoor', 'Both', 15, 120, 86),
(111, 3, 'Genshin Impact', 'gaming', 'Open-world action RPG', 'adventurous,excited,calm', 'Medium', 'Indoor', 'Solo', 30, 180, 89),
(112, 3, 'Pokemon GO', 'gaming', 'AR location-based game', 'adventurous,social,happy', 'High', 'Outdoor', 'Both', 20, 120, 84),
(113, 3, 'Ludo King', 'gaming', 'Classic board game digital', 'social,happy,competitive', 'Low', 'Indoor', 'Small Group', 10, 30, 81),
(114, 3, 'Asphalt 9', 'gaming', 'Arcade racing game', 'excited,energetic,competitive', 'Low', 'Indoor', 'Both', 5, 20, 79),
(115, 3, '8 Ball Pool', 'gaming', 'Online pool billiards', 'calm,focused,competitive', 'Low', 'Indoor', 'Both', 5, 15, 77),
(116, 3, 'Chess.com', 'gaming', 'Online chess platform', 'strategic,focused,calm', 'Low', 'Indoor', 'Both', 10, 60, 85),
(117, 3, 'Wordle', 'gaming', 'Daily word puzzle game', 'curious,focused,calm', 'Low', 'Indoor', 'Solo', 5, 10, 78),
(118, 3, 'Brain Out', 'gaming', 'Tricky puzzle challenges', 'curious,focused,bored', 'Low', 'Indoor', 'Solo', 5, 30, 76),
(119, 3, 'Gardenscapes', 'gaming', 'Match-3 garden decoration', 'calm,creative,happy', 'Low', 'Indoor', 'Solo', 10, 60, 75);

-- Mobile Game Rules
INSERT INTO game_rules (game_id, rule_text, players_min, players_max, equipment_needed) VALUES
(100, 'Drop on island, collect weapons and survive', 1, 100, 'Smartphone, Internet'),
(100, 'Stay in safe zone, last player/team wins', 1, 100, 'Good reflexes'),
(101, 'Land, loot, survive in 10-minute battles', 1, 50, 'Smartphone, Internet'),
(102, 'Classic FPS modes: Team Deathmatch, Domination, Battle Royale', 1, 100, 'Smartphone, Good internet'),
(103, 'Match 3+ candies to clear levels', 1, 1, 'Smartphone'),
(103, 'Complete level objectives before moves run out', 1, 1, 'Patience'),
(104, 'Build and upgrade your village', 1, 1, 'Smartphone, Internet'),
(104, 'Train troops and attack other players', 1, 1, 'Strategic thinking'),
(108, 'Complete tasks while identifying impostors', 4, 15, 'Smartphone/PC, Internet'),
(108, 'Impostors sabotage and eliminate crewmates', 4, 15, 'Communication skills'),
(109, 'Gather resources and build structures', 1, 10, 'Smartphone/Tablet'),
(109, 'Survive nights by crafting tools', 1, 10, 'Creativity'),
(113, 'Roll dice and move tokens around board', 2, 4, 'Smartphone'),
(113, 'First to get all tokens home wins', 2, 4, 'Good luck'),
(116, 'Move pieces strategically to checkmate opponent', 2, 2, 'Chess knowledge'),
(117, 'Guess 5-letter word in 6 tries', 1, 1, 'Vocabulary skills');

-- Mobile Game Tutorials
INSERT INTO game_tutorials (game_id, tutorial_link) VALUES
(100, 'https://www.youtube.com/watch?v=ioNFnsuY6SY'),
(101, 'https://www.youtube.com/watch?v=Tt_bgUDhGU0'),
(102, 'https://www.youtube.com/watch?v=LixGul_Jcnk'),
(108, 'https://www.youtube.com/watch?v=pt0S_8n4aos'),
(109, 'https://www.youtube.com/watch?v=LknJd9rd3NU'),
(111, 'https://www.youtube.com/watch?v=xClY8xiB0Pg');

-- ============================================
-- PC GAMES (Activity IDs 120-139)
-- ============================================

INSERT INTO activities (id, category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, priority) VALUES
(120, 3, 'Valorant', 'gaming', 'Tactical FPS shooter', 'competitive,focused,excited', 'Medium', 'Indoor', 'Small Group', 30, 60, 92),
(121, 3, 'League of Legends', 'gaming', 'MOBA strategic team game', 'strategic,competitive,angry', 'Medium', 'Indoor', 'Small Group', 30, 60, 91),
(122, 3, 'Dota 2', 'gaming', 'Complex MOBA game', 'strategic,competitive,focused', 'Medium', 'Indoor', 'Small Group', 40, 90, 90),
(123, 3, 'CS:GO', 'gaming', 'Counter-Strike tactical shooter', 'competitive,focused,excited', 'Medium', 'Indoor', 'Small Group', 30, 60, 93),
(124, 3, 'Fortnite', 'gaming', 'Battle royale building game', 'excited,competitive,creative', 'Medium', 'Indoor', 'Both', 20, 40, 89),
(125, 3, 'Minecraft Java', 'gaming', 'Infinite creative sandbox', 'creative,calm,happy', 'Low', 'Indoor', 'Both', 30, 300, 90),
(126, 3, 'GTA V', 'gaming', 'Open-world action adventure', 'excited,adventurous,stressed', 'Medium', 'Indoor', 'Both', 30, 180, 88),
(127, 3, 'The Witcher 3', 'gaming', 'Epic fantasy RPG', 'adventurous,focused,calm', 'Low', 'Indoor', 'Solo', 60, 300, 87),
(128, 3, 'Red Dead Redemption 2', 'gaming', 'Western open-world epic', 'adventurous,calm,focused', 'Low', 'Indoor', 'Solo', 60, 240, 86),
(129, 3, 'Cyberpunk 2077', 'gaming', 'Futuristic RPG adventure', 'adventurous,excited,curious', 'Low', 'Indoor', 'Solo', 60, 180, 83),
(130, 3, 'Apex Legends', 'gaming', 'Hero-based battle royale', 'competitive,excited,strategic', 'Medium', 'Indoor', 'Both', 20, 40, 87),
(131, 3, 'Overwatch 2', 'gaming', 'Team-based hero shooter', 'competitive,strategic,social', 'Medium', 'Indoor', 'Small Group', 20, 60, 85),
(132, 3, 'Rocket League', 'gaming', 'Soccer with rocket cars', 'competitive,excited,happy', 'Low', 'Indoor', 'Both', 5, 20, 84),
(133, 3, 'FIFA 23', 'gaming', 'Football simulation game', 'competitive,excited,social', 'Low', 'Indoor', 'Both', 10, 30, 86),
(134, 3, 'Elden Ring', 'gaming', 'Dark fantasy action RPG', 'challenging,focused,angry', 'Medium', 'Indoor', 'Solo', 60, 240, 88),
(135, 3, 'Stardew Valley', 'gaming', 'Relaxing farming simulator', 'calm,happy,creative', 'Low', 'Indoor', 'Solo', 30, 180, 85),
(136, 3, 'Terraria', 'gaming', '2D adventure sandbox', 'adventurous,creative,excited', 'Low', 'Indoor', 'Both', 30, 180, 82),
(137, 3, 'Age of Empires IV', 'gaming', 'Real-time strategy game', 'strategic,focused,competitive', 'Low', 'Indoor', 'Both', 40, 120, 81),
(138, 3, 'Civilization VI', 'gaming', 'Turn-based strategy empire', 'strategic,calm,focused', 'Low', 'Indoor', 'Both', 60, 360, 83),
(139, 3, 'Sims 4', 'gaming', 'Life simulation game', 'creative,calm,happy', 'Low', 'Indoor', 'Solo', 30, 180, 80);

-- PC Game Rules
INSERT INTO game_rules (game_id, rule_text, players_min, players_max, equipment_needed) VALUES
(120, '5v5 tactical shooter with unique agent abilities', 5, 10, 'Gaming PC, Mouse, Keyboard'),
(121, '5v5 MOBA: Destroy enemy nexus', 5, 10, 'Gaming PC, Mouse, Keyboard'),
(123, '5v5: Plant/defuse bomb or eliminate enemy team', 5, 10, 'Gaming PC, Good aim'),
(125, 'Gather resources, craft items, build structures', 1, 100, 'PC, Creativity'),
(132, 'Score goals using rocket-powered cars', 1, 8, 'PC/Console, Controller recommended'),
(135, 'Farm crops, raise animals, build relationships', 1, 4, 'PC, Patience');

-- ============================================
-- BOARD GAMES (Activity IDs 140-154)
-- ============================================

INSERT INTO activities (id, category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, priority) VALUES
(140, 3, 'Chess', 'gaming', 'Strategic board game', 'strategic,focused,calm', 'Low', 'Indoor', 'Both', 10, 120, 90),
(141, 3, 'Monopoly', 'gaming', 'Property trading game', 'competitive,strategic,social', 'Low', 'Indoor', 'Small Group', 60, 180, 85),
(142, 3, 'Scrabble', 'gaming', 'Word building game', 'focused,calm,competitive', 'Low', 'Indoor', 'Small Group', 30, 90, 82),
(143, 3, 'UNO', 'gaming', 'Fast-paced card matching', 'happy,excited,social', 'Low', 'Indoor', 'Small Group', 15, 45, 88),
(144, 3, 'Ludo', 'gaming', 'Classic dice racing game', 'happy,social,competitive', 'Low', 'Indoor', 'Small Group', 20, 45, 83),
(145, 3, 'Checkers', 'gaming', 'Strategy capture game', 'strategic,focused,calm', 'Low', 'Indoor', 'Both', 15, 60, 79),
(146, 3, 'Snakes and Ladders', 'gaming', 'Luck-based board game', 'happy,social,excited', 'Low', 'Indoor', 'Small Group', 10, 30, 76),
(147, 3, 'Carrom', 'gaming', 'Striker flicking game', 'focused,competitive,social', 'Low', 'Indoor', 'Small Group', 20, 60, 84),
(148, 3, 'Jenga', 'gaming', 'Block stacking game', 'nervous,focused,social', 'Low', 'Indoor', 'Small Group', 10, 30, 81),
(149, 3, 'Catan', 'gaming', 'Resource trading strategy', 'strategic,social,competitive', 'Low', 'Indoor', 'Small Group', 60, 120, 87),
(150, 3, 'Risk', 'gaming', 'World domination strategy', 'strategic,competitive,focused', 'Low', 'Indoor', 'Small Group', 90, 240, 84),
(151, 3, 'Ticket to Ride', 'gaming', 'Train route building', 'strategic,calm,social', 'Low', 'Indoor', 'Small Group', 45, 90, 82),
(152, 3, 'Pandemic', 'gaming', 'Cooperative disease control', 'strategic,cooperative,focused', 'Low', 'Indoor', 'Small Group', 45, 90, 83),
(153, 3, 'Codenames', 'gaming', 'Word association party game', 'social,strategic,creative', 'Low', 'Indoor', 'Large Group', 15, 30, 85),
(154, 3, 'Exploding Kittens', 'gaming', 'Strategic card game', 'funny,excited,social', 'Low', 'Indoor', 'Small Group', 15, 30, 80);

-- Board Game Rules
INSERT INTO game_rules (game_id, rule_text, players_min, players_max, equipment_needed) VALUES
(140, 'Checkmate opponent king using strategic moves', 2, 2, 'Chess board, 32 pieces'),
(141, 'Buy properties, build houses, bankrupt opponents', 2, 8, 'Monopoly board, money, tokens'),
(142, 'Create words on board using letter tiles', 2, 4, 'Scrabble board, letter tiles'),
(143, 'Match card color or number, first to empty hand wins', 2, 10, 'UNO card deck'),
(144, 'Roll dice, race tokens to home', 2, 4, 'Ludo board, dice, tokens'),
(147, 'Flick striker to pocket carrom men', 2, 4, 'Carrom board, striker, coins'),
(148, 'Remove blocks without toppling tower', 2, 8, 'Jenga blocks'),
(149, 'Collect resources, build settlements and cities', 3, 4, 'Catan board, resource cards');

-- ============================================
-- CARD GAMES (Activity IDs 155-164)
-- ============================================

INSERT INTO activities (id, category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, priority) VALUES
(155, 3, 'Poker', 'gaming', 'Strategic betting card game', 'strategic,competitive,focused', 'Low', 'Indoor', 'Small Group', 30, 180, 88),
(156, 3, 'Rummy', 'gaming', 'Card melding game', 'strategic,focused,social', 'Low', 'Indoor', 'Small Group', 20, 60, 84),
(157, 3, 'Bridge', 'gaming', 'Trick-taking partnership game', 'strategic,focused,social', 'Low', 'Indoor', 'Small Group', 45, 120, 82),
(158, 3, 'Hearts', 'gaming', 'Trick-avoidance card game', 'strategic,focused,competitive', 'Low', 'Indoor', 'Small Group', 20, 45, 79),
(159, 3, 'Blackjack', 'gaming', '21 card game', 'strategic,excited,competitive', 'Low', 'Indoor', 'Small Group', 10, 60, 83),
(160, 3, 'Solitaire', 'gaming', 'Single player card game', 'calm,focused,bored', 'Low', 'Indoor', 'Solo', 5, 20, 76),
(161, 3, 'Go Fish', 'gaming', 'Simple matching game', 'happy,social,calm', 'Low', 'Indoor', 'Small Group', 10, 20, 74),
(162, 3, 'Spades', 'gaming', 'Partnership trick-taking', 'strategic,competitive,social', 'Low', 'Indoor', 'Small Group', 20, 60, 80),
(163, 3, 'Crazy Eights', 'gaming', 'Shedding-type card game', 'happy,social,excited', 'Low', 'Indoor', 'Small Group', 10, 30, 77),
(164, 3, 'Teen Patti', 'gaming', 'Indian poker variant', 'competitive,excited,social', 'Low', 'Indoor', 'Small Group', 20, 90, 85);

-- Card Game Rules
INSERT INTO game_rules (game_id, rule_text, players_min, players_max, equipment_needed) VALUES
(155, 'Best 5-card hand wins the pot', 2, 10, 'Standard deck, chips'),
(156, 'Form sets and runs, first to meld all cards wins', 2, 6, 'Standard deck or Rummy cards'),
(159, 'Get closer to 21 than dealer without busting', 1, 7, 'Standard deck'),
(160, 'Sort cards into foundations by suit', 1, 1, 'Standard deck'),
(164, 'Best 3-card hand wins, similar to poker', 2, 10, 'Standard deck');

-- ============================================
-- OUTDOOR/SPORTS GAMES (Activity IDs 165-189)
-- ============================================

INSERT INTO activities (id, category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, priority) VALUES
(165, 4, 'Football/Soccer', 'gaming', 'Team ball sport', 'energetic,competitive,social', 'High', 'Outdoor', 'Large Group', 45, 120, 92),
(166, 4, 'Cricket', 'gaming', 'Bat and ball team sport', 'competitive,strategic,social', 'High', 'Outdoor', 'Large Group', 90, 480, 90),
(167, 4, 'Basketball', 'gaming', 'Hoop shooting sport', 'energetic,competitive,social', 'High', 'Both', 'Small Group', 30, 90, 89),
(168, 4, 'Tennis', 'gaming', 'Racket sport', 'competitive,focused,energetic', 'High', 'Outdoor', 'Both', 30, 120, 87),
(169, 4, 'Badminton', 'gaming', 'Shuttlecock racket sport', 'energetic,competitive,social', 'High', 'Both', 'Both', 15, 60, 86),
(170, 4, 'Volleyball', 'gaming', 'Net ball team sport', 'energetic,social,competitive', 'High', 'Both', 'Small Group', 30, 90, 85),
(171, 4, 'Table Tennis', 'gaming', 'Indoor paddle sport', 'focused,competitive,energetic', 'Medium', 'Indoor', 'Both', 10, 60, 84),
(172, 4, 'Kabaddi', 'gaming', 'Contact team sport', 'energetic,competitive,strategic', 'High', 'Outdoor', 'Large Group', 30, 60, 82),
(173, 4, 'Kho Kho', 'gaming', 'Traditional tag game', 'energetic,social,happy', 'High', 'Outdoor', 'Large Group', 20, 40, 80),
(174, 4, 'Hide and Seek', 'gaming', 'Classic hiding game', 'excited,happy,social', 'Medium', 'Both', 'Small Group', 15, 45, 78),
(175, 4, 'Tag/Catch', 'gaming', 'Chasing game', 'energetic,happy,social', 'High', 'Outdoor', 'Small Group', 10, 30, 79),
(176, 4, 'Frisbee', 'gaming', 'Disc throwing game', 'happy,social,energetic', 'Medium', 'Outdoor', 'Both', 20, 60, 81),
(177, 4, 'Dodgeball', 'gaming', 'Ball throwing elimination', 'energetic,competitive,excited', 'High', 'Outdoor', 'Large Group', 15, 45, 83),
(178, 4, 'Capture the Flag', 'gaming', 'Territory strategy game', 'strategic,energetic,competitive', 'High', 'Outdoor', 'Large Group', 30, 90, 84),
(179, 4, 'Red Light Green Light', 'gaming', 'Movement control game', 'happy,focused,social', 'Medium', 'Outdoor', 'Small Group', 10, 20, 76),
(180, 4, 'Duck Duck Goose', 'gaming', 'Circle chasing game', 'happy,social,energetic', 'Medium', 'Outdoor', 'Small Group', 10, 20, 75),
(181, 4, 'Hopscotch', 'gaming', 'Hopping grid game', 'happy,focused,energetic', 'Medium', 'Outdoor', 'Both', 5, 20, 74),
(182, 4, 'Jump Rope', 'gaming', 'Skipping exercise game', 'energetic,happy,focused', 'High', 'Both', 'Both', 5, 30, 77),
(183, 4, 'Four Square', 'gaming', 'Ball bouncing game', 'competitive,social,energetic', 'Medium', 'Outdoor', 'Small Group', 15, 45, 78),
(184, 4, 'Tug of War', 'gaming', 'Rope pulling contest', 'competitive,energetic,social', 'High', 'Outdoor', 'Large Group', 5, 15, 80),
(185, 4, 'Relay Race', 'gaming', 'Team running competition', 'competitive,energetic,social', 'High', 'Outdoor', 'Large Group', 10, 30, 81),
(186, 4, 'Swimming', 'gaming', 'Water sport activity', 'energetic,calm,happy', 'High', 'Outdoor', 'Both', 30, 120, 88),
(187, 4, 'Rock Climbing', 'gaming', 'Wall climbing sport', 'challenging,focused,adventurous', 'High', 'Both', 'Solo', 30, 180, 86),
(188, 4, 'Skateboarding', 'gaming', 'Board riding sport', 'adventurous,excited,focused', 'High', 'Outdoor', 'Solo', 20, 120, 83),
(189, 4, 'Cycling', 'gaming', 'Bike riding activity', 'energetic,calm,happy', 'High', 'Outdoor', 'Both', 30, 180, 85);

-- Sports Game Rules
INSERT INTO game_rules (game_id, rule_text, players_min, players_max, equipment_needed) VALUES
(165, 'Score goals by kicking ball into opponent net', 2, 22, 'Football, goal posts'),
(166, 'Score runs by hitting ball and running between wickets', 2, 22, 'Cricket bat, ball, stumps'),
(167, 'Shoot ball through hoop to score points', 2, 10, 'Basketball, hoop'),
(168, 'Hit ball over net within court boundaries', 2, 4, 'Tennis racket, ball, net'),
(169, 'Hit shuttlecock over net', 2, 4, 'Badminton racket, shuttlecock'),
(171, 'Hit ball back and forth on table', 2, 4, 'Table, paddles, ball'),
(174, 'One person seeks while others hide', 2, 20, 'Hiding spots'),
(175, 'Tag others by touching them', 2, 20, 'Open space'),
(177, 'Eliminate players by hitting with ball', 6, 20, 'Soft balls'),
(184, 'Pull rope to bring opponents across line', 6, 30, 'Strong rope');

-- ============================================
-- TRADITIONAL/INDOOR GAMES (Activity IDs 190-204)
-- ============================================

INSERT INTO activities (id, category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, priority) VALUES
(190, 3, 'Chinese Checkers', 'gaming', 'Marble hopping game', 'strategic,focused,social', 'Low', 'Indoor', 'Small Group', 20, 45, 79),
(191, 3, 'Dominoes', 'gaming', 'Tile matching game', 'strategic,calm,social', 'Low', 'Indoor', 'Small Group', 15, 45, 78),
(192, 3, 'Mancala', 'gaming', 'Ancient count-and-capture', 'strategic,focused,calm', 'Low', 'Indoor', 'Both', 10, 30, 77),
(193, 3, 'Backgammon', 'gaming', 'Board racing game', 'strategic,competitive,focused', 'Low', 'Indoor', 'Both', 20, 60, 80),
(194, 3, 'Mahjong', 'gaming', 'Tile matching game', 'strategic,focused,social', 'Low', 'Indoor', 'Small Group', 30, 90, 82),
(195, 3, 'Darts', 'gaming', 'Target throwing game', 'focused,competitive,social', 'Low', 'Indoor', 'Both', 10, 45, 81),
(196, 3, 'Billiards/Pool', 'gaming', 'Cue sports game', 'focused,competitive,calm', 'Low', 'Indoor', 'Both', 20, 90, 84),
(197, 3, 'Foosball', 'gaming', 'Table soccer game', 'competitive,excited,social', 'Low', 'Indoor', 'Both', 5, 30, 82),
(198, 3, 'Air Hockey', 'gaming', 'Fast puck game', 'competitive,excited,focused', 'Low', 'Indoor', 'Both', 5, 20, 80),
(199, 3, 'Bowling', 'gaming', 'Pin knocking sport', 'focused,social,competitive', 'Low', 'Indoor', 'Both', 30, 120, 85),
(200, 3, 'Pictionary', 'gaming', 'Drawing guessing game', 'creative,social,happy', 'Low', 'Indoor', 'Small Group', 20, 60, 83),
(201, 3, 'Charades', 'gaming', 'Acting guessing game', 'social,funny,excited', 'Low', 'Indoor', 'Small Group', 15, 45, 84),
(202, 3, 'Truth or Dare', 'gaming', 'Question and challenge', 'social,excited,nervous', 'Low', 'Indoor', 'Small Group', 20, 60, 79),
(203, 3, 'Never Have I Ever', 'gaming', 'Confession party game', 'social,funny,excited', 'Low', 'Indoor', 'Small Group', 15, 45, 78),
(204, 3, '20 Questions', 'gaming', 'Guessing game', 'strategic,social,curious', 'Low', 'Indoor', 'Small Group', 10, 30, 76);

-- Traditional Game Rules
INSERT INTO game_rules (game_id, rule_text, players_min, players_max, equipment_needed) VALUES
(191, 'Match dominoes end to end', 2, 4, 'Domino set'),
(195, 'Throw darts at numbered board', 1, 8, 'Dartboard, darts'),
(196, 'Pocket balls using cue stick', 1, 2, 'Pool table, cues, balls'),
(199, 'Knock down pins with bowling ball', 1, 6, 'Bowling alley, ball'),
(200, 'Draw words/phrases for team to guess', 4, 12, 'Paper, markers'),
(201, 'Act out words without speaking', 4, 20, 'Word cards');

-- ============================================
-- PUZZLE/BRAIN GAMES (Activity IDs 205-214)
-- ============================================

INSERT INTO activities (id, category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, priority) VALUES
(205, 3, 'Rubiks Cube', 'gaming', 'Color matching puzzle', 'focused,challenging,calm', 'Low', 'Indoor', 'Solo', 5, 60, 82),
(206, 3, 'Jigsaw Puzzle', 'gaming', 'Picture assembly puzzle', 'calm,focused,patient', 'Low', 'Indoor', 'Both', 30, 300, 80),
(207, 3, 'Sudoku', 'gaming', 'Number logic puzzle', 'focused,calm,strategic', 'Low', 'Indoor', 'Solo', 10, 60, 81),
(208, 3, 'Crossword Puzzle', 'gaming', 'Word clue puzzle', 'focused,curious,calm', 'Low', 'Indoor', 'Both', 15, 90, 79),
(209, 3, 'Trivia Quiz', 'gaming', 'Knowledge testing game', 'curious,competitive,social', 'Low', 'Indoor', 'Both', 15, 60, 83),
(210, 3, 'Escape Room', 'gaming', 'Puzzle solving challenge', 'strategic,excited,social', 'Medium', 'Indoor', 'Small Group', 45, 90, 88),
(211, 3, 'Memory Card Game', 'gaming', 'Card matching memory', 'focused,calm,competitive', 'Low', 'Indoor', 'Small Group', 10, 30, 76),
(212, 3, 'Simon Says', 'gaming', 'Command following game', 'focused,social,happy', 'Low', 'Both', 'Small Group', 10, 20, 75),
(213, 3, 'Word Search', 'gaming', 'Letter grid puzzle', 'calm,focused,patient', 'Low', 'Indoor', 'Solo', 5, 30, 74),
(214, 3, 'Spot the Difference', 'gaming', 'Visual comparison puzzle', 'focused,calm,patient', 'Low', 'Indoor', 'Both', 5, 20, 73);

-- Puzzle Game Rules
INSERT INTO game_rules (game_id, rule_text, players_min, players_max, equipment_needed) VALUES
(205, 'Solve cube to have each face one solid color', 1, 1, 'Rubiks Cube'),
(206, 'Assemble pieces to complete picture', 1, 10, 'Jigsaw puzzle set'),
(207, 'Fill 9x9 grid with numbers 1-9', 1, 1, 'Sudoku puzzle'),
(210, 'Solve puzzles to escape room within time limit', 2, 8, 'Escape room setup'),
(211, 'Match pairs of cards by memory', 2, 6, 'Memory card deck');

-- ============================================
-- CONSOLE-EXCLUSIVE GAMES (Activity IDs 215-224)
-- ============================================

INSERT INTO activities (id, category_id, name, execution_type, description, mood_tags, energy_level, location_type, social_type, min_time, max_time, priority) VALUES
(215, 3, 'Mario Kart', 'gaming', 'Kart racing game', 'excited,competitive,happy', 'Low', 'Indoor', 'Small Group', 10, 30, 89),
(216, 3, 'Super Smash Bros', 'gaming', 'Fighting party game', 'competitive,excited,social', 'Low', 'Indoor', 'Small Group', 10, 60, 88),
(217, 3, 'The Legend of Zelda', 'gaming', 'Action adventure RPG', 'adventurous,focused,calm', 'Low', 'Indoor', 'Solo', 60, 240, 92),
(218, 3, 'God of War', 'gaming', 'Action mythology adventure', 'adventurous,excited,focused', 'Medium', 'Indoor', 'Solo', 60, 180, 90),
(219, 3, 'Spider-Man PS', 'gaming', 'Superhero action adventure', 'excited,adventurous,happy', 'Medium', 'Indoor', 'Solo', 30, 120, 89),
(220, 3, 'Halo', 'gaming', 'Sci-fi FPS game', 'competitive,excited,strategic', 'Medium', 'Indoor', 'Both', 30, 120, 87),
(221, 3, 'Uncharted', 'gaming', 'Action adventure treasure hunt', 'adventurous,excited,curious', 'Medium', 'Indoor', 'Solo', 60, 180, 86),
(222, 3, 'Gran Turismo', 'gaming', 'Racing simulation', 'focused,competitive,calm', 'Low', 'Indoor', 'Both', 20, 90, 84),
(223, 3, 'Animal Crossing', 'gaming', 'Life simulation game', 'calm,creative,happy', 'Low', 'Indoor', 'Solo', 30, 180, 85),
(224, 3, 'Fall Guys', 'gaming', 'Obstacle course battle royale', 'funny,excited,competitive', 'Low', 'Indoor', 'Both', 10, 30, 82);

-- Console Game Rules
INSERT INTO game_rules (game_id, rule_text, players_min, players_max, equipment_needed) VALUES
(215, 'Race karts on creative tracks with items', 1, 4, 'Nintendo Switch/Console'),
(216, 'Battle using Nintendo characters', 1, 8, 'Nintendo Switch'),
(217, 'Explore Hyrule and save princess Zelda', 1, 1, 'Nintendo Console'),
(218, 'Combat gods in Norse mythology', 1, 1, 'PlayStation Console'),
(220, 'FPS campaign and multiplayer battles', 1, 16, 'Xbox Console'),
(223, 'Build island life and interact with villagers', 1, 8, 'Nintendo Switch');

-- ============================================
-- Add more tutorials
-- ============================================

INSERT INTO game_tutorials (game_id, tutorial_link) VALUES
(120, 'https://www.youtube.com/watch?v=valorant_guide'),
(121, 'https://www.youtube.com/watch?v=lol_beginners'),
(140, 'https://www.youtube.com/watch?v=chess_basics'),
(143, 'https://www.youtube.com/watch?v=uno_rules'),
(155, 'https://www.youtube.com/watch?v=poker_tutorial'),
(165, 'https://www.youtube.com/watch?v=football_skills'),
(166, 'https://www.youtube.com/watch?v=cricket_basics'),
(210, 'https://www.youtube.com/watch?v=escape_room_tips'),
(215, 'https://www.youtube.com/watch?v=mariokart_tips');



-- ============================================
-- END OF GAME DATA
-- Total: 125 Games Added!
-- ============================================

-- ============================================
-- END OF SCHEMA
-- ============================================