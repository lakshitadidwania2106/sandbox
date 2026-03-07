"""
SigmaShield-Style Detection (Exact Implementation)
===================================================

This is a direct port of SigmaShield's fuzzy search logic.
Simple, fast, and proven to work.

Key differences from our enhanced version:
1. NO normalization (only .strip())
2. Simple sliding window
3. Early termination on first match
4. Uses RapidFuzz ratio (0-100 scale)
"""

from rapidfuzz import fuzz
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def fuzzy_search_in_file(file_path, target_snippet, min_score=60):
    """
    Search for similar code in a file using sliding window + fuzzy matching.
    
    This is the EXACT logic from SigmaShield - proven to work.
    
    Args:
        file_path: Path to file to search
        target_snippet: Code snippet to find
        min_score: Minimum similarity score (0-100)
    
    Returns:
        True if match found, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            full_code = f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return False

    # IMPORTANT: Only strip, no other normalization!
    target_snippet = target_snippet.strip()
    
    best_score = 0
    best_match = ""
    best_index = -1

    code_lines = full_code.splitlines()
    snippet_lines = target_snippet.splitlines()
    snippet_len = len(snippet_lines)

    # Sliding window approach
    for i in range(len(code_lines) - snippet_len + 1):
        window = "\n".join(code_lines[i:i + snippet_len])
        
        # Calculate fuzzy similarity (IMPORTANT: strip both sides)
        score = fuzz.ratio(window.strip(), target_snippet)
        
        if score > best_score:
            best_score = score
            best_match = window
            best_index = i

    # If score exceeds threshold, we found a match
    if best_score >= min_score:
        logger.warning(
            f"\n✅ Match found in file: {file_path}\n"
            f"📌 Match (score: {best_score}) starting at line {best_index + 1}:\n"
            f"{best_match}"
        )
        return True  # Signal to stop further search

    return False  # No good match in this file


def global_fuzzy_search(target_snippet, folder_path=None, min_score=60):
    """
    Search for similar code across all Python files in a directory.
    
    This is the EXACT logic from SigmaShield.
    
    Args:
        target_snippet: Code snippet to find
        folder_path: Directory to search (defaults to current directory)
        min_score: Minimum similarity score (0-100)
    
    Returns:
        True if match found, False otherwise
    """
    if folder_path is None:
        folder_path = "./proprietary_code"
    
    folder = Path(folder_path)
    
    if not folder.exists():
        logger.error(f"Directory not found: {folder_path}")
        return False
    
    logger.info(f"Searching in: {folder_path}")
    
    # Search all Python files
    for file_path in folder.rglob("*.py"):
        # Skip test files and venv
        if 'test' in str(file_path).lower() or 'venv' in str(file_path):
            continue
        
        found = fuzzy_search_in_file(file_path, target_snippet, min_score)
        
        if found:
            return True  # Early return on first match
    
    logger.info("❌ No matching code snippet found in any file.")
    return False


def check_if_company_code(text, folder_path=None, min_score=60):
    """
    Check if text contains company proprietary code.
    
    This is the EXACT logic from SigmaShield's checker.py.
    
    Args:
        text: Text to check
        folder_path: Directory with proprietary code
        min_score: Minimum similarity score (0-100)
    
    Returns:
        True if proprietary code detected, False otherwise
    """
    logger.debug(f"Checking text (length: {len(text)})")
    
    # Quick length check
    if len(text) < 20:
        return False
    
    # Run fuzzy search
    matched = global_fuzzy_search(text, folder_path, min_score)
    
    logger.debug(f"Match result: {matched}")
    
    return matched


# =============================================================================
# Quick Test Function
# =============================================================================

def quick_test():
    """Quick test to verify detection is working."""
    
    print("="*70)
    print("SIGMASHIELD-STYLE DETECTION TEST")
    print("="*70)
    
    # Test 1: Exact copy of proprietary code
    print("\n1. Testing with EXACT proprietary code:")
    print("-" * 70)
    
    test_code = """def calculate_secret_score(data, weights, threshold=0.5):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    
    if score > threshold:
        return score * 1.5
    return score"""
    
    print(test_code)
    result = check_if_company_code(test_code, "./proprietary_code", min_score=60)
    print(f"\nResult: {'🚨 BLOCKED' if result else '✅ ALLOWED'}")
    
    # Test 2: Slightly modified code
    print("\n2. Testing with MODIFIED proprietary code:")
    print("-" * 70)
    
    test_code2 = """def calculate_secret_score(data, weights, threshold=0.5):
    total = 0
    for idx, val in enumerate(data):
        total += val * weights[idx]
    
    if total > threshold:
        return total * 1.5
    return total"""
    
    print(test_code2)
    result2 = check_if_company_code(test_code2, "./proprietary_code", min_score=60)
    print(f"\nResult: {'🚨 BLOCKED' if result2 else '✅ ALLOWED'}")
    
    # Test 3: Generic code (should NOT match)
    print("\n3. Testing with GENERIC code:")
    print("-" * 70)
    
    test_code3 = """def add_numbers(a, b):
    return a + b

def multiply(x, y):
    return x * y"""
    
    print(test_code3)
    result3 = check_if_company_code(test_code3, "./proprietary_code", min_score=60)
    print(f"\nResult: {'🚨 BLOCKED' if result3 else '✅ ALLOWED'}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(level=logging.INFO)
    
    quick_test()
