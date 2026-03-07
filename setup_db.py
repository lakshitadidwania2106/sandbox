import sqlite3
import os

if os.path.exists("company.db"):
    os.remove("company.db")

conn = sqlite3.connect("company.db")
cursor = conn.cursor()

# Create customers table
cursor.execute("""
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE
)
""")

# Create orders table
cursor.execute("""
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_email TEXT,
    product TEXT,
    status TEXT,
    expected_delivery TEXT
)
""")

# Create tickets table
cursor.execute("""
CREATE TABLE tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_email TEXT,
    issue TEXT,
    status TEXT,
    created_at TEXT
)
""")

# Insert Customers
cursor.execute("INSERT INTO customers (name, email) VALUES ('Lakshita', 'lakshita21lr@gmail.com')")

# Insert Orders for Lakshita
cursor.execute("""
INSERT INTO orders (order_id, customer_email, product, status, expected_delivery) 
VALUES ('AMZ1234', 'lakshita21lr@gmail.com', 'Wireless Headphones', 'Shipped', '2026-03-10')
""")

# Insert a sample ticket
cursor.execute("""
INSERT INTO tickets (customer_email, issue, status, created_at)
VALUES ('lakshita21lr@gmail.com', 'complaining about delivery delay', 'In Progress', '2026-03-02')
""")

conn.commit()
conn.close()

print("E-commerce database created successfully.")