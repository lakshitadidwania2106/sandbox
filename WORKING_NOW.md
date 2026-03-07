# ✅ MITM Proxy is Running!

## Status: WORKING

The proxy is now listening on port 8080.

---

## Quick Setup (Choose One)

### Option 1: Firefox (EASIEST - 2 minutes)

1. **Open Firefox**

2. **Configure Proxy**:
   - Menu (☰) → Settings
   - Scroll to "Network Settings" → Click "Settings"
   - Select "Manual proxy configuration"
   - HTTP Proxy: `127.0.0.1`
   - Port: `8080`
   - ✅ Check "Also use this proxy for HTTPS"
   - Click "OK"

3. **Test**:
   - Go to: `https://google.com`
   - Click "Advanced" → "Accept the Risk and Continue"
   - Page loads ✅

4. **Test ChatGPT**:
   - Go to: `https://chatgpt.com`
   - Accept certificate warning
   - Try normal chat: Works ✅
   - Try proprietary code: Gets blocked 🚫

---

### Option 2: Chrome (Needs Certificate)

1. **Install Certificate First**:
   ```bash
   python install_certificate.py
   ```
   Follow the instructions

2. **Configure Windows Proxy**:
   - Press `Win + I`
   - Network & Internet → Proxy
   - Turn ON "Use a proxy server"
   - Address: `127.0.0.1`, Port: `8080`
   - Save

3. **Restart Chrome**

4. **Test**:
   - Go to: `https://google.com`
   - Should load without warning ✅

---

## Test with ChatGPT

### Test 1: Normal Chat (Should Work)
```
You: Hello, how are you?
Result: ✅ Works normally
```

### Test 2: Generic Code (Should Work)
```python
def add(a, b):
    return a + b
```
Result: ✅ Sends to ChatGPT

### Test 3: Proprietary Code (Should Block)
```python
def calculate_secret_score(data, weights, threshold=0.5):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    
    if score > threshold:
        return score * 1.5
    return score
```
Result: 🚫 BLOCKED - You'll see "403 Forbidden"

Check the proxy terminal - you'll see:
```
🚨 PROPRIETARY CODE DETECTED!
🚫 Blocking request
```

---

## Troubleshooting

### Issue: Certificate warnings in Firefox

**Solution**: Just click "Advanced" → "Accept the Risk" for each site
- Firefox will remember your choice
- This is normal for MITM proxies

### Issue: Sites don't load

**Solution**:
1. Check proxy terminal shows "HTTP(S) proxy listening at *:8080"
2. Check browser proxy is configured: `127.0.0.1:8080`
3. Try `http://mitm.it` first (no certificate needed)

### Issue: ChatGPT not being blocked

**Solution**:
1. Make sure you're pasting the exact proprietary code
2. Check proxy terminal for detection messages
3. Verify proprietary code exists in `./proprietary_code/`

---

## Stop the Proxy

When done testing:

1. **Stop proxy**: Press `Ctrl+C` in the terminal

2. **Disable proxy**:
   - **Firefox**: Settings → Network Settings → "No proxy"
   - **Chrome**: Windows Settings → Network & Internet → Proxy → Turn OFF

---

## Summary

✅ Proxy is running on port 8080
✅ Certificate is at: `C:\Users\Pragati Sharma\.mitmproxy\mitmproxy-ca-cert.cer`
✅ Use Firefox for easiest setup (no certificate install needed)
✅ Test with ChatGPT to see blocking in action

**Next**: Configure Firefox proxy and test!
