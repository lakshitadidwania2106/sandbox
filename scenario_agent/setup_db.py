import sqlite3

conn = sqlite3.connect("company.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    role TEXT
)
""")

cursor.execute("INSERT INTO users (name, role) VALUES ('Alice', 'admin')")
cursor.execute("INSERT INTO users (name, role) VALUES ('Bob', 'employee')")
cursor.execute("INSERT INTO users (name, role) VALUES ('Charlie', 'admin')")

conn.commit()
conn.close()

print("Database created successfully.")