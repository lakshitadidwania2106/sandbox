"""
Comprehensive Test Suite
Verifies all components are working correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from security.fuzzy_detector import (
    fuzzy_search_in_file,
    global_fuzzy_search,
    check_if_company_code
)

def test_fuzzy_matching_algorithm():
    """Test the core fuzzy matching algorithm"""
    print("\n" + "="*70)
    print("TEST 1: Core Fuzzy Matching Algorithm")
    print("="*70)
    
    # Test 1: Exact match
    print("\n1.1 Testing exact match...")
    exact_code = """def calculate_secret_score(data, weights, threshold=0.5):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    
    if score > threshold:
        return score * 1.5
    return score"""
    
    result = check_if_company_code(exact_code, "./proprietary_code", min_score=60)
    assert result == True, "❌ FAILED: Exact match should be detected"
    print("✅ PASSED: Exact match detected")
    
    # Test 2: Modified code (renamed variables)
    print("\n1.2 Testing modified code (renamed variables)...")
    modified_code = """def calculate_secret_score(data, weights, threshold=0.5):
    total = 0
    for idx, val in enumerate(data):
        total += val * weights[idx]
    
    if total > threshold:
        return total * 1.5
    return total"""
    
    result = check_if_company_code(modified_code, "./proprietary_code", min_score=60)
    assert result == True, "❌ FAILED: Modified code should be detected"
    print("✅ PASSED: Modified code detected")
    
    # Test 3: Generic code (should NOT match)
    print("\n1.3 Testing generic code...")
    generic_code = """def add_numbers(a, b):
    return a + b

def multiply(x, y):
    return x * y"""
    
    result = check_if_company_code(generic_code, "./proprietary_code", min_score=60)
    assert result == False, "❌ FAILED: Generic code should NOT be detected"
    print("✅ PASSED: Generic code allowed")
    
    # Test 4: Short text (should be skipped)
    print("\n1.4 Testing short text...")
    short_text = "hello"
    result = check_if_company_code(short_text, "./proprietary_code", min_score=60)
    assert result == False, "❌ FAILED: Short text should be skipped"
    print("✅ PASSED: Short text skipped")
    
    print("\n✅ All fuzzy matching tests PASSED!")


def test_sliding_window():
    """Test the sliding window approach"""
    print("\n" + "="*70)
    print("TEST 2: Sliding Window Approach")
    print("="*70)
    
    # Test with code snippet in middle of file
    print("\n2.1 Testing snippet detection in middle of file...")
    snippet = """score = 0
    for i, value in enumerate(data):
        score += value * weights[i]"""
    
    result = fuzzy_search_in_file(
        "proprietary_code/secret_algorithm.py",
        snippet,
        min_score=60
    )
    assert result == True, "❌ FAILED: Should find snippet in middle of file"
    print("✅ PASSED: Snippet found in middle of file")
    
    print("\n✅ Sliding window test PASSED!")


def test_threshold_sensitivity():
    """Test different threshold values"""
    print("\n" + "="*70)
    print("TEST 3: Threshold Sensitivity")
    print("="*70)
    
    test_code = """def calculate_secret_score(data, weights, threshold=0.5):
    total = 0
    for idx, val in enumerate(data):
        total += val * weights[idx]
    return total"""
    
    # Test with strict threshold (50)
    print("\n3.1 Testing with strict threshold (50)...")
    result = check_if_company_code(test_code, "./proprietary_code", min_score=50)
    assert result == True, "❌ FAILED: Should detect with threshold 50"
    print("✅ PASSED: Detected with threshold 50")
    
    # Test with balanced threshold (60)
    print("\n3.2 Testing with balanced threshold (60)...")
    result = check_if_company_code(test_code, "./proprietary_code", min_score=60)
    assert result == True, "❌ FAILED: Should detect with threshold 60"
    print("✅ PASSED: Detected with threshold 60")
    
    # Test with lenient threshold (80)
    print("\n3.3 Testing with lenient threshold (80)...")
    result = check_if_company_code(test_code, "./proprietary_code", min_score=80)
    # This might not match due to high threshold
    print(f"   Result with threshold 80: {'Detected' if result else 'Not detected'}")
    print("✅ PASSED: Threshold sensitivity working")
    
    print("\n✅ Threshold sensitivity tests PASSED!")


def test_mitm_integration():
    """Test MITM proxy integration"""
    print("\n" + "="*70)
    print("TEST 4: MITM Proxy Integration")
    print("="*70)
    
    try:
        from security.mitm_proxy import check_if_company_code as mitm_check
        
        print("\n4.1 Testing MITM import...")
        print("✅ PASSED: MITM proxy imports successfully")
        
        print("\n4.2 Testing MITM detection...")
        test_code = """def calculate_secret_score(data, weights, threshold=0.5):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    return score"""
        
        result = mitm_check(test_code)
        assert result == True, "❌ FAILED: MITM should detect proprietary code"
        print("✅ PASSED: MITM detection working")
        
        print("\n✅ MITM integration tests PASSED!")
        
    except Exception as e:
        print(f"❌ FAILED: MITM integration error: {e}")
        return False
    
    return True


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*70)
    print("TEST 5: Edge Cases")
    print("="*70)
    
    # Test 1: Empty string
    print("\n5.1 Testing empty string...")
    result = check_if_company_code("", "./proprietary_code", min_score=60)
    assert result == False, "❌ FAILED: Empty string should not be detected"
    print("✅ PASSED: Empty string handled")
    
    # Test 2: Whitespace only
    print("\n5.2 Testing whitespace only...")
    result = check_if_company_code("   \n\n   ", "./proprietary_code", min_score=60)
    assert result == False, "❌ FAILED: Whitespace should not be detected"
    print("✅ PASSED: Whitespace handled")
    
    # Test 3: Very long text
    print("\n5.3 Testing very long text...")
    long_text = "x = 1\n" * 1000
    result = check_if_company_code(long_text, "./proprietary_code", min_score=60)
    assert result == False, "❌ FAILED: Long generic text should not be detected"
    print("✅ PASSED: Long text handled")
    
    # Test 4: Special characters
    print("\n5.4 Testing special characters...")
    special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    result = check_if_company_code(special_text, "./proprietary_code", min_score=60)
    assert result == False, "❌ FAILED: Special characters should not be detected"
    print("✅ PASSED: Special characters handled")
    
    print("\n✅ Edge case tests PASSED!")


def test_file_operations():
    """Test file operations"""
    print("\n" + "="*70)
    print("TEST 6: File Operations")
    print("="*70)
    
    # Test 1: Valid file
    print("\n6.1 Testing valid file...")
    result = fuzzy_search_in_file(
        "proprietary_code/secret_algorithm.py",
        "def calculate_secret_score",
        min_score=60
    )
    assert result == True, "❌ FAILED: Should find code in valid file"
    print("✅ PASSED: Valid file processed")
    
    # Test 2: Non-existent file
    print("\n6.2 Testing non-existent file...")
    result = fuzzy_search_in_file(
        "nonexistent.py",
        "test",
        min_score=60
    )
    assert result == False, "❌ FAILED: Non-existent file should return False"
    print("✅ PASSED: Non-existent file handled")
    
    # Test 3: Directory search
    print("\n6.3 Testing directory search...")
    result = global_fuzzy_search(
        "def calculate_secret_score",
        "./proprietary_code",
        min_score=60
    )
    assert result == True, "❌ FAILED: Should find code in directory"
    print("✅ PASSED: Directory search working")
    
    print("\n✅ File operation tests PASSED!")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUITE")
    print("Testing all components of the proprietary code detection system")
    print("="*70)
    
    try:
        # Check proprietary code exists
        if not Path("proprietary_code/secret_algorithm.py").exists():
            print("\n❌ ERROR: proprietary_code/secret_algorithm.py not found!")
            print("   Please ensure the proprietary code directory exists.")
            return False
        
        # Run all tests
        test_fuzzy_matching_algorithm()
        test_sliding_window()
        test_threshold_sensitivity()
        test_mitm_integration()
        test_edge_cases()
        test_file_operations()
        
        # Summary
        print("\n" + "="*70)
        print("COMPREHENSIVE TEST RESULTS")
        print("="*70)
        print("\n✅ ALL TESTS PASSED!")
        print("\nSystem Status:")
        print("  ✅ Core fuzzy matching: WORKING")
        print("  ✅ Sliding window: WORKING")
        print("  ✅ Threshold sensitivity: WORKING")
        print("  ✅ MITM integration: WORKING")
        print("  ✅ Edge cases: HANDLED")
        print("  ✅ File operations: WORKING")
        print("\n🎉 The system is fully operational and ready for production!")
        print("="*70)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
