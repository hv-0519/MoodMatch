#!/usr/bin/env python3
"""
FIXED: Database Test Script with CATEGORY_ID
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = "models/instance/moodmatch.db"

print("=" * 60)
print("DATABASE TEST - WITH CATEGORY_ID FIX")
print("=" * 60)

# Check if database exists
print(f"\n1. Checking database path: {DB_PATH}")
if os.path.exists(DB_PATH):
    print("   ✓ Database file exists")
else:
    print("   ✗ Database file NOT FOUND!")
    print(f"   Current directory: {os.getcwd()}")
    exit(1)

# Connect to database
try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print("   ✓ Database connection successful")
except Exception as e:
    print(f"   ✗ Database connection failed: {e}")
    exit(1)

# Check activities table structure
print("\n2. Checking activities table structure:")
try:
    cursor.execute("PRAGMA table_info(activities)")
    columns = cursor.fetchall()
    
    if not columns:
        print("   ✗ Activities table does NOT exist!")
        exit(1)
    
    print("   ✓ Activities table exists with columns:")
    has_category_id = False
    for col in columns:
        not_null = "NOT NULL" if col[3] else ""
        pk = "PRIMARY KEY" if col[5] else ""
        print(f"      - {col[1]} ({col[2]}) {not_null} {pk}")
        if col[1] == 'category_id':
            has_category_id = True
            if col[3]:  # NOT NULL
                print(f"        ⚠️  CRITICAL: category_id is NOT NULL!")
    
    if not has_category_id:
        print("   ℹ️  Note: category_id column not found in table")
    
except Exception as e:
    print(f"   ✗ Error checking table: {e}")
    exit(1)

# Check for categories table
print("\n3. Checking categories table:")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
    if cursor.fetchone():
        print("   ✓ Categories table exists")
        
        cursor.execute("SELECT * FROM categories LIMIT 10")
        categories = cursor.fetchall()
        print(f"   Available categories ({len(categories)}):")
        for cat in categories:
            cat_dict = dict(cat)
            # Try to display id and name
            cat_id = cat_dict.get('id', 'N/A')
            cat_name = cat_dict.get('name', cat_dict.get('category_name', 'N/A'))
            print(f"      ID: {cat_id}, Name: {cat_name}")
            
        # Get first category ID for testing
        if categories:
            first_category = categories[0]
            test_category_id = first_category['id'] if 'id' in first_category.keys() else 1
        else:
            test_category_id = 1
    else:
        print("   ⚠️  Categories table NOT found - using category_id = 1")
        test_category_id = 1
        
except Exception as e:
    print(f"   ⚠️  Error checking categories: {e}")
    test_category_id = 1

# Try to insert a test activity WITH category_id
print(f"\n4. Attempting to insert TEST activity with category_id={test_category_id}:")
test_data = {
    'name': 'TEST_ACTIVITY_' + datetime.now().strftime('%H%M%S'),
    'execution_type': 'physical',
    'description': 'Test activity with category_id',
    'priority': 5,
    'is_active': 1,
    'mood_tags': 'test, debug',
    'energy_level': 'medium',
    'location_type': 'indoor',
    'social_type': 'solo',
    'min_time': '15',
    'max_time': '30',
    'min_budget': '0',
    'max_budget': '10',
    'category_id': test_category_id  # CRITICAL FIX
}

try:
    cursor.execute("""
        INSERT INTO activities (
            name, execution_type, description, priority, is_active,
            mood_tags, energy_level, location_type, social_type,
            min_time, max_time, min_budget, max_budget, category_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        test_data['name'],
        test_data['execution_type'],
        test_data['description'],
        test_data['priority'],
        test_data['is_active'],
        test_data['mood_tags'],
        test_data['energy_level'],
        test_data['location_type'],
        test_data['social_type'],
        test_data['min_time'],
        test_data['max_time'],
        test_data['min_budget'],
        test_data['max_budget'],
        test_data['category_id']  # CRITICAL FIX
    ))
    
    conn.commit()
    
    last_id = cursor.lastrowid
    print(f"   ✓✓✓ SUCCESS! Test activity inserted!")
    print(f"   Activity ID: {last_id}")
    print(f"   Activity Name: {test_data['name']}")
    print(f"   Category ID: {test_data['category_id']}")
    
    # Verify insertion
    cursor.execute("SELECT * FROM activities WHERE id = ?", (last_id,))
    inserted = cursor.fetchone()
    
    if inserted:
        print("\n   Verified - Activity in database:")
        for key in inserted.keys():
            print(f"      {key}: {inserted[key]}")
    
except sqlite3.Error as e:
    conn.rollback()
    print(f"   ✗✗✗ INSERT FAILED: {e}")
    print("\n   SOLUTION: Your form MUST include category_id field!")
    
except Exception as e:
    conn.rollback()
    print(f"   ✗ Unexpected error: {e}")

# Final count
print("\n5. Final activity count:")
try:
    cursor.execute("SELECT COUNT(*) FROM activities")
    final_count = cursor.fetchone()[0]
    print(f"   Total activities: {final_count}")
except Exception as e:
    print(f"   Error: {e}")

conn.close()

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)
print("Your database requires category_id (NOT NULL constraint)")
print("Your form was missing this field!")
print("\nSOLUTION:")
print("1. Use the updated admin_fixed.py")
print("2. Use manage_activities_with_category.html")
print("3. Make sure categories table has data")
print("=" * 60)