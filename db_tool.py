import sqlite3

DB_NAME = "company.db"

def search_orders(email):
    """Searches the database for orders associated with a given email address."""
    print(f"\n--- [DB TOOL] Searching orders for {email} ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT order_id, product, status, expected_delivery FROM orders WHERE customer_email=?",
        (email,)
    )

    results = cursor.fetchall()
    conn.close()

    if not results:
        return "No orders found."

    formatted_results = []
    for row in results:
        formatted_results.append(f"Order ID: {row[0]}, Product: {row[1]}, Status: {row[2]}, Expected Delivery: {row[3]}")
    
    return "\n".join(formatted_results)


def search_tickets(email):
    """Searches the database for support tickets associated with a given email address."""
    print(f"\n--- [DB TOOL] Searching tickets for {email} ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ticket_id, issue, status, created_at FROM tickets WHERE customer_email=?",
        (email,)
    )

    results = cursor.fetchall()
    conn.close()

    if not results:
        return "No support tickets found."

    formatted_results = []
    for row in results:
        formatted_results.append(f"Ticket ID: {row[0]}, Issue: '{row[1]}', Status: {row[2]}, Created: {row[3]}")
    
    return "\n".join(formatted_results)

def create_ticket(email, issue):
    """Creates a new support ticket in the database for the given email and issue."""
    import datetime
    print(f"\n--- [DB TOOL] Creating new ticket for {email} ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    created_at = datetime.datetime.now().strftime("%Y-%m-%d")
    status = "Open"
    
    cursor.execute(
        "INSERT INTO tickets (customer_email, issue, status, created_at) VALUES (?, ?, ?, ?)",
        (email, issue, status, created_at)
    )
    
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return f"Ticket successfully created. Ticket ID: {ticket_id}, Status: {status}"

def insert_mock_order(email, order_id, product, status, expected_delivery):
    """Inserts a mock order into the database."""
    print(f"\n--- [DB TOOL] Inserting mock order {order_id} for {email} ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO orders (order_id, customer_email, product, status, expected_delivery) VALUES (?, ?, ?, ?, ?)",
        (order_id, email, product, status, expected_delivery)
    )
    conn.commit()
    conn.close()
    return f"Order {order_id} inserted successfully."
