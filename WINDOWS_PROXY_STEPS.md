# Windows Proxy Configuration - Visual Guide

## For Chrome/Edge Users on Windows

Chrome and Edge use **Windows system proxy settings**, not browser-specific settings.

---

## Step-by-Step with Screenshots

### Step 1: Open Windows Settings

**Option A: Quick way**
- Press `Win + I` on your keyboard

**Option B: Start menu**
- Click Start menu
- Click Settings (gear icon)

---

### Step 2: Go to Network & Internet

**Windows 11:**
- Click "Network & Internet" in the left sidebar

**Windows 10:**
- Click "Network & Internet"

---

### Step 3: Click Proxy

**Windows 11:**
- In the left sidebar, scroll down and click "Proxy"

**Windows 10:**
- In the left sidebar, click "Proxy"

---

### Step 4: Configure Manual Proxy

**Windows 11:**
1. Scroll down to "Manual proxy setup"
2. Click the "Set up" button
3. Turn ON the toggle for "Use a proxy server"
4. Fill in:
   - **Proxy IP address**: `127.0.0.1`
   - **Port**: `8080`
5. Click "Save"

**Windows 10:**
1. Scroll down to "Manual proxy setup"
2. Turn ON the toggle for "Use a proxy server"
3. Fill in:
   - **Address**: `127.0.0.1`
   - **Port**: `8080`
4. Click "Save"

---

### What You Should See

After configuration, you should see:
```
Manual proxy setup
Use a proxy server: ON
Proxy IP address: 127.0.0.1
Port: 8080
```

---

## Alternative: Using Control Panel

If you can't find the settings above:

1. Press `Win + R`
2. Type: `inetcpl.cpl`
3. Press Enter
4. Click "Connections" tab
5. Click "LAN settings" button
6. Check "Use a proxy server for your LAN"
7. Enter:
   - Address: `127.0.0.1`
   - Port: `8080`
8. Click OK → OK

---

## Verify Proxy is Configured

### Method 1: Check Settings
1. Go back to Settings → Network & Internet → Proxy
2. Should show: "Use a proxy server: ON"
3. Should show: `127.0.0.1:8080`

### Method 2: Test in Browser
1. Open Chrome
2. Go to: `http://mitm.it`
3. If it loads → Proxy is working ✅
4. If it doesn't load → Proxy not configured correctly ❌

### Method 3: Check Proxy Terminal
1. Look at the terminal where you ran `python security/start_proxy.py`
2. Visit any website in Chrome
3. You should see logs like:
   ```
   127.0.0.1:xxxxx: GET https://google.com/
   ```
4. If you see logs → Proxy is working ✅
5. If no logs → Proxy not configured correctly ❌

---

## Common Mistakes

### ❌ Wrong: Looking for proxy in Chrome settings
Chrome doesn't have its own proxy settings on Windows. It uses Windows system proxy.

### ❌ Wrong: Using 127.0.0.1 without port
You need both: `127.0.0.1` AND port `8080`

### ❌ Wrong: Using localhost instead of 127.0.0.1
Use `127.0.0.1` (the IP address), not "localhost"

### ✅ Correct: Windows Settings → Network & Internet → Proxy
This is where Chrome gets its proxy settings from.

---

## Disable Proxy When Done

**To turn off the proxy:**

1. Press `Win + I`
2. Go to Network & Internet → Proxy
3. Turn OFF "Use a proxy server"
4. Click Save

**Or quick way:**
1. Press `Win + R`
2. Type: `inetcpl.cpl`
3. Connections → LAN settings
4. Uncheck "Use a proxy server"
5. OK → OK

---

## For Other Browsers

### Firefox
Firefox has its own proxy settings:
- Settings → Network Settings → Settings
- Manual proxy: `127.0.0.1:8080`

### Edge
Edge uses Windows system proxy (same as Chrome)

### Brave
Brave uses Windows system proxy (same as Chrome)

---

## Quick Reference

| Browser | Proxy Location |
|---------|---------------|
| Chrome | Windows Settings → Network & Internet → Proxy |
| Edge | Windows Settings → Network & Internet → Proxy |
| Brave | Windows Settings → Network & Internet → Proxy |
| Firefox | Firefox Settings → Network Settings |

---

## Troubleshooting

### Issue: Can't find "Proxy" in settings

**Solution**: Use Control Panel method:
1. Press `Win + R`
2. Type: `inetcpl.cpl`
3. Follow steps above

### Issue: Proxy settings keep resetting

**Solution**: 
- Some VPN software resets proxy settings
- Disable VPN while testing
- Or use Firefox (has its own proxy settings)

### Issue: "Use a proxy server" toggle is grayed out

**Solution**:
- You might be on a corporate network with managed settings
- Try Control Panel method instead
- Or use Firefox

---

## Complete Testing Checklist

- [ ] Proxy started: `python security/start_proxy.py`
- [ ] Windows proxy configured: `127.0.0.1:8080`
- [ ] Certificate installed in Trusted Root
- [ ] Chrome restarted completely
- [ ] http://mitm.it loads
- [ ] https://google.com loads without warning
- [ ] Proxy terminal shows request logs
- [ ] Ready to test ChatGPT!

---

## Next Steps

Once proxy is configured:
1. Install certificate (see `FIX_CERTIFICATE_NOW.md`)
2. Test with ChatGPT (see `QUICK_TEST_CHATGPT.md`)
3. Disable proxy when done

---

## Need Help?

- **Detailed guide**: `CHROME_SETUP_WINDOWS.md`
- **Certificate issues**: `CERTIFICATE_FIX_WINDOWS.md`
- **Run diagnostic**: `python test_proxy_setup.py`
