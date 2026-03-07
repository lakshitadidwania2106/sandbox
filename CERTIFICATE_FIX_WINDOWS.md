# Certificate Installation Fix for Windows

## Problem
Sites don't load after installing mitmproxy certificate - showing "Your connection is not private" or "NET::ERR_CERT_AUTHORITY_INVALID"

## Solution

### Method 1: Install Certificate Properly (Recommended)

1. **Find the certificate file**:
   ```
   C:\Users\Pragati Sharma\.mitmproxy\mitmproxy-ca-cert.cer
   ```

2. **Install it correctly**:
   - Right-click on `mitmproxy-ca-cert.cer`
   - Click "Install Certificate"
   - Select "Current User" → Next
   - Select "Place all certificates in the following store"
   - Click "Browse"
   - Select **"Trusted Root Certification Authorities"** (IMPORTANT!)
   - Click "OK" → "Next" → "Finish"
   - Click "Yes" on the security warning

3. **Restart your browser completely**:
   - Close ALL browser windows
   - Open Task Manager (Ctrl+Shift+Esc)
   - End any Chrome/Edge/Firefox processes
   - Reopen browser

4. **Test**: Go to https://google.com
   - Should load without certificate warning

### Method 2: Use Firefox (Easiest)

Firefox uses its own certificate store, which is often easier:

1. **Open Firefox**

2. **Configure proxy**:
   - Settings → Network Settings → Settings
   - Select "Manual proxy configuration"
   - HTTP Proxy: `127.0.0.1`, Port: `8080`
   - Check "Also use this proxy for HTTPS"
   - Click "OK"

3. **Visit any HTTPS site** (like https://google.com)
   - You'll see a certificate warning
   - Click "Advanced" → "Accept the Risk and Continue"
   - Firefox will remember this

4. **Or import certificate properly**:
   - Settings → Privacy & Security → Certificates → View Certificates
   - Click "Authorities" tab → "Import"
   - Browse to: `C:\Users\Pragati Sharma\.mitmproxy\mitmproxy-ca-cert.pem`
   - Check "Trust this CA to identify websites"
   - Click "OK"

### Method 3: Command Line Installation (Advanced)

Run PowerShell as Administrator:

```powershell
# Import certificate to Trusted Root
$cert = "C:\Users\Pragati Sharma\.mitmproxy\mitmproxy-ca-cert.cer"
Import-Certificate -FilePath $cert -CertStoreLocation Cert:\CurrentUser\Root
```

Then restart browser.

### Method 4: Disable Certificate Verification (Testing Only)

**Chrome/Edge** - Launch with flag:
```bash
# Close all Chrome windows first
"C:\Program Files\Google\Chrome\Application\chrome.exe" --ignore-certificate-errors --ignore-urlfetcher-cert-requests
```

**⚠️ WARNING**: Only use this for testing! Don't browse other sites with this flag.

## Verification Steps

### Step 1: Check if proxy is running

In the terminal where you ran `python security/start_proxy.py`, you should see:
```
Proxy server listening at http://0.0.0.0:8080
```

### Step 2: Test proxy without HTTPS

1. Open browser
2. Go to: http://mitm.it (HTTP, not HTTPS)
3. Should load the mitmproxy page
4. If this doesn't work, proxy isn't configured correctly

### Step 3: Test with HTTPS

1. Go to: https://google.com
2. If you see certificate warning:
   - Certificate not installed correctly
   - Try Method 1 or 2 above
3. If page loads normally:
   - Certificate is working! ✅

### Step 4: Check proxy logs

In the proxy terminal, you should see:
```
127.0.0.1:xxxxx: GET https://google.com/
```

If you don't see any logs, proxy isn't being used.

## Common Issues

### Issue 1: "Certificate not trusted" error

**Cause**: Certificate not in Trusted Root store

**Fix**: 
- Use Method 1 above
- Make sure you select "Trusted Root Certification Authorities"
- NOT "Personal" or "Intermediate"

### Issue 2: Chrome/Edge still shows warning

**Cause**: Browser cache or certificate not trusted

**Fix**:
1. Clear browser cache: Settings → Privacy → Clear browsing data
2. Restart browser completely (close all windows)
3. Check certificate is in Trusted Root:
   - Run: `certmgr.msc`
   - Go to: Trusted Root Certification Authorities → Certificates
   - Look for "mitmproxy"
   - If not there, reinstall using Method 1

### Issue 3: Firefox shows warning

**Cause**: Firefox uses its own certificate store

**Fix**: Use Method 2 (Firefox-specific instructions)

### Issue 4: Sites don't load at all

**Cause**: Proxy not configured or not running

**Fix**:
1. Check proxy is running: Terminal should show "Proxy server listening"
2. Check proxy settings: Should be `127.0.0.1:8080`
3. Test http://mitm.it (without HTTPS)
4. Check Windows firewall isn't blocking port 8080

### Issue 5: Some sites work, others don't

**Cause**: Certificate pinning or proxy bypass

**Fix**:
- Some sites (like banks) use certificate pinning and won't work with MITM
- This is normal and expected
- For testing, use ChatGPT, Google, Twitter, etc.

## Quick Test Procedure

After fixing certificate:

1. **Start proxy**:
   ```bash
   python security/start_proxy.py
   ```

2. **Test HTTP** (should work without certificate):
   ```
   http://mitm.it
   ```

3. **Test HTTPS** (needs certificate):
   ```
   https://google.com
   ```

4. **Test ChatGPT**:
   ```
   https://chatgpt.com
   ```

5. **Check proxy logs** - should see requests

## Alternative: Skip Certificate for Testing

If you just want to test the detection logic without dealing with certificates:

### Option A: Test with HTTP sites only

Some sites still support HTTP (though rare). The proxy will work without certificate for HTTP.

### Option B: Use the CLI tool instead

```bash
# Test detection without proxy
python check_code.py --file proprietary_code/secret_algorithm.py

# Should show: BLOCKED
```

### Option C: Use Bifrost plugin instead

The Bifrost plugin doesn't require certificate installation:

```bash
./setup_bifrost_plugin.sh
# Configure tools to use Bifrost
export ANTHROPIC_BASE_URL="http://localhost:8000"
```

See `TERMINAL_AGENTS_SETUP.md` for details.

## Still Not Working?

### Debug Checklist

- [ ] Proxy is running (terminal shows "Proxy server listening")
- [ ] Proxy configured in browser (`127.0.0.1:8080`)
- [ ] Certificate file exists: `C:\Users\Pragati Sharma\.mitmproxy\mitmproxy-ca-cert.cer`
- [ ] Certificate installed in "Trusted Root Certification Authorities"
- [ ] Browser restarted completely
- [ ] http://mitm.it loads (HTTP test)
- [ ] Proxy terminal shows traffic logs

### Get Help

If still not working, check:

1. **Proxy logs**: What errors do you see?
2. **Browser console**: Press F12, check Console tab for errors
3. **Certificate manager**: Run `certmgr.msc`, verify mitmproxy is in Trusted Root
4. **Firewall**: Check Windows Firewall isn't blocking port 8080

### Last Resort: Use Firefox

Firefox is usually the easiest because:
- Uses its own certificate store
- Can accept certificate warnings per-site
- Less strict than Chrome/Edge

Follow Method 2 above for Firefox-specific instructions.

## Success Criteria

You'll know it's working when:

✅ http://mitm.it loads  
✅ https://google.com loads without warning  
✅ Proxy terminal shows request logs  
✅ Can browse HTTPS sites normally  

Then you're ready to test with ChatGPT!
