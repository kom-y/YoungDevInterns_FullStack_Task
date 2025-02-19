import sqlite3

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create admin table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Create students table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Save changes and close
conn.commit()
conn.close()

print("Database initialized successfully!")
