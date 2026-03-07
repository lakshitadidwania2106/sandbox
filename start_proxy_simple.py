"""
Simple MITM Proxy Starter
==========================

Starts the proxy WITHOUT automatically configuring system proxy.
You configure the proxy manually after it's running.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Start mitmproxy."""
    print("="*70)
    print("BIFROST MITM PROXY - SIMPLE START")
    print("="*70)
    print()
    
    # Check if mitmproxy is installed
    try:
        result = subprocess.run(["mitmdump", "--version"], capture_output=True, text=True)
        print(f"✅ mitmproxy found")
    except FileNotFoundError:
        print("❌ mitmproxy not installed!")
        print("   Install with: pip install mitmproxy")
        return 1
    
    # Check proprietary code
    code_dir = Path("./proprietary_code")
    if code_dir.exists():
        py_files = list(code_dir.glob("*.py"))
        print(f"✅ Proprietary code directory found: {code_dir}")
        print(f"   Found {len(py_files)} Python files to protect")
    else:
        print(f"⚠️  Warning: {code_dir} not found")
        print("   Add your proprietary code files to test detection")
    
    print()
    print("🚀 Starting mitmproxy on port 8080...")
    print()
    print("="*70)
    print("IMPORTANT: Configure proxy AFTER you see 'Proxy server listening'")
    print("="*70)
    print()
    print("1. Wait for: 'Proxy server listening at http://0.0.0.0:8080'")
    print("2. Then configure Windows proxy:")
    print("   - Press Win + I")
    print("   - Network & Internet → Proxy")
    print("   - Turn ON 'Use a proxy server'")
    print("   - Address: 127.0.0.1, Port: 8080")
    print()
    print("3. Install certificate:")
    print("   - Visit: http://mitm.it")
    print("   - Download and install certificate")
    print()
    print("4. Test:")
    print("   - Visit: https://google.com")
    print("   - Visit: https://chatgpt.com")
    print()
    print("Press Ctrl+C to stop")
    print("="*70)
    print()
    
    # Start mitmproxy
    script_path = Path(__file__).parent / "security" / "mitm_proxy.py"
    
    try:
        # Run mitmdump with the script
        subprocess.run([
            "mitmdump",
            "-s", str(script_path),
            "--set", "block_global=false",
            "--listen-port", "8080"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Proxy stopped")
        print("Remember to disable Windows proxy:")
        print("  Settings → Network & Internet → Proxy → Turn OFF")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
