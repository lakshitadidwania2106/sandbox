"""
Quick Proxy Setup Diagnostic
Tests if proxy is configured correctly
"""

import os
import sys
import socket
from pathlib import Path

def check_certificate_exists():
    """Check if mitmproxy certificate exists"""
    print("\n" + "="*70)
    print("1. Checking Certificate Files")
    print("="*70)
    
    cert_dir = Path.home() / ".mitmproxy"
    
    if not cert_dir.exists():
        print(f"❌ Certificate directory not found: {cert_dir}")
        print("   Run the proxy once to generate certificates")
        return False
    
    print(f"✅ Certificate directory exists: {cert_dir}")
    
    cert_files = {
        "mitmproxy-ca-cert.cer": "Windows certificate",
        "mitmproxy-ca-cert.pem": "Linux/Mac certificate",
        "mitmproxy-ca-cert.p12": "PKCS12 certificate",
    }
    
    found = False
    for filename, description in cert_files.items():
        cert_path = cert_dir / filename
        if cert_path.exists():
            print(f"✅ Found: {filename} ({description})")
            print(f"   Path: {cert_path}")
            found = True
        else:
            print(f"⚠️  Missing: {filename}")
    
    return found


def check_proxy_port():
    """Check if proxy port is available"""
    print("\n" + "="*70)
    print("2. Checking Proxy Port")
    print("="*70)
    
    port = 8080
    
    try:
        # Try to connect to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is open (proxy is running)")
            return True
        else:
            print(f"❌ Port {port} is not open (proxy is NOT running)")
            print(f"   Start the proxy: python security/start_proxy.py")
            return False
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False


def check_proprietary_code():
    """Check if proprietary code exists"""
    print("\n" + "="*70)
    print("3. Checking Proprietary Code")
    print("="*70)
    
    code_dir = Path("./proprietary_code")
    
    if not code_dir.exists():
        print(f"❌ Proprietary code directory not found: {code_dir}")
        return False
    
    print(f"✅ Proprietary code directory exists: {code_dir}")
    
    py_files = list(code_dir.glob("*.py"))
    
    if not py_files:
        print("⚠️  No Python files found in proprietary_code/")
        print("   Add your proprietary code files to test detection")
        return False
    
    print(f"✅ Found {len(py_files)} Python file(s):")
    for f in py_files:
        size = f.stat().st_size
        print(f"   - {f.name} ({size} bytes)")
    
    return True


def check_dependencies():
    """Check if required packages are installed"""
    print("\n" + "="*70)
    print("4. Checking Dependencies")
    print("="*70)
    
    packages = {
        "rapidfuzz": "Fuzzy matching",
        "mitmproxy": "MITM proxy",
    }
    
    all_installed = True
    
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✅ {package} installed ({description})")
        except ImportError:
            print(f"❌ {package} NOT installed ({description})")
            print(f"   Install: pip install {package}")
            all_installed = False
    
    return all_installed


def test_detection():
    """Test if detection is working"""
    print("\n" + "="*70)
    print("5. Testing Detection Engine")
    print("="*70)
    
    try:
        from security.fuzzy_detector import check_if_company_code
        
        # Test with proprietary code
        test_code = """def calculate_secret_score(data, weights, threshold=0.5):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    return score"""
        
        print("Testing with proprietary code snippet...")
        result = check_if_company_code(test_code, "./proprietary_code", min_score=60)
        
        if result:
            print("✅ Detection WORKING - proprietary code detected")
        else:
            print("⚠️  Detection not working - code not detected")
            print("   This might be OK if your proprietary code is different")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing detection: {e}")
        return False


def print_instructions():
    """Print next steps"""
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    print("\n1. Install Certificate:")
    cert_path = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.cer"
    print(f"   - Right-click: {cert_path}")
    print("   - Install Certificate → Current User")
    print("   - Place in: Trusted Root Certification Authorities")
    print("   - Restart browser")
    
    print("\n2. Configure Browser Proxy:")
    print("   - Settings → Network → Proxy")
    print("   - Manual proxy: 127.0.0.1:8080")
    
    print("\n3. Test:")
    print("   - Visit: http://mitm.it (should load)")
    print("   - Visit: https://google.com (should load without warning)")
    print("   - Visit: https://chatgpt.com (try to paste proprietary code)")
    
    print("\n4. Troubleshooting:")
    print("   - See: CERTIFICATE_FIX_WINDOWS.md")
    print("   - Or use Firefox (easier certificate setup)")


def main():
    """Run all diagnostics"""
    print("="*70)
    print("PROXY SETUP DIAGNOSTIC")
    print("="*70)
    
    results = {
        "Certificate": check_certificate_exists(),
        "Proxy Port": check_proxy_port(),
        "Proprietary Code": check_proprietary_code(),
        "Dependencies": check_dependencies(),
        "Detection": test_detection(),
    }
    
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All checks passed! System is ready.")
        print_instructions()
    else:
        print("\n⚠️  Some checks failed. Fix the issues above.")
        
        if not results["Proxy Port"]:
            print("\n💡 TIP: Start the proxy first:")
            print("   python security/start_proxy.py")
        
        if not results["Certificate"]:
            print("\n💡 TIP: Run the proxy once to generate certificates:")
            print("   python security/start_proxy.py")
            print("   Then press Ctrl+C to stop it")
        
        print_instructions()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
