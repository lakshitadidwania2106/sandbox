# Quick Test with ChatGPT - 5 Minutes

## Step 1: Start Proxy (1 min)

```bash
python security/start_proxy.py
```

Keep this terminal open!

## Step 2: Install Certificate (1 min)

1. Open browser → Go to: **http://mitm.it**
2. Click your OS (Windows/Mac/Linux)
3. Install the certificate

**Windows**: Double-click → Install → Trusted Root Certification Authorities  
**Mac**: Double-click → Keychain Access → Trust → Always Trust  
**Firefox**: Settings → Certificates → Import → Trust for websites

## Step 3: Configure Proxy (1 min)

**Chrome/Edge (uses Windows system proxy):**
- Press `Win + I` → Network & Internet → Proxy
- Turn ON "Use a proxy server"
- Address: `127.0.0.1`, Port: `8080`
- Click Save
- **Note**: Chrome doesn't have its own proxy settings, it uses Windows system proxy

**Firefox (has its own proxy):**
- Settings → Network Settings → Settings
- Manual proxy configuration
- HTTP Proxy: `127.0.0.1`, Port: `8080`
- Check "Also use this proxy for HTTPS"

**Mac:**
- System Preferences → Network → Advanced → Proxies
- HTTP/HTTPS Proxy: `127.0.0.1:8080`

**Linux:**
- Settings → Network → Proxy
- Manual: `127.0.0.1:8080`

## Step 4: Test on ChatGPT (2 min)

### Test A: Proprietary Code (Should BLOCK 🚫)

1. Go to: **https://chatgpt.com**
2. Paste this code:

```python
def calculate_secret_score(data, weights, threshold=0.5):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    
    if score > threshold:
        return score * 1.5
    return score
```

3. Try to send → Should see **403 Forbidden** or error

**Check proxy terminal** - should show:
```
🚨 PROPRIETARY CODE DETECTED!
🚫 Blocking request
```

### Test B: Generic Code (Should ALLOW ✅)

1. Paste this code:

```python
def add(a, b):
    return a + b
```

2. Send → Should work normally

**Check proxy terminal** - should show:
```
✅ No proprietary code detected
```

## Step 5: Clean Up

1. Stop proxy: `Ctrl+C`
2. Disable proxy in browser settings
3. Done! ✅

---

## Expected Results

| Test | Code Type | Expected | What You See |
|------|-----------|----------|--------------|
| A | Proprietary | 🚫 BLOCKED | 403 error, request fails |
| B | Generic | ✅ ALLOWED | Message sends normally |

---

## Troubleshooting

**Certificate warning?**
→ Install certificate from http://mitm.it and restart browser

**Not blocking?**
→ Check proxy terminal for errors, verify proxy is `127.0.0.1:8080`

**All requests blocked?**
→ Threshold too low, check `security/fuzzy_detector.py` line 13

---

## Success! 🎉

If Test A was blocked and Test B was allowed, your system is working!

**Next steps:**
- Add your real code to `./proprietary_code/`
- Test with your code: `python check_code.py --file your_file.py`
- For production: See `BIFROST_INTEGRATION_GUIDE.md`

---

**Full guide**: See `MANUAL_TESTING_GUIDE.md` for detailed instructions
