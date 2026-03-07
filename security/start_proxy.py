"""
Start Bifrost MITM Proxy
=========================

This script starts the MITM proxy and configures system proxy settings.
Based on SigmaShield's start.py
"""

import subprocess
import time
import atexit
import signal
import sys
import platform
from pathlib import Path

mitm_process = None


def set_windows_proxy(enable=True, proxy_server="127.0.0.1:8080"):
    """Set Windows system proxy."""
    import winreg
    
    internet_settings = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
        0, winreg.KEY_WRITE
    )
    
    if enable:
        winreg.SetValueEx(internet_settings, 'ProxyEnable', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(internet_settings, 'ProxyServer', 0, winreg.REG_SZ, proxy_server)
        print(f"✅ Windows proxy enabled: {proxy_server}")
    else:
        winreg.SetValueEx(internet_settings, 'ProxyEnable', 0, winreg.REG_DWORD, 0)
        print("✅ Windows proxy disabled")
    
    winreg.CloseKey(internet_settings)


def set_mac_proxy(service="Wi-Fi", enable=True, host="127.0.0.1", port=8080):
    """Set macOS system proxy."""
    if enable:
        subprocess.run(["networksetup", "-setwebproxy", service, host, str(port)])
        subprocess.run(["networksetup", "-setsecurewebproxy", service, host, str(port)])
        print(f"✅ macOS proxy enabled: {host}:{port}")
    else:
        subprocess.run(["networksetup", "-setwebproxystate", service, "off"])
        subprocess.run(["networksetup", "-setsecurewebproxystate", service, "off"])
        print("✅ macOS proxy disabled")


def set_linux_proxy(enable=True, host="127.0.0.1", port=8080):
    """Set Linux system proxy (GNOME)."""
    if enable:
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "host", host])
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "port", str(port)])
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "host", host])
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "port", str(port)])
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "manual"])
        print(f"✅ Linux proxy enabled: {host}:{port}")
    else:
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "none"])
        print("✅ Linux proxy disabled")


def set_system_proxy(enable=True):
    """Set system proxy based on OS."""
    system = platform.system()
    
    try:
        if system == "Windows":
            set_windows_proxy(enable)
        elif system == "Darwin":  # macOS
            # Try to detect network service
            service = "Wi-Fi"  # Default, user may need to change
            set_mac_proxy(service, enable)
        elif system == "Linux":
            set_linux_proxy(enable)
        else:
            print(f"⚠️  Unsupported OS: {system}")
            print("   Please configure proxy manually:")
            print("   HTTP Proxy: 127.0.0.1:8080")
            print("   HTTPS Proxy: 127.0.0.1:8080")
    except Exception as e:
        print(f"⚠️  Could not set system proxy: {e}")
        print("   Please configure proxy manually:")
        print("   HTTP Proxy: 127.0.0.1:8080")
        print("   HTTPS Proxy: 127.0.0.1:8080")


def start_mitm_proxy():
    """Start mitmproxy."""
    script_path = Path(__file__).parent / "mitm_proxy.py"
    
    try:
        process = subprocess.Popen(
            ["mitmdump", "-s", str(script_path), "--set", "block_global=false"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("✅ mitmproxy started successfully")
        return process
    
    except FileNotFoundError:
        print("❌ mitmdump not found!")
        print("   Install with: pip install mitmproxy")
        return None
    
    except Exception as e:
        print(f"❌ Failed to start mitmproxy: {e}")
        return None


def cleanup():
    """Cleanup on exit."""
    print("\n👋 Shutting down...")
    
    # Stop mitmproxy
    global mitm_process
    if mitm_process:
        mitm_process.terminate()
        print("🛑 mitmproxy stopped")
    
    # Disable system proxy
    set_system_proxy(enable=False)


def handle_signal(sig, frame):
    """Handle Ctrl+C and other signals."""
    sys.exit(0)


def main():
    """Main entry point."""
    print("="*70)
    print("BIFROST MITM PROXY - STARTUP")
    print("="*70)
    print()
    
    # Check if mitmproxy is installed
    try:
        result = subprocess.run(["mitmdump", "--version"], capture_output=True, text=True)
        print(f"✅ mitmproxy found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ mitmproxy not installed!")
        print("   Install with: pip install mitmproxy")
        return 1
    
    print()
    
    # Set system proxy
    print("🔧 Configuring system proxy...")
    set_system_proxy(enable=True)
    time.sleep(1)
    print()
    
    # Start mitmproxy
    print("🚀 Starting mitmproxy...")
    global mitm_process
    mitm_process = start_mitm_proxy()
    
    if not mitm_process:
        cleanup()
        return 1
    
    print()
    print("="*70)
    print("✅ PROXY RUNNING")
    print("="*70)
    print()
    print("The proxy is now monitoring your network traffic.")
    print()
    print("Monitored sites:")
    print("  • ChatGPT (chatgpt.com)")
    print("  • Twitter/X (x.com)")
    print("  • StackOverflow (stackoverflow.com)")
    print("  • LLM APIs (OpenAI, Anthropic, etc.)")
    print()
    print("⚠️  IMPORTANT:")
    print("  1. Install mitmproxy certificate for HTTPS:")
    print("     Visit: http://mitm.it")
    print("  2. Press Ctrl+C to stop the proxy")
    print()
    print("="*70)
    print()
    
    # Register cleanup
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
