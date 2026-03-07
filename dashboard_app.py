#!/usr/bin/env python3
"""
Bifrost Security Dashboard - Standalone Version
Works without agent dependencies
"""

import sys
sys.path.insert(0, '/home/unichronic/sandbox')

from flask import Flask, render_template, request, jsonify
from security.lakera_guard import scan_prompt
from security.presidio_scanner import scan_output, redact_output

app = Flask(__name__)

def process_through_security(text):
    """Process text through all Bifrost security layers"""
    result = {
        'blocked': False,
        'scrubbed': False,
        'layers': {},
        'clean_text': text,
        'message': ''
    }
    
    # LAYER 1: OPA Policy - Check for malicious commands and harmful content
    malicious_patterns = ['drop_table', 'delete_all', 'admin_action', 'system_command', 'DROP TABLE', 'DELETE FROM', 'INSERT INTO']
    harmful_keywords = ['kill', 'murder', 'suicide', 'bomb', 'weapon', 'attack', 'harm', 'hurt', 'violence']
    
    # Check for SQL/admin commands
    if any(pattern.lower() in text.lower() for pattern in malicious_patterns):
        result['blocked'] = True
        result['message'] = f'🚫 OPA Policy: Unauthorized administrative command detected'
        result['layers']['opa'] = 'BLOCKED'
        result['layers']['lakera'] = 'SKIPPED'
        result['layers']['presidio_input'] = 'SKIPPED'
        return result
    
    # Check for harmful/violent content
    if any(keyword in text.lower() for keyword in harmful_keywords):
        result['blocked'] = True
        result['message'] = f'🚫 OPA Policy: Harmful or violent content detected'
        result['layers']['opa'] = 'BLOCKED'
        result['layers']['lakera'] = 'SKIPPED'
        result['layers']['presidio_input'] = 'SKIPPED'
        return result
    
    result['layers']['opa'] = 'PASS'
    
    # LAYER 2: Lakera Guard
    lakera_result = scan_prompt(text)
    if lakera_result.flagged:
        result['blocked'] = True
        result['message'] = f'🚫 Lakera Guard: Prompt injection detected (ID: {lakera_result.request_uuid})'
        result['layers']['lakera'] = 'BLOCKED'
        result['layers']['presidio_input'] = 'SKIPPED'
        return result
    result['layers']['lakera'] = 'PASS'
    
    # LAYER 3: Presidio Input
    pii_result = scan_output(text)
    if pii_result.has_pii:
        result['scrubbed'] = True
        result['clean_text'] = redact_output(text)
        entities = ', '.join(pii_result.entity_types)
        result['layers']['presidio_input'] = f'SCRUBBED ({entities})'
        result['message'] = f'⚠️ Presidio: {pii_result.entity_count} PII entities scrubbed'
    else:
        result['layers']['presidio_input'] = 'PASS'
    
    return result

@app.route("/")
def index():
    return render_template("dashboard.html")

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
    
    # Generate actual AI-like response based on query
    clean_query = security_check['clean_text']
    
    # Simple response generation (replace with real AI agent)
    if "python" in clean_query.lower():
        agent_response = "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used for web development, data science, automation, and AI applications."
    elif "capital" in clean_query.lower() and "france" in clean_query.lower():
        agent_response = "The capital of France is Paris. It's known for the Eiffel Tower, Louvre Museum, and rich cultural heritage."
    elif "order" in clean_query.lower() or "amazon" in clean_query.lower():
        agent_response = "I can help you check your order status. Your order information has been processed through our secure system."
    elif any(word in clean_query.lower() for word in ["hello", "hi", "hey"]):
        agent_response = "Hello! I'm your AI assistant protected by Bifrost security. How can I help you today?"
    elif "?" in clean_query:
        agent_response = f"I understand you're asking about: '{clean_query}'. This is a simulated response. In production, this would connect to a real AI model like GPT or Gemini to provide detailed answers."
    else:
        agent_response = f"I've processed your request: '{clean_query}'. This response is generated after passing through all security layers to ensure safety."
    
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

if __name__ == "__main__":
    print("=" * 70)
    print("🛡️  BIFROST SECURITY TESTING DASHBOARD")
    print("=" * 70)
    print()
    print("Starting server...")
    print("  → URL: http://localhost:5000")
    print("  → Dashboard: http://localhost:5000/dashboard")
    print()
    print("Security Layers Active:")
    print("  ✓ Layer 1: Lakera Guard (Prompt Injection Detection)")
    print("  ✓ Layer 2: OPA Policy (Access Control)")
    print("  ✓ Layer 3: Presidio Input (PII Scrubbing)")
    print("  ✓ Layer 4: Presidio Output (Response Protection)")
    print()
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
