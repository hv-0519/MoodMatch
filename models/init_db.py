"""
MoodMatch Database Initialization Script
Drops existing database and creates fresh one with seed data
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_NAME = 'instance/moodmatch.db'
SQL_FILE = 'moodmatch.sql'

def init_db():
    """Initialize database with schema and seed data"""
    
    # Remove old database
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print('🗑️  Old Database Removed!')
    
    # Create instance directory if doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    # Connect to new database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    try:
        # Read and execute SQL schema
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Execute the schema
        cursor.executescript(sql_script)
        
        # Now update password hashes (the placeholders in seed data)
        print('🔐 Generating password hashes...')
        
        # Hash for admin password (admin123)
        admin_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
        cursor.execute("UPDATE admins SET password_hash = ? WHERE username = 'admin'", (admin_hash,))
        
        # Hash for sample users (user123)
        user_hash = generate_password_hash('user123', method='pbkdf2:sha256')
        cursor.execute("UPDATE users SET password_hash = ?", (user_hash,))
        
        conn.commit()
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("\n✅ Database initialized successfully!")
        print(f"📊 Tables created: {len(tables)}")
        print(f"📁 Location: {DB_NAME}")
        print("\n📋 Tables:")
        for table in sorted(tables):
            if not table.startswith('sqlite_'):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   - {table}: {count} rows")
        
        print("\n🔑 Login Credentials:")
        print("   Admin:  username='admin' password='admin123'")
        print("   User 1: username='user_001' password='user123'")
        print("   User 2: username='user_002' password='user123'")
        print("   User 3: username='user_003' password='user123'")
        
    except UnicodeDecodeError:
        print("❌ Error: Could not decode SQL file. Ensure it's saved with UTF-8 encoding.")
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("   🎨 MOODMATCH DATABASE INITIALIZATION")
    print("=" * 60)
    init_db()
    print("=" * 60)