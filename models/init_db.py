import sqlite3
import os

DB_NAME = 'mood.db'
SQL_FILE = 'reset_db.sql'

def init_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print('Old Database Removed!!!')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    # ADDED encoding='utf-8' HERE
    try:
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        cursor.executescript(sql_script)
        conn.commit()
        print("Database initialized successfully.")
    except UnicodeDecodeError:
        print("Error: Could not decode the SQL file. Ensure it is saved with UTF-8 encoding.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()