#models/database.py

import sqlite3
from contextlib import contextmanager
import json
from datetime import datetime
from config import Config

class Database:
    '''Database handler for mood activities application'''
    
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE
    
    @contextmanager
    def get_connection(self):
        '''Context manager for database connections'''
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        '''Initialize database tables and seed data'''
        with self.get_connection() as conn:
            c = conn.cursor()
            
            # Activities table
            c.execute('''CREATE TABLE IF NOT EXISTS activities
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          category TEXT NOT NULL,
                          mood TEXT NOT NULL,
                          time_required TEXT,
                          budget TEXT,
                          energy_level TEXT,
                          location_type TEXT,
                          distance TEXT,
                          description TEXT,
                          created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            
            # User preferences history
            c.execute('''CREATE TABLE IF NOT EXISTS user_history
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          mood TEXT,
                          filters TEXT,
                          result_count INTEGER,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            
            # Favorites table
            c.execute('''CREATE TABLE IF NOT EXISTS favorites
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          activity_id INTEGER,
                          added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (activity_id) REFERENCES activities(id))''')
            
            # Check if activities already exist
            c.execute('SELECT COUNT(*) FROM activities')
            if c.fetchone()[0] == 0:
                from utils.seed_data import get_seed_data
                activities = get_seed_data()
                c.executemany('''INSERT INTO activities 
                                 (name, category, mood, time_required, budget, 
                                  energy_level, location_type, distance, description) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', activities)
                print(f"✅ Database seeded with {len(activities)} activities")
    
    def get_activities(self, mood, filters=None):
        '''Get activities filtered by mood and optional filters'''
        filters = filters or {}
        
        with self.get_connection() as conn:
            c = conn.cursor()
            
            query = "SELECT * FROM activities WHERE mood = ?"
            params = [mood]
            
            # Apply filters
            if filters.get('time'):
                query += " AND time_required = ?"
                params.append(filters['time'])
            
            if filters.get('budget'):
                query += " AND budget = ?"
                params.append(filters['budget'])
            
            if filters.get('energy'):
                query += " AND energy_level = ?"
                params.append(filters['energy'])
            
            if filters.get('location'):
                query += " AND location_type = ?"
                params.append(filters['location'])
            
            if filters.get('distance'):
                query += " AND distance = ?"
                params.append(filters['distance'])
            
            query += " ORDER BY name"
            
            c.execute(query, params)
            return [dict(row) for row in c.fetchall()]
    
    def get_activity_by_id(self, activity_id):
        '''Get single activity by ID'''
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM activities WHERE id = ?', (activity_id,))
            row = c.fetchone()
            return dict(row) if row else None
    
    def save_user_history(self, mood, filters, result_count):
        '''Save user search to history'''
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO user_history (mood, filters, result_count) 
                         VALUES (?, ?, ?)''',
                      (mood, json.dumps(filters), result_count))
    
    def get_user_history(self, limit=10):
        '''Get user search history'''
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT * FROM user_history 
                         ORDER BY timestamp DESC LIMIT ?''', (limit,))
            return [dict(row) for row in c.fetchall()]
    
    def add_favorite(self, activity_id):
        '''Add activity to favorites'''
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO favorites (activity_id) VALUES (?)', (activity_id,))
    
    def remove_favorite(self, activity_id):
        '''Remove activity from favorites'''
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM favorites WHERE activity_id = ?', (activity_id,))
    
    def get_favorites(self):
        '''Get all favorite activities'''
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT a.* FROM activities a
                         INNER JOIN favorites f ON a.id = f.activity_id
                         ORDER BY f.added_at DESC''')
            return [dict(row) for row in c.fetchall()]
    
    def get_statistics(self):
        '''Get database statistics'''
        with self.get_connection() as conn:
            c = conn.cursor()
            
            stats = {}
            
            # Total activities
            c.execute('SELECT COUNT(*) as count FROM activities')
            stats['total_activities'] = c.fetchone()['count']
            
            # Activities by category
            c.execute('''SELECT category, COUNT(*) as count 
                         FROM activities GROUP BY category''')
            stats['by_category'] = {row['category']: row['count'] 
                                   for row in c.fetchall()}
            
            # Activities by mood
            c.execute('''SELECT mood, COUNT(*) as count 
                         FROM activities GROUP BY mood''')
            stats['by_mood'] = {row['mood']: row['count'] 
                               for row in c.fetchall()}
            
            return stats

# Global database instance
db = Database()