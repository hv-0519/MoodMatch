-- QUICK FIX: Rename tables to match user_complete.py

-- 1. Rename activity_resources → resources


-- 4. Fix execution_type values (must match: editor, resource, steps, gaming, travel)
UPDATE activities SET execution_type = 'editor' WHERE execution_type IN ('writing', 'journaling');
UPDATE activities SET execution_type = 'resource' WHERE execution_type IN ('reading', 'learning', 'documentary');
UPDATE activities SET execution_type = 'steps' WHERE execution_type IN ('cooking', 'diy', 'yoga', 'photography');
UPDATE activities SET execution_type = 'gaming' WHERE execution_type IN ('gaming_mobile', 'gaming_pc', 'gaming_board', 'game', 'sports');
UPDATE activities SET execution_type = 'travel' WHERE execution_type IN ('travel_short', 'travel_medium', 'travel_long');

-- 5. Fix filter value capitalization
UPDATE activities SET energy_level = 'Low' WHERE LOWER(energy_level) = 'low';
UPDATE activities SET energy_level = 'Medium' WHERE LOWER(energy_level) = 'medium';
UPDATE activities SET energy_level = 'High' WHERE LOWER(energy_level) = 'high';

UPDATE activities SET location_type = 'Indoor' WHERE LOWER(location_type) = 'indoor';
UPDATE activities SET location_type = 'Outdoor' WHERE LOWER(location_type) = 'outdoor';
UPDATE activities SET location_type = 'Both' WHERE LOWER(location_type) = 'both';

UPDATE activities SET social_type = 'Solo' WHERE LOWER(social_type) = 'solo';
UPDATE activities SET social_type = 'Small Group' WHERE LOWER(social_type) IN ('group', 'small group');
UPDATE activities SET social_type = 'Large Group' WHERE LOWER(social_type) = 'large group';
UPDATE activities SET social_type = 'Both' WHERE LOWER(social_type) = 'both';

-- 6. Add activity_filters table (needed by routes)
CREATE TABLE IF NOT EXISTS activity_filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL UNIQUE,
    min_time INTEGER,
    max_time INTEGER,
    min_budget INTEGER,
    max_budget INTEGER,
    energy_level TEXT,
    location_type TEXT,
    distance_type TEXT,
    social_type TEXT,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

-- 7. Add feedback_text column to user_history if missing
ALTER TABLE user_history ADD COLUMN feedback_text TEXT;

PRAGMA foreign_keys = ON;