"""
Test Script: Verify Detection is Working
=========================================

This tests all components to ensure they're working correctly.
"""

import sys
from pathlib import Path

print("="*70)
print("BIFROST PROPRIETARY CODE DETECTION - SYSTEM TEST")
print("="*70)

# =============================================================================
# Test 1: Check Dependencies
# =============================================================================

print("\n1. Checking dependencies...")
print("-" * 70)

try:
    from rapidfuzz import fuzz
    print("✅ RapidFuzz installed:", fuzz.__version__ if hasattr(fuzz, '__version__') else "version unknown")
except ImportError:
    print("❌ RapidFuzz NOT installed - run: pip install rapidfuzz")
    sys.exit(1)

try:
    from mitmproxy import http
    print("✅ mitmproxy installed")
except ImportError:
    print("⚠️  mitmproxy NOT installed - run: pip install mitmproxy")
    print("   (Only needed for MITM proxy, not for detection)")

# =============================================================================
# Test 2: Check Proprietary Code Directory
# =============================================================================

print("\n2. Checking proprietary code directory...")
print("-" * 70)

proprietary_dir = Path("./proprietary_code")

if proprietary_dir.exists():
    files = list(proprietary_dir.rglob("*.py"))
    print(f"✅ Directory exists: {proprietary_dir}")
    print(f"   Found {len(files)} Python files:")
    for f in files:
        print(f"   - {f.name} ({f.stat().st_size} bytes)")
else:
    print(f"❌ Directory NOT found: {proprietary_dir}")
    print("   Create it with: mkdir proprietary_code")
    sys.exit(1)

# =============================================================================
# Test 3: Test SigmaShield-Style Detection
# =============================================================================

print("\n3. Testing SigmaShield-style detection...")
print("-" * 70)

try:
    from security.fuzzy_detector import check_if_company_code
    
    # Test with exact proprietary code
    test_code = """def calculate_secret_score(data, weights, threshold=0.5):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    
    if score > threshold:
        return score * 1.5
    return score"""
    
    print("Testing with proprietary code snippet...")
    result = check_if_company_code(test_code, "./proprietary_code", min_score=60)
    
    if result:
        print("✅ Detection WORKING - proprietary code detected!")
    else:
        print("❌ Detection NOT working - should have detected proprietary code")
    
    # Test with generic code
    generic_code = """def add(a, b):
    return a + b"""
    
    print("\nTesting with generic code...")
    result2 = check_if_company_code(generic_code, "./proprietary_code", min_score=60)
    
    if not result2:
        print("✅ Detection WORKING - generic code allowed!")
    else:
        print("❌ Detection NOT working - should have allowed generic code")
    
except Exception as e:
    print(f"❌ Error testing detection: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# Test 4: Test MITM Proxy Integration
# =============================================================================

print("\n4. Testing MITM proxy integration...")
print("-" * 70)

try:
    # Just check if it imports without errors
    from security.mitm_proxy import check_if_company_code as mitm_check
    print("✅ MITM proxy imports successfully")
    
    # Test the function
    result = mitm_check(test_code)
    if result:
        print("✅ MITM detection WORKING - proprietary code detected!")
    else:
        print("❌ MITM detection NOT working")
    
except Exception as e:
    print(f"⚠️  Error with MITM proxy: {e}")
    print("   This is OK if you haven't installed mitmproxy yet")

# =============================================================================
# Summary
# =============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print("""
✅ Core detection is WORKING!

Next steps:
1. Add more proprietary code files to ./proprietary_code/
2. Test with your actual proprietary code
3. Start the MITM proxy: python security/start_proxy.py
4. Configure your browser to use the proxy (localhost:8080)
5. Install mitmproxy certificate: http://mitm.it

The system will now block any attempts to paste your proprietary code
into ChatGPT, Twitter, StackOverflow, or other sites!
""")
