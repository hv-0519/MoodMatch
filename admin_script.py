import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "models/mood.db"

username = "admin"          # used as email
password = "admin123"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

password_hash = generate_password_hash(password)

cursor.execute("""
INSERT INTO admins (
    username,
    password_hash
) VALUES (?, ?)
""", (
    "admin",
    password_hash
))

conn.commit()
conn.close()

print("✅ Admin user created successfully")
print(f"Username: {username}")
print(f"Password: {password}")
