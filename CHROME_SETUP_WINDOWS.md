# Chrome Setup for Windows - Complete Guide

Chrome uses **Windows system proxy settings**, not its own proxy settings.

## Step-by-Step Setup for Chrome

### Step 1: Start the Proxy

Open a terminal and run:
```bash
python security/start_proxy.py
```

Keep this terminal open! You should see:
```
Proxy server listening at http://0.0.0.0:8080
```

---

### Step 2: Configure Windows System Proxy

Chrome uses Windows system proxy, so configure it in Windows Settings:

**Method A: Windows 11**

1. Press `Win + I` to open Settings
2. Go to **Network & Internet**
3. Click **Proxy** (on the left sidebar)
4. Scroll down to **Manual proxy setup**
5. Click **Set up** button
6. Turn on **"Use a proxy server"**
7. Enter:
   - **Proxy IP address**: `127.0.0.1`
   - **Port**: `8080`
8. Click **Save**

**Method B: Windows 10**

1. Press `Win + I` to open Settings
2. Go to **Network & Internet**
3. Click **Proxy** (on the left sidebar)
4. Scroll down to **Manual proxy setup**
5. Turn on **"Use a proxy server"**
6. Enter:
   - **Address**: `127.0.0.1`
   - **Port**: `8080`
7. Click **Save**

**Method C: Control Panel (All Windows versions)**

1. Press `Win + R`
2. Type: `inetcpl.cpl`
3. Press Enter
4. Go to **Connections** tab
5. Click **LAN settings**
6. Check **"Use a proxy server for your LAN"**
7. Enter:
   - **Address**: `127.0.0.1`
   - **Port**: `8080`
8. Click **OK** → **OK**

---

### Step 3: Install Certificate

1. **Open File Explorer**
2. **Navigate to**: `C:\Users\Pragati Sharma\.mitmproxy`
3. **Find**: `mitmproxy-ca-cert.cer`
4. **Right-click** → "Install Certificate"
5. **Select**:
   - Store Location: **"Current User"**
   - Click **Next**
6. **Select**: **"Place all certificates in the following store"**
7. Click **Browse**
8. **Select**: **"Trusted Root Certification Authorities"** ← IMPORTANT!
9. Click **OK** → **Next** → **Finish**
10. Click **Yes** on the security warning

---

### Step 4: Restart Chrome

1. **Close ALL Chrome windows**
2. **Open Task Manager**: `Ctrl + Shift + Esc`
3. **Find** "Google Chrome" processes
4. **Right-click** each one → "End Task"
5. **Wait** 5 seconds
6. **Reopen Chrome**

---

### Step 5: Test the Setup

**Test 1: HTTP (no certificate needed)**
1. Open Chrome
2. Go to: `http://mitm.it`
3. Should see the mitmproxy certificate page
4. If this doesn't work, proxy isn't configured correctly

**Test 2: HTTPS (needs certificate)**
1. Go to: `https://google.com`
2. Should load WITHOUT any certificate warning
3. If you see "Your connection is not private", certificate isn't installed correctly

**Test 3: Check proxy logs**
1. Look at the terminal where proxy is running
2. You should see:
   ```
   127.0.0.1:xxxxx: GET https://google.com/
   ```
3. If you don't see logs, proxy isn't being used

---

### Step 6: Test with ChatGPT

1. **Go to**: `https://chatgpt.com`

2. **Try to paste proprietary code**:
   ```python
   def calculate_secret_score(data, weights, threshold=0.5):
       score = 0
       for i, value in enumerate(data):
           score += value * weights[i]
       
       if score > threshold:
           return score * 1.5
       return score
   ```

3. **Try to send the message**

4. **Expected result**: 🚫 Request should be BLOCKED
   - You'll see an error or "403 Forbidden"
   - Check proxy terminal - should show:
     ```
     🚨 PROPRIETARY CODE DETECTED!
     🚫 Blocking request to https://chatgpt.com/
     ```

5. **Try generic code**:
   ```python
   def add(a, b):
       return a + b
   ```

6. **Expected result**: ✅ Should send normally

---

## Troubleshooting

### Issue: "Your connection is not private" warning

**Cause**: Certificate not installed in Trusted Root

**Fix**:
1. Press `Win + R`
2. Type: `certmgr.msc`
3. Press Enter
4. Navigate to: **Trusted Root Certification Authorities** → **Certificates**
5. Look for "mitmproxy" in the list
6. **If you see it**: Certificate is installed ✅
7. **If you don't see it**: Repeat Step 3 above (Install Certificate)

### Issue: http://mitm.it doesn't load

**Cause**: Proxy not configured or not running

**Fix**:
1. Check proxy is running (terminal shows "Proxy server listening")
2. Check Windows proxy settings:
   - Press `Win + I` → Network & Internet → Proxy
   - Should show: `127.0.0.1:8080`
3. Restart Chrome completely

### Issue: Proxy logs show nothing

**Cause**: Chrome not using the proxy

**Fix**:
1. Verify Windows proxy is enabled:
   - Settings → Network & Internet → Proxy
   - "Use a proxy server" should be ON
2. Restart Chrome
3. Try visiting any website
4. Check proxy terminal for logs

### Issue: Some sites work, others don't

**Cause**: Normal - some sites use certificate pinning

**Fix**:
- This is expected behavior
- Banks and some secure sites won't work with MITM proxy
- ChatGPT, Google, Twitter should work fine

---

## Alternative: Use Extension (Easier!)

If Windows proxy settings are confusing, use a Chrome extension:

### Using Proxy SwitchyOmega Extension

1. **Install Extension**:
   - Go to: https://chrome.google.com/webstore
   - Search: "Proxy SwitchyOmega"
   - Click "Add to Chrome"

2. **Configure**:
   - Click the extension icon
   - Click "Options"
   - Create new profile: "MITM Proxy"
   - Protocol: `HTTP`
   - Server: `127.0.0.1`
   - Port: `8080`
   - Click "Apply changes"

3. **Enable**:
   - Click extension icon
   - Select "MITM Proxy"

4. **Test**:
   - Go to http://mitm.it
   - Should load

5. **Disable when done**:
   - Click extension icon
   - Select "Direct" (no proxy)

---

## Quick Command Reference

**Start proxy**:
```bash
python security/start_proxy.py
```

**Check if proxy is running**:
```bash
python test_proxy_setup.py
```

**Test detection without proxy**:
```bash
python check_code.py --file proprietary_code/secret_algorithm.py
```

---

## When You're Done Testing

**Disable the proxy**:

1. Press `Win + I`
2. Go to **Network & Internet** → **Proxy**
3. Turn OFF **"Use a proxy server"**
4. Click **Save**

**Stop the proxy**:
- Press `Ctrl + C` in the terminal

**Restart Chrome**:
- Close all windows and reopen

---

## Summary

For Chrome on Windows:

1. ✅ Start proxy: `python security/start_proxy.py`
2. ✅ Configure Windows proxy: Settings → Network & Internet → Proxy → `127.0.0.1:8080`
3. ✅ Install certificate: Right-click `.cer` file → Install → Trusted Root
4. ✅ Restart Chrome completely
5. ✅ Test: http://mitm.it then https://google.com
6. ✅ Test ChatGPT with proprietary code

**Chrome uses Windows system proxy, not its own settings!**

---

## Still Having Issues?

Run the diagnostic:
```bash
python test_proxy_setup.py
```

This will tell you exactly what's wrong.

Or see: `CERTIFICATE_FIX_WINDOWS.md` for detailed troubleshooting.
