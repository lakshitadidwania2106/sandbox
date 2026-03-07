# Fix Certificate Issue - Quick Steps

## Your Issue
You installed the certificate from `C:\Users\Pragati Sharma\.mitmproxy` but sites still don't load.

## Quick Fix (5 minutes)

### Step 1: Install Certificate Correctly

The certificate needs to be in the **Trusted Root** store, not just installed.

1. **Open File Explorer**
2. **Navigate to**: `C:\Users\Pragati Sharma\.mitmproxy`
3. **Find**: `mitmproxy-ca-cert.cer`
4. **Right-click** → "Install Certificate"
5. **IMPORTANT**: Select these options:
   - Store Location: **"Current User"** → Next
   - Select: **"Place all certificates in the following store"**
   - Click **"Browse"**
   - Select: **"Trusted Root Certification Authorities"** ← THIS IS CRITICAL!
   - Click "OK" → "Next" → "Finish"
   - Click "Yes" on security warning

### Step 2: Verify Certificate is Installed

1. **Press** `Win + R`
2. **Type**: `certmgr.msc`
3. **Press** Enter
4. **Navigate to**: Trusted Root Certification Authorities → Certificates
5. **Look for**: "mitmproxy" in the list
6. **If you see it**: ✅ Certificate is installed correctly
7. **If you don't see it**: ❌ Repeat Step 1

### Step 3: Restart Browser Completely

1. **Close ALL browser windows**
2. **Open Task Manager**: `Ctrl + Shift + Esc`
3. **Find** Chrome/Edge/Firefox processes
4. **Right-click** → "End Task" on each one
5. **Wait** 5 seconds
6. **Reopen** browser

### Step 4: Test

1. **Go to**: http://mitm.it (HTTP, not HTTPS)
   - Should load the mitmproxy page
   - If not, proxy isn't running or configured

2. **Go to**: https://google.com (HTTPS)
   - Should load WITHOUT certificate warning
   - If you see warning, certificate isn't trusted

## Alternative: Use Firefox (Easier!)

Firefox is much easier because it has its own certificate store:

### Firefox Method

1. **Open Firefox**

2. **Configure Proxy**:
   - Menu → Settings → Network Settings → Settings
   - Select "Manual proxy configuration"
   - HTTP Proxy: `127.0.0.1`, Port: `8080`
   - ✅ Check "Also use this proxy for HTTPS"
   - Click "OK"

3. **Visit**: https://google.com
   - You'll see a warning: "Warning: Potential Security Risk Ahead"
   - Click "Advanced"
   - Click "Accept the Risk and Continue"
   - Firefox will remember this

4. **Done!** Now test with ChatGPT

## Troubleshooting

### Problem: "Your connection is not private" in Chrome/Edge

**Cause**: Certificate not in Trusted Root store

**Fix**: 
- Run `certmgr.msc`
- Check if "mitmproxy" is in "Trusted Root Certification Authorities"
- If not, repeat Step 1 above
- Make sure you select "Trusted Root" not "Personal"

### Problem: http://mitm.it doesn't load

**Cause**: Proxy not running or not configured

**Fix**:
1. Check proxy is running: Terminal should show "Proxy server listening"
2. Check proxy settings: Should be `127.0.0.1:8080`
3. Restart browser

### Problem: Certificate warning on every site

**Cause**: Certificate not trusted by system

**Fix**:
- Use Firefox method above (easier)
- Or reinstall certificate in Trusted Root (Step 1)

## Quick Diagnostic

Run this to check your setup:

```bash
python test_proxy_setup.py
```

This will tell you exactly what's wrong.

## Still Not Working?

### Option 1: Use Firefox
- Easiest solution
- Follow "Firefox Method" above
- Works 99% of the time

### Option 2: Skip HTTPS Testing
- Test with CLI tool instead:
  ```bash
  python check_code.py --file proprietary_code/secret_algorithm.py
  ```
- This tests detection without needing proxy/certificate

### Option 3: Use Bifrost Plugin
- No certificate needed
- See `TERMINAL_AGENTS_SETUP.md`
- Better for production anyway

## Expected Result

When working correctly:

✅ http://mitm.it loads  
✅ https://google.com loads without warning  
✅ Proxy terminal shows: `127.0.0.1:xxxxx: GET https://google.com/`  
✅ Can browse HTTPS sites normally  

Then you can test with ChatGPT!

## Need More Help?

See detailed guide: `CERTIFICATE_FIX_WINDOWS.md`
