"""
Test Detection of Formatted vs Minified Code
"""

from security.fuzzy_detector import check_if_company_code

print("="*70)
print("TEST: Formatted vs Minified Code Detection")
print("="*70)

# Test 1: Formatted code (with proper indentation)
print("\n1. Testing FORMATTED code (with newlines and indentation):")
print("-"*70)

formatted_code = """def calculate_secret_score(data, weights, threshold=0.5):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    
    if score > threshold:
        return score * 1.5
    return score"""

print(formatted_code)
result1 = check_if_company_code(formatted_code, "./proprietary_code", min_score=60)
print(f"\nResult: {'🚨 BLOCKED' if result1 else '✅ ALLOWED'}")

# Test 2: Minified code (all on one line)
print("\n\n2. Testing MINIFIED code (all on one line):")
print("-"*70)

minified_code = "def calculate_secret_score(data, weights, threshold=0.5): score = 0 for i, value in enumerate(data): score += value * weights[i] if score > threshold: return score * 1.5 return score"

print(minified_code)
result2 = check_if_company_code(minified_code, "./proprietary_code", min_score=60)
print(f"\nResult: {'🚨 BLOCKED' if result2 else '✅ ALLOWED'}")

# Test 3: Minified with different spacing
print("\n\n3. Testing MINIFIED with different spacing:")
print("-"*70)

minified_code2 = "def calculate_secret_score(data,weights,threshold=0.5):score=0 for i,value in enumerate(data):score+=value*weights[i] if score>threshold:return score*1.5 return score"

print(minified_code2)
result3 = check_if_company_code(minified_code2, "./proprietary_code", min_score=60)
print(f"\nResult: {'🚨 BLOCKED' if result3 else '✅ ALLOWED'}")

# Test 4: Generic code (should NOT match)
print("\n\n4. Testing GENERIC code (should be allowed):")
print("-"*70)

generic_code = "def add(a, b): return a + b"

print(generic_code)
result4 = check_if_company_code(generic_code, "./proprietary_code", min_score=60)
print(f"\nResult: {'🚨 BLOCKED' if result4 else '✅ ALLOWED'}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Formatted code:     {'BLOCKED ✅' if result1 else 'ALLOWED ❌'}")
print(f"Minified code:      {'BLOCKED ✅' if result2 else 'ALLOWED ❌'}")
print(f"Minified (no space):{'BLOCKED ✅' if result3 else 'ALLOWED ❌'}")
print(f"Generic code:       {'ALLOWED ✅' if not result4 else 'BLOCKED ❌'}")
print()

if result1 and result2 and result3 and not result4:
    print("🎉 ALL TESTS PASSED!")
    print("   - Formatted code detected ✅")
    print("   - Minified code detected ✅")
    print("   - Generic code allowed ✅")
else:
    print("⚠️  SOME TESTS FAILED")
    if not result1:
        print("   - Formatted code NOT detected ❌")
    if not result2:
        print("   - Minified code NOT detected ❌")
    if not result3:
        print("   - Minified (no space) NOT detected ❌")
    if result4:
        print("   - Generic code was blocked (should be allowed) ❌")

print("="*70)
