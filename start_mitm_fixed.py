"""
Fixed MITM Proxy Starter with Certificate Setup
"""

import subprocess
import sys
import os
from pathlib import Path
import time

def check_certificate():
    """Check if mitmproxy certificate exists and show instructions"""
    cert_dir = Path.home() / ".mitmproxy"
    cert_file = cert_dir / "mitmproxy-ca-cert.cer"
    
    print("\n" + "="*70)
    print("CERTIFICATE SETUP")
    print("="*70)
    
    if cert_file.exists():
        print(f"✅ Certificate found: {cert_file}")
        print("\nTo install certificate:")
        print(f"1. Right-click: {cert_file}")
        print("2. Install Certificate → Current User")
        print("3. Place in: Trusted Root Certification Authorities")
        print("4. Restart browser")
    else:
        print("⚠️  Certificate will be generated on first run")
        print(f"   Location: {cert_file}")
        print("\nAfter starting proxy:")
        print("1. Visit: http://mitm.it")
        print("2. Download certificate for your OS")
        print("3. Install it")
    
    print("="*70)
    print()

def check_port():
    """Check if port 8080 is available"""
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True,
        text=True
    )
    
    if ":8080" in result.stdout:
        print("⚠️  Port 8080 is already in use!")
        print("\nFinding process...")
        
        lines = result.stdout.split('\n')
        for line in lines:
            if ":8080" in line and "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                print(f"   Process ID: {pid}")
                
                response = input("\nKill this process? (y/n): ")
                if response.lower() == 'y':
                    subprocess.run(["taskkill", "/PID", pid, "/F"])
                    print("✅ Process killed")
                    time.sleep(1)
                    return True
                else:
                    print("\n💡 Use a different port:")
                    print("   mitmdump -s security/mitm_proxy.py --listen-port 8082")
                    return False
    
    return True

def main():
    """Start mitmproxy with proper setup"""
    print("="*70)
    print("MITM PROXY - FIXED STARTUP")
    print("="*70)
    print()
    
    # Check mitmproxy
    try:
        result = subprocess.run(["mitmdump", "--version"], capture_output=True, text=True)
        print(f"✅ mitmproxy found")
    except FileNotFoundError:
        print("❌ mitmproxy not installed!")
        print("   Install: pip install mitmproxy")
        return 1
    
    # Check proprietary code
    code_dir = Path("./proprietary_code")
    if code_dir.exists():
        py_files = list(code_dir.glob("*.py"))
        print(f"✅ Proprietary code: {len(py_files)} files")
    else:
        print(f"⚠️  No proprietary code directory")
    
    print()
    
    # Check port
    if not check_port():
        return 1
    
    # Show certificate info
    check_certificate()
    
    # Start proxy
    print("🚀 Starting mitmproxy on port 8080...")
    print()
    print("="*70)
    print("PROXY STARTING")
    print("="*70)
    print()
    print("After you see 'Proxy server listening':")
    print()
    print("FOR FIREFOX (EASIEST):")
    print("1. Open Firefox")
    print("2. Settings → Network Settings → Manual proxy")
    print("3. HTTP Proxy: 127.0.0.1, Port: 8080")
    print("4. Check 'Also use this proxy for HTTPS'")
    print("5. Visit: https://google.com")
    print("6. Click 'Advanced' → 'Accept the Risk'")
    print("7. Test: https://chatgpt.com")
    print()
    print("FOR CHROME:")
    print("1. Windows Settings → Network & Internet → Proxy")
    print("2. Turn ON 'Use a proxy server'")
    print("3. Address: 127.0.0.1, Port: 8080")
    print("4. Install certificate (see above)")
    print()
    print("Press Ctrl+C to stop")
    print("="*70)
    print()
    
    script_path = Path(__file__).parent / "security" / "mitm_proxy.py"
    
    try:
        # Run mitmdump
        subprocess.run([
            "mitmdump",
            "-s", str(script_path),
            "--set", "block_global=false",
            "--listen-port", "8080",
            "--set", "confdir=~/.mitmproxy"  # Explicit cert directory
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Proxy stopped")
        print("\nRemember to:")
        print("- Disable browser proxy settings")
        print("- Or turn OFF Windows proxy")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
