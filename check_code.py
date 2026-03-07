#!/usr/bin/env python3
"""
Quick CLI tool to check if code is proprietary.

Usage:
    python check_code.py "def my_function(): pass"
    python check_code.py --file mycode.py
    python check_code.py --interactive
"""

import sys
import argparse
from pathlib import Path
from security.fuzzy_detector import check_if_company_code


def check_text(text: str, threshold: int = 60):
    """Check if text contains proprietary code."""
    print(f"Checking {len(text)} characters...")
    print("-" * 70)
    
    is_proprietary = check_if_company_code(
        text,
        folder_path="./proprietary_code",
        min_score=threshold
    )
    
    print("-" * 70)
    if is_proprietary:
        print("🚨 RESULT: PROPRIETARY CODE DETECTED - WOULD BE BLOCKED")
    else:
        print("✅ RESULT: NO PROPRIETARY CODE - WOULD BE ALLOWED")
    
    return is_proprietary


def check_file(file_path: str, threshold: int = 60):
    """Check if file contains proprietary code."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return False
    
    print(f"Reading file: {file_path}")
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    return check_text(text, threshold)


def interactive_mode(threshold: int = 60):
    """Interactive mode - paste code and check."""
    print("="*70)
    print("INTERACTIVE MODE")
    print("="*70)
    print("Paste your code below, then press Ctrl+D (Unix) or Ctrl+Z (Windows)")
    print("to check. Type 'quit' to exit.")
    print("-" * 70)
    
    while True:
        try:
            print("\nPaste code (Ctrl+D/Ctrl+Z when done):")
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip().lower() == 'quit':
                        return
                    lines.append(line)
                except EOFError:
                    break
            
            text = '\n'.join(lines)
            
            if text.strip():
                check_text(text, threshold)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Check if code contains proprietary content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check_code.py "def my_function(): pass"
  python check_code.py --file mycode.py
  python check_code.py --interactive
  python check_code.py --file mycode.py --threshold 70
        """
    )
    
    parser.add_argument(
        'code',
        nargs='?',
        help='Code to check (as string)'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='Check code from file'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interactive mode (paste code)'
    )
    
    parser.add_argument(
        '--threshold', '-t',
        type=int,
        default=60,
        help='Similarity threshold (0-100, default: 60)'
    )
    
    args = parser.parse_args()
    
    # Check if proprietary_code directory exists
    if not Path('./proprietary_code').exists():
        print("❌ Error: ./proprietary_code directory not found")
        print("Create it and add your proprietary code files:")
        print("  mkdir proprietary_code")
        print("  cp /path/to/your/code/*.py proprietary_code/")
        sys.exit(1)
    
    # Determine mode
    if args.interactive:
        interactive_mode(args.threshold)
    elif args.file:
        result = check_file(args.file, args.threshold)
        sys.exit(0 if not result else 1)
    elif args.code:
        result = check_text(args.code, args.threshold)
        sys.exit(0 if not result else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
