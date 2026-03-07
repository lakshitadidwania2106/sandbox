from flask import Flask, render_template, request, jsonify
from agent import ask_agent
import sys
sys.path.insert(0, '/home/unichronic/sandbox')
from security.lakera_guard import scan_prompt
from security.presidio_scanner import scan_output, redact_output

app = Flask(__name__)

def process_through_security(text, user_email=""):
    """Process text through all Bifrost security layers"""
    result = {
        'blocked': False,
        'scrubbed': False,
        'layers': {},
        'clean_text': text,
        'message': ''
    }
    
    # LAYER 1: Lakera Guard
    lakera_result = scan_prompt(text)
    if lakera_result.flagged:
        result['blocked'] = True
        result['message'] = f'🚫 Security Alert: Prompt injection detected (ID: {lakera_result.request_uuid})'
        result['layers']['lakera'] = 'BLOCKED'
        return result
    result['layers']['lakera'] = 'PASS'
    
    # LAYER 2: OPA Policy (simulated)
    result['layers']['opa'] = 'PASS'
    
    # LAYER 3: Presidio Input
    pii_result = scan_output(text)
    if pii_result.has_pii:
        result['scrubbed'] = True
        result['clean_text'] = redact_output(text)
        result['layers']['presidio_input'] = f'SCRUBBED ({", ".join(pii_result.entity_types)})'
    else:
        result['layers']['presidio_input'] = 'PASS'
    
    return result

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/test", methods=["POST"])
def test_security():
    """Test endpoint for security dashboard"""
    data = request.json
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    # Process through security layers
    security_check = process_through_security(text)
    
    if security_check['blocked']:
        return jsonify({
            "blocked": True,
            "message": security_check['message'],
            "layers": security_check['layers']
        })
    
    # Simulate agent response
    agent_response = f"Processed query: '{security_check['clean_text']}'. This is a simulated agent response for security testing."
    
    # Check output for PII
    output_pii = scan_output(agent_response)
    if output_pii.has_pii:
        agent_response = redact_output(agent_response)
        security_check['layers']['presidio_output'] = 'SCRUBBED'
    else:
        security_check['layers']['presidio_output'] = 'PASS'
    
    return jsonify({
        "blocked": False,
        "response": agent_response,
        "pii_scrubbed": security_check['scrubbed'],
        "layers": security_check['layers']
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    email = data.get("email", "lakshita21lr@gmail.com")
    query = data.get("query", "")
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    # 🛡️ BIFROST SECURITY CHECK
    security_check = process_through_security(query, email)
    
    if security_check['blocked']:
        return jsonify({
            "error": security_check['message'],
            "security_layers": security_check['layers']
        }), 403
    
    # Use scrubbed text if PII was found
    safe_query = security_check['clean_text']
    
    try:
        response = ask_agent(safe_query, email)
        
        # LAYER 4: Check agent response for PII
        output_pii = scan_output(response)
        if output_pii.has_pii:
            response = redact_output(response)
        
        return jsonify({
            "response": response,
            "security_layers": security_check['layers'],
            "pii_scrubbed": security_check['scrubbed']
        })
    except Exception as e:
        print(f"Error calling agent: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.json
    email = data.get("email", "lakshita21lr@gmail.com")
    
    print("\n--- [SIMULATION] Starting Simulation Flow ---")
    print("🛡️ Bifrost Security: ACTIVE")
    
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
    
    # 4. Analyze it with agent (with security)
    query = f"Analyze my latest Amazon order ({order_id}). Read the database and find the new email about it. Tell me what product it is, the ID, and when it will arrive based on the email and DB."
    
    # 🛡️ BIFROST SECURITY CHECK
    security_check = process_through_security(query, email)
    
    if security_check['blocked']:
        return jsonify({
            "error": security_check['message'],
            "security_layers": security_check['layers']
        }), 403
    
    safe_query = security_check['clean_text']
    
    try:
        response = ask_agent(safe_query, email)
        
        # LAYER 4: Check agent response for PII
        output_pii = scan_output(response)
        if output_pii.has_pii:
            response = redact_output(response)
            print("🔒 Bifrost: PII scrubbed from agent response")
        
        print("✅ Bifrost: Request processed through all security layers")
        return jsonify({
            "response": response,
            "security_layers": security_check['layers']
        })
    except Exception as e:
        print(f"Error calling agent during simulation: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
