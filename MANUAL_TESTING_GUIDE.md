# Manual Testing Guide - ChatGPT

This guide walks you through manually testing the proprietary code detection system with ChatGPT.

## 🎯 What You'll Test

You'll try to paste proprietary code into ChatGPT and verify it gets blocked by the MITM proxy.

## 📋 Prerequisites

- ✅ Python installed
- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ Proprietary code in `./proprietary_code/` directory
- ✅ Web browser (Chrome, Firefox, Edge, etc.)

## 🚀 Step-by-Step Testing Procedure

### Step 1: Start the MITM Proxy

Open a terminal and run:

```bash
python security/start_proxy.py
```

You should see:
```
======================================================================
BIFROST MITM PROXY - Starting...
======================================================================

✅ Proprietary code directory found: ./proprietary_code
   Found 1 Python files to protect

Starting mitmproxy on port 8080...
Press Ctrl+C to stop

Proxy server listening at http://0.0.0.0:8080
```

**Keep this terminal open!** The proxy needs to stay running.

---

### Step 2: Install mitmproxy Certificate

1. **Open your browser** (Chrome, Firefox, Edge, etc.)

2. **Go to**: http://mitm.it

3. **Click on your platform**:
   - Windows: Click "Windows"
   - macOS: Click "Apple"
   - Linux: Click "Linux"

4. **Install the certificate**:
   
   **For Windows:**
   - Double-click the downloaded certificate
   - Click "Install Certificate"
   - Select "Current User"
   - Select "Place all certificates in the following store"
   - Click "Browse" → Select "Trusted Root Certification Authorities"
   - Click "Next" → "Finish"
   - Click "Yes" on the security warning

   **For macOS:**
   - Double-click the downloaded certificate
   - Enter your password
   - Open "Keychain Access"
   - Find "mitmproxy" certificate
   - Double-click → Trust → "Always Trust"

   **For Firefox** (uses its own certificate store):
   - Go to Settings → Privacy & Security → Certificates → View Certificates
   - Click "Import"
   - Select the downloaded certificate
   - Check "Trust this CA to identify websites"
   - Click "OK"

---

### Step 3: Configure Browser Proxy

**Option A: System-Wide Proxy (Recommended)**

**Windows:**
1. Open Settings → Network & Internet → Proxy
2. Under "Manual proxy setup", click "Set up"
3. Turn on "Use a proxy server"
4. Address: `127.0.0.1`
5. Port: `8080`
6. Click "Save"

**macOS:**
1. System Preferences → Network
2. Select your network → Advanced → Proxies
3. Check "Web Proxy (HTTP)" and "Secure Web Proxy (HTTPS)"
4. Server: `127.0.0.1`
5. Port: `8080`
6. Click "OK" → "Apply"

**Linux:**
1. Settings → Network → Network Proxy
2. Select "Manual"
3. HTTP Proxy: `127.0.0.1:8080`
4. HTTPS Proxy: `127.0.0.1:8080`
5. Click "Apply"

**Option B: Browser Extension (Alternative)**

**Chrome/Edge:**
1. Install "Proxy SwitchyOmega" extension
2. Create new profile: "MITM Proxy"
3. Protocol: HTTP
4. Server: `127.0.0.1`
5. Port: `8080`
6. Click the extension icon → Select "MITM Proxy"

**Firefox:**
1. Settings → Network Settings → Settings
2. Select "Manual proxy configuration"
3. HTTP Proxy: `127.0.0.1`, Port: `8080`
4. Check "Also use this proxy for HTTPS"
5. Click "OK"

---

### Step 4: Verify Proxy is Working

1. **Check the proxy terminal** - you should see traffic being logged:
   ```
   127.0.0.1:xxxxx: GET https://www.google.com/
   127.0.0.1:xxxxx: GET https://chatgpt.com/
   ```

2. **Visit any HTTPS site** (like https://google.com)
   - If you see a certificate warning, the proxy isn't configured correctly
   - If the page loads normally, the proxy is working! ✅

---

### Step 5: Test with ChatGPT

#### Test 1: Try to Paste Proprietary Code (Should be BLOCKED)

1. **Open ChatGPT**: https://chatgpt.com

2. **Copy your proprietary code**:
   ```python
   def calculate_secret_score(data, weights, threshold=0.5):
       score = 0
       for i, value in enumerate(data):
           score += value * weights[i]
       
       if score > threshold:
           return score * 1.5
       return score
   ```

3. **Paste into ChatGPT** and try to send

4. **Expected Result**: 🚫 REQUEST BLOCKED
   - You should see: "Request blocked: Proprietary code detected"
   - Or the request fails with a 403 error
   - Check the proxy terminal - you should see:
     ```
     📝 Checking ChatGPT request...
     🚨 PROPRIETARY CODE DETECTED!
        Text length: 219 chars
     🚫 [PROPRIETARY_CODE_IN_CHATGPT] Blocking request to https://chatgpt.com/...
     ```

#### Test 2: Try Generic Code (Should be ALLOWED)

1. **Copy generic code**:
   ```python
   def add_numbers(a, b):
       return a + b
   
   def multiply(x, y):
       return x * y
   ```

2. **Paste into ChatGPT** and send

3. **Expected Result**: ✅ REQUEST ALLOWED
   - The message should send successfully
   - ChatGPT should respond normally
   - Check the proxy terminal - you should see:
     ```
     📝 Checking ChatGPT request...
     ✅ No proprietary code detected - request allowed
     ```

#### Test 3: Try Modified Proprietary Code (Should be BLOCKED)

1. **Copy modified code** (renamed variables):
   ```python
   def calculate_secret_score(data, weights, threshold=0.5):
       total = 0
       for idx, val in enumerate(data):
           total += val * weights[idx]
       
       if total > threshold:
           return total * 1.5
       return total
   ```

2. **Paste into ChatGPT** and try to send

3. **Expected Result**: 🚫 REQUEST BLOCKED
   - Even with renamed variables, it should be blocked
   - Fuzzy matching detects the similar structure
   - Check the proxy terminal for detection message

---

### Step 6: Test with Other Sites (Optional)

#### Twitter/X

1. Go to https://twitter.com (or https://x.com)
2. Try to post a tweet with proprietary code
3. Should be blocked with 403 error

#### StackOverflow

1. Go to https://stackoverflow.com
2. Try to create a question/answer with proprietary code
3. Should be blocked with 403 error

---

### Step 7: Stop the Proxy

When done testing:

1. **Stop the proxy**: Press `Ctrl+C` in the terminal

2. **Disable browser proxy**:
   - Windows: Settings → Network & Internet → Proxy → Turn off
   - macOS: System Preferences → Network → Advanced → Proxies → Uncheck all
   - Linux: Settings → Network → Network Proxy → Disable
   - Browser extension: Click extension → Select "Direct"

3. **Verify normal browsing**: Visit any website to confirm it works without proxy

---

## 🔍 Troubleshooting

### Issue: Certificate Warning in Browser

**Problem**: Browser shows "Your connection is not private" warning

**Solution**:
1. Make sure you installed the certificate from http://mitm.it
2. Restart your browser after installing the certificate
3. For Chrome: Go to chrome://restart
4. For Firefox: Make sure you imported the certificate in Firefox's own certificate manager

### Issue: Proxy Not Intercepting Requests

**Problem**: No traffic showing in proxy terminal

**Solution**:
1. Verify proxy settings: `127.0.0.1:8080`
2. Check if proxy is running (terminal should show "Proxy server listening")
3. Try visiting http://mitm.it - if it doesn't load, proxy isn't configured
4. Restart browser after configuring proxy

### Issue: ChatGPT Not Being Blocked

**Problem**: Proprietary code goes through without blocking

**Solution**:
1. Check proxy terminal - is it detecting the request?
2. Verify proprietary code exists in `./proprietary_code/`
3. Run test: `python test_detection_working.py`
4. Check if the code similarity is above threshold (60%)
5. Try lowering threshold in `security/fuzzy_detector.py` (line 13)

### Issue: All Requests Being Blocked

**Problem**: Even generic code is blocked

**Solution**:
1. Check threshold setting (should be 60, not lower)
2. Verify proprietary code files are correct
3. Run: `python check_code.py "def add(a,b): return a+b"`
4. Should show "ALLOWED" - if not, threshold is too low

### Issue: Proxy Slowing Down Browsing

**Problem**: Websites load very slowly

**Solution**:
1. This is normal for MITM proxies (adds 5-20ms per request)
2. For production, use Bifrost plugin instead (much faster)
3. Only use MITM proxy for testing
4. Disable proxy when not testing

---

## 📊 What to Look For

### In the Proxy Terminal

**When proprietary code is detected:**
```
📝 Checking ChatGPT request...
✅ Match found in file: proprietary_code\secret_algorithm.py
📌 Match (score: 84.375) starting at line 11:
    ...code snippet...
🚨 PROPRIETARY CODE DETECTED!
   Text length: 219 chars
🚫 [PROPRIETARY_CODE_IN_CHATGPT] Blocking request to https://chatgpt.com/...
```

**When generic code is allowed:**
```
📝 Checking ChatGPT request...
❌ No matching code snippet found in any file.
✅ Request allowed
```

### In the Browser

**When blocked:**
- Request fails
- May show "403 Forbidden" error
- Message doesn't send to ChatGPT
- Error message: "Request blocked: Proprietary code detected"

**When allowed:**
- Request succeeds
- Message sends normally
- ChatGPT responds as usual

---

## 🎯 Success Criteria

Your system is working correctly if:

✅ **Test 1**: Proprietary code is BLOCKED  
✅ **Test 2**: Generic code is ALLOWED  
✅ **Test 3**: Modified proprietary code is BLOCKED  
✅ **Proxy terminal**: Shows detection messages  
✅ **Browser**: Shows 403 error when blocked  

---

## 📝 Testing Checklist

- [ ] Proxy started successfully
- [ ] Certificate installed
- [ ] Browser proxy configured
- [ ] Visited http://mitm.it successfully
- [ ] Test 1: Proprietary code blocked ✅
- [ ] Test 2: Generic code allowed ✅
- [ ] Test 3: Modified code blocked ✅
- [ ] Proxy terminal shows detections
- [ ] Browser shows 403 errors when blocked
- [ ] Proxy stopped and disabled

---

## 🚀 Next Steps After Testing

Once you've verified it works:

1. **Add your real proprietary code**:
   ```bash
   cp /path/to/your/code/*.py ./proprietary_code/
   ```

2. **Test with your code**:
   ```bash
   python check_code.py --file ./proprietary_code/your_file.py
   ```

3. **For production use**, consider:
   - **Bifrost plugin** (better performance, no browser config)
   - See `TERMINAL_AGENTS_SETUP.md` for setup

4. **Adjust threshold** if needed:
   - Edit `security/fuzzy_detector.py`, line 13
   - Lower (50) = more strict, may have false positives
   - Higher (70) = more lenient, may miss some matches
   - Default (60) = balanced

---

## 💡 Tips

- **Test with your actual code**: The sample code is just for testing
- **Try different variations**: Rename variables, reorder lines, etc.
- **Check the similarity scores**: Shown in proxy terminal
- **Use log_only mode first**: Set `BLOCK_ON_DETECTION = False` in `security/config.py` to test without blocking
- **Monitor the logs**: Keep an eye on the proxy terminal

---

## 🎉 You're Done!

If all tests passed, your proprietary code detection system is working correctly and ready to protect your code!

For production deployment, see:
- `BIFROST_INTEGRATION_GUIDE.md` - For Bifrost plugin setup
- `TERMINAL_AGENTS_SETUP.md` - For terminal agents and AI IDEs
- `README.md` - For complete documentation
