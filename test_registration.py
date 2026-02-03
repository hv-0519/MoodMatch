import sqlite3

# Test the database connection and table structure
conn = sqlite3.connect("models/instance/moodmatch.db")
cursor = conn.cursor()

# Check users table
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
print("Users table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check interests table
cursor.execute("PRAGMA table_info(interests)")
columns = cursor.fetchall()
print("\nInterests table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check sample interests
cursor.execute("SELECT * FROM interests LIMIT 10")
interests = cursor.fetchall()
print("\nSample interests:")
for interest in interests:
    print(f"  ID: {interest[0]}, Name: {interest[2]}")

conn.close()