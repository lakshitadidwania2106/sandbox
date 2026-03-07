from flask import Flask, render_template, request, jsonify
from agent import ask_agent

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    email = data.get("email", "lakshita21lr@gmail.com")
    query = data.get("query", "")
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
        
    try:
        response = ask_agent(query, email)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error calling agent: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.json
    email = data.get("email", "lakshita21lr@gmail.com")
    
    print("\n--- [SIMULATION] Starting Simulation Flow ---")
    
    import db_tool
    import gmail_tool
    import time
    import random
    import datetime

    # 1. Generate random mock data
    products = [
        "Smart Refrigerator", "Sony PlayStation 5", "Apple MacBook Pro", 
        "Dyson V15 Vacuum", "OLED Smart TV 55-inch", "Kindle Paperwhite",
        "Nintendo Switch", "Bose QuietComfort Headphones", "Logitech MX Master 3S"
    ]
    statuses = ["Delayed", "Processing", "Shipped Out", "Pending"]
    
    product = random.choice(products)
    status = random.choice(statuses)
    order_id = f"AMZ-{random.randint(1000, 9999)}"
    
    # Random future date 2-10 days from now
    future_days = random.randint(2, 10)
    expected_date = (datetime.datetime.now() + datetime.timedelta(days=future_days)).strftime("%Y-%m-%d")

    # 2. Update DB
    db_tool.insert_mock_order(
        email, 
        order_id, 
        product, 
        status, 
        expected_date
    )
    
    # 3. Send email
    subject = f"Amazon Order {order_id} Update"
    body = f"Dear Customer,\n\nWe are writing to inform you that your Amazon order {order_id} for the '{product}' has a status of: {status}.\nThe new expected delivery date is {expected_date}.\n\nThank you for shopping with us!"
    gmail_tool.send_email(email, subject, body)
    
    print(f"\n[SIMULATION] Simulated Order {order_id} for {product}. Waiting 4 seconds for Gmail to index...")
    time.sleep(4) 
    
    # 4. Analyze it with agent
    query = f"Analyze my latest Amazon order ({order_id}). Read the database and find the new email about it. Tell me what product it is, the ID, and when it will arrive based on the email and DB."
    
    try:
        response = ask_agent(query, email)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error calling agent during simulation: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
