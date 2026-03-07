"""
Install mitmproxy Certificate on Windows
"""

import subprocess
import sys
from pathlib import Path

def install_certificate():
    """Install mitmproxy certificate to Windows Trusted Root store"""
    
    cert_dir = Path.home() / ".mitmproxy"
    cert_file = cert_dir / "mitmproxy-ca-cert.cer"
    
    print("="*70)
    print("MITMPROXY CERTIFICATE INSTALLER")
    print("="*70)
    print()
    
    # Check if certificate exists
    if not cert_file.exists():
        print("❌ Certificate not found!")
        print(f"   Expected location: {cert_file}")
        print()
        print("To generate certificate:")
        print("1. Run: python start_mitm_fixed.py")
        print("2. Wait for proxy to start")
        print("3. Press Ctrl+C to stop")
        print("4. Run this script again")
        return 1
    
    print(f"✅ Certificate found: {cert_file}")
    print()
    
    # Show manual installation instructions
    print("MANUAL INSTALLATION (Recommended):")
    print("="*70)
    print()
    print(f"1. Right-click on: {cert_file}")
    print("2. Click 'Install Certificate'")
    print("3. Select 'Current User' → Next")
    print("4. Select 'Place all certificates in the following store'")
    print("5. Click 'Browse'")
    print("6. Select 'Trusted Root Certification Authorities'")
    print("7. Click OK → Next → Finish")
    print("8. Click 'Yes' on security warning")
    print("9. Restart your browser")
    print()
    print("="*70)
    print()
    
    # Try automatic installation (requires admin)
    response = input("Try automatic installation? (requires admin) (y/n): ")
    
    if response.lower() == 'y':
        print("\nAttempting automatic installation...")
        print("(You may see a UAC prompt - click Yes)")
        print()
        
        try:
            # Use certutil to install
            result = subprocess.run([
                "certutil",
                "-addstore",
                "-user",
                "Root",
                str(cert_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Certificate installed successfully!")
                print()
                print("Next steps:")
                print("1. Restart your browser")
                print("2. Start proxy: python start_mitm_fixed.py")
                print("3. Configure browser proxy: 127.0.0.1:8080")
                print("4. Test: https://google.com")
                return 0
            else:
                print("❌ Automatic installation failed")
                print(f"   Error: {result.stderr}")
                print()
                print("Please use manual installation (see above)")
                return 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            print("Please use manual installation (see above)")
            return 1
    else:
        print("\nPlease follow the manual installation steps above.")
        return 0


if __name__ == "__main__":
    sys.exit(install_certificate())
