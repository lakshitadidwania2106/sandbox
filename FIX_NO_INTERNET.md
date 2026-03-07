# Fix "No Internet" Error - Quick Solution

## Problem
After configuring proxy, sites show "No internet" or "Unable to connect"

## Cause
The proxy is configured in Windows, but the proxy server isn't running.

---

## Quick Fix (2 steps)

### Step 1: Make Sure Proxy is Running

Open a terminal and run:
```bash
python security/start_proxy.py
```

You MUST see this message:
```
Proxy server listening at http://0.0.0.0:8080
```

**IMPORTANT**: Keep this terminal window open! Don't close it.

If you see errors, the proxy isn't starting. See troubleshooting below.

---

### Step 2: Test in Browser

1. Open Chrome
2. Go to: `http://mitm.it`
3. Should load the mitmproxy certificate page

If it loads → Proxy is working! ✅  
If it doesn't load → See troubleshooting below ❌

---

## Troubleshooting

### Issue: Proxy won't start

**Error**: "Address already in use" or "Port 8080 is already in use"

**Solution**:
```bash
# Find what's using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F

# Try starting proxy again
python security/start_proxy.py
```

**Error**: "mitmproxy not found" or "No module named mitmproxy"

**Solution**:
```bash
pip install mitmproxy
python security/start_proxy.py
```

**Error**: Other errors

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Try again
python security/start_proxy.py
```

---

### Issue: Proxy is running but sites still show "No internet"

**Cause**: Proxy is running but not responding

**Solution 1**: Check if proxy is actually listening

```bash
# Run diagnostic
python test_proxy_setup.py
```

Should show:
```
✅ PASS: Proxy Port
```

If it shows:
```
❌ FAIL: Proxy Port
```

Then proxy isn't running correctly.

**Solution 2**: Try a different port

Edit `security/start_proxy.py` and change port from 8080 to 8888:

```python
# Line where it says port=8080, change to:
port=8888
```

Then update Windows proxy settings to use port `8888` instead of `8080`.

---

### Issue: Proxy terminal shows errors

**Error**: "Permission denied"

**Solution**: Run terminal as Administrator
- Right-click Command Prompt or PowerShell
- Select "Run as Administrator"
- Run: `python security/start_proxy.py`

**Error**: "Cannot bind to port"

**Solution**: Port is already in use
```bash
# Find and kill the process using port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

---

## Quick Recovery

If nothing works, disable the proxy:

### Disable Windows Proxy

**Method 1: Settings**
1. Press `Win + I`
2. Network & Internet → Proxy
3. Turn OFF "Use a proxy server"
4. Click Save

**Method 2: Control Panel**
1. Press `Win + R`
2. Type: `inetcpl.cpl`
3. Connections → LAN settings
4. Uncheck "Use a proxy server"
5. OK → OK

Now your internet should work normally again.

---

## Correct Startup Sequence

Follow this exact order:

1. **Start proxy FIRST**:
   ```bash
   python security/start_proxy.py
   ```
   Wait for: "Proxy server listening at http://0.0.0.0:8080"

2. **Then configure Windows proxy**:
   - Settings → Network & Internet → Proxy
   - Turn ON "Use a proxy server"
   - `127.0.0.1:8080`

3. **Then open browser**:
   - Open Chrome
   - Go to http://mitm.it
   - Should load

4. **Install certificate** (if needed)

5. **Test with HTTPS**:
   - Go to https://google.com

---

## Verification Checklist

Before browsing, verify:

- [ ] Proxy terminal is open and shows "Proxy server listening"
- [ ] Windows proxy is configured: `127.0.0.1:8080`
- [ ] http://mitm.it loads in browser
- [ ] Proxy terminal shows request logs when you visit sites

If all checked → Proxy is working correctly ✅

---

## Common Mistakes

### ❌ Mistake 1: Configuring proxy before starting it
**Fix**: Start proxy FIRST, then configure Windows proxy

### ❌ Mistake 2: Closing the proxy terminal
**Fix**: Keep the terminal open while testing

### ❌ Mistake 3: Wrong port number
**Fix**: Use `8080` in both proxy startup and Windows settings

### ❌ Mistake 4: Using "localhost" instead of "127.0.0.1"
**Fix**: Use `127.0.0.1` (the IP address)

---

## Alternative: Use Firefox (Easier!)

If Chrome keeps having issues, Firefox is much easier:

1. **Start proxy**:
   ```bash
   python security/start_proxy.py
   ```

2. **Open Firefox**

3. **Configure Firefox proxy** (not Windows proxy):
   - Settings → Network Settings → Settings
   - Manual proxy: `127.0.0.1:8080`
   - Check "Also use this proxy for HTTPS"

4. **Test**: Go to http://mitm.it

5. **For HTTPS**: When you see certificate warning, click "Advanced" → "Accept Risk"

Firefox is more forgiving and easier to debug.

---

## Test Without Browser

To verify detection works without dealing with proxy/certificate:

```bash
# Test detection directly
python check_code.py --file proprietary_code/secret_algorithm.py

# Should show: BLOCKED
```

This tests the core detection without needing proxy or certificate.

---

## What You Should See

### In Proxy Terminal (when working):
```
Proxy server listening at http://0.0.0.0:8080
127.0.0.1:xxxxx: GET http://mitm.it/
127.0.0.1:xxxxx: GET https://google.com/
```

### In Browser (when working):
- http://mitm.it → Loads certificate page
- https://google.com → Loads normally (after certificate installed)
- No "No internet" errors

---

## Still Not Working?

### Option 1: Run Diagnostic
```bash
python test_proxy_setup.py
```

This will tell you exactly what's wrong.

### Option 2: Check Proxy Logs
Look at the terminal where proxy is running. Any errors?

### Option 3: Try Different Port
Change from 8080 to 8888 in both proxy and Windows settings.

### Option 4: Use Bifrost Plugin Instead
Skip the MITM proxy entirely:
- See `TERMINAL_AGENTS_SETUP.md`
- No certificate or proxy configuration needed
- Works better for production

---

## Summary

**The issue**: Windows proxy is configured, but proxy server isn't running.

**The fix**: 
1. Start proxy: `python security/start_proxy.py`
2. Keep terminal open
3. Test: http://mitm.it should load

**If still broken**: Disable Windows proxy (Settings → Network & Internet → Proxy → Turn OFF)
