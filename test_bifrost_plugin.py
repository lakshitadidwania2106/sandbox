"""
Test Script for Bifrost Proprietary Code Detection Plugin
==========================================================

This script tests the Bifrost plugin to ensure it's working correctly.
"""

import requests
import json
import sys

# Configuration
BIFROST_URL = "http://localhost:8080"  # Change this to your Bifrost URL
API_KEY = "your-api-key-here"  # Change this to your API key

print("="*70)
print("BIFROST PROPRIETARY CODE DETECTION PLUGIN TEST")
print("="*70)

# Test 1: Proprietary Code (Should be BLOCKED)
print("\n1. Testing with PROPRIETARY code...")
print("-" * 70)

proprietary_code = """def calculate_secret_score(data, weights, threshold=0.5):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    
    if score > threshold:
        return score * 1.5
    return score"""

print("Code being sent:")
print(proprietary_code)

try:
    response = requests.post(
        f"{BIFROST_URL}/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        json={
            "model": "gpt-4",
            "messages": [
                {
                    "role": "user",
                    "content": f"Explain this code:\n\n{proprietary_code}"
                }
            ]
        },
        timeout=10
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 403:
        print("✅ CORRECT: Request was BLOCKED (403 Forbidden)")
        try:
            error_data = response.json()
            print(f"Error Message: {error_data.get('error', {}).get('message', 'N/A')}")
        except:
            print(f"Response: {response.text}")
    elif response.status_code == 200:
        print("❌ WRONG: Request was ALLOWED (should have been blocked)")
        print("The plugin may not be working correctly")
    else:
        print(f"⚠️  UNEXPECTED: Got status code {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Could not connect to Bifrost")
    print(f"   Make sure Bifrost is running at {BIFROST_URL}")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Test 2: Generic Code (Should be ALLOWED)
print("\n2. Testing with GENERIC code...")
print("-" * 70)

generic_code = """def add_numbers(a, b):
    return a + b

def multiply_numbers(x, y):
    return x * y"""

print("Code being sent:")
print(generic_code)

try:
    response = requests.post(
        f"{BIFROST_URL}/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        json={
            "model": "gpt-4",
            "messages": [
                {
                    "role": "user",
                    "content": f"Explain this code:\n\n{generic_code}"
                }
            ]
        },
        timeout=10
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ CORRECT: Request was ALLOWED (200 OK)")
        try:
            data = response.json()
            print(f"Response received from LLM")
        except:
            pass
    elif response.status_code == 403:
        print("❌ WRONG: Request was BLOCKED (should have been allowed)")
        print("This is a false positive - consider adjusting the threshold")
        try:
            error_data = response.json()
            print(f"Error Message: {error_data.get('error', {}).get('message', 'N/A')}")
        except:
            print(f"Response: {response.text}")
    else:
        print(f"⚠️  UNEXPECTED: Got status code {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Test 3: Modified Proprietary Code (Should be BLOCKED)
print("\n3. Testing with MODIFIED proprietary code...")
print("-" * 70)

modified_code = """def calculate_secret_score(data, weights, threshold=0.5):
    total = 0
    for idx, val in enumerate(data):
        total += val * weights[idx]
    
    if total > threshold:
        return total * 1.5
    return total"""

print("Code being sent (variable names changed):")
print(modified_code)

try:
    response = requests.post(
        f"{BIFROST_URL}/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        json={
            "model": "gpt-4",
            "messages": [
                {
                    "role": "user",
                    "content": f"Explain this code:\n\n{modified_code}"
                }
            ]
        },
        timeout=10
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 403:
        print("✅ CORRECT: Request was BLOCKED (403 Forbidden)")
        print("Fuzzy matching detected the similarity despite variable name changes")
        try:
            error_data = response.json()
            print(f"Error Message: {error_data.get('error', {}).get('message', 'N/A')}")
        except:
            print(f"Response: {response.text}")
    elif response.status_code == 200:
        print("⚠️  ALLOWED: Request was not blocked")
        print("Similarity may be below threshold - this is expected with threshold=60")
    else:
        print(f"⚠️  UNEXPECTED: Got status code {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

print("""
If all tests passed:
✅ Plugin is working correctly!
✅ Proprietary code is being detected and blocked
✅ Generic code is being allowed

If tests failed:
1. Check Bifrost logs: tail -f /var/log/bifrost/bifrost.log
2. Verify plugin is loaded: grep "proprietary-detection" /var/log/bifrost/bifrost.log
3. Check proprietary code directory: ls -la proprietary_code/
4. Verify plugin configuration in Bifrost config
5. Try adjusting similarity_threshold in config

For more help, see: BIFROST_INTEGRATION_GUIDE.md
""")

print("="*70)
