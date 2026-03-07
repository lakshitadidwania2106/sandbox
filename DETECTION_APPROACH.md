# 🔍 SigmaShield's Approach Explained

## 🎯 How SigmaShield Works

SigmaShield uses a **Man-in-the-Middle (MITM) Proxy** to intercept ALL network traffic from your computer and check if you're pasting proprietary code into websites.

### Architecture

```
Your Computer
    ↓
[MITM Proxy] ← Intercepts ALL HTTP/HTTPS traffic
    ↓
Checks each request:
  - ChatGPT?
  - Twitter?
  - StackOverflow?
  - Image upload?
    ↓
[Fuzzy Search] ← Compare against proprietary code
    ↓
Block or Allow
    ↓
Internet (ChatGPT, Twitter, etc.)
```

## 🔧 Technical Implementation

### 1. MITM Proxy Setup

```python
# start.py
def start():
    # Set system proxy to route ALL traffic through MITM
    set_mac_proxy("Wi-Fi", "127.0.0.1", 8080)
    
    # Start mitmproxy on port 8080
    subprocess.Popen(["mitmdump", "-s", "./proxy.py"])
```

**What this does:**
- Changes your system proxy settings
- Routes ALL HTTP/HTTPS traffic through localhost:8080
- mitmproxy intercepts and can modify/block requests

### 2. Request Interception

```python
# proxy.py
class BlockProprietaryRequests:
    def request(self, flow: http.HTTPFlow) -> None:
        url = flow.request.url.lower()
        
        # Check specific sites
        if "chatgpt.com" in url:
            handle_chatgpt(flow)
        
        if "x.com" in url and "createtweet" in url:
            handle_twitter(flow)
        
        if "stackoverflow.com" in url and "submit" in url:
            handle_stackoverflow(flow)
```

### 3. Site-Specific Handlers

#### ChatGPT Handler
```python
# chatgpt.py
def handle_chatgpt(flow):
    # Parse JSON request
    request_data = json.loads(flow.request.content)
    
    # Extract messages
    for message in request_data['messages']:
        parts = message.get('content', {}).get('parts', [])
        for part in parts:
            # Check if it's proprietary code
            if check_if_company_code(part):
                return True  # Block!
    
    return False  # Allow
```

#### Twitter Handler
```python
# twitter.py
def handle_twitter(flow):
    request_data = json.loads(flow.request.content)
    
    # Extract tweet text
    tweet_text = request_data['variables'].get('tweet_text')
    
    # Check if proprietary
    if check_if_company_code(tweet_text):
        return True  # Block!
```

#### StackOverflow Handler
```python
# stackoverflow.py
def handle_stackoverflow(flow):
    # Parse form data
    form_data = urllib.parse.parse_qs(flow.request.content)
    post_text = form_data.get('post-text', [''])[0]
    
    # Check if proprietary
    if check_if_company_code(post_text):
        return True  # Block!
```

### 4. Fuzzy Search Check

```python
# checker.py
def check_if_company_code(text):
    # Use fuzzy search against proprietary codebase
    matched = global_fuzzy_search(text, min_score=60)
    return matched

# fuzzysearch.py
def global_fuzzy_search(target_snippet, min_score=60):
    # Search all .py files in current directory
    for file_path in Path.rglob("*.py"):
        # Sliding window + RapidFuzz
        if fuzzy_search_in_file(file_path, target_snippet, min_score):
            return True  # Found match!
    
    return False
```

### 5. Image OCR (Bonus Feature)

```python
# proxy.py
if content_type.startswith("image/"):
    # Save image
    fp = save_image_for_ocr(flow)
    
    # Run OCR to extract text
    ocr_text = await get_code_in_image(fp)
    
    # Check if extracted text is proprietary
    if check_if_company_code(ocr_text):
        block(flow, "COMPANY_CODE_FOUND_IN_IMAGE")
```

## 🆚 SigmaShield vs Our Implementation

| Feature | SigmaShield | Our Implementation |
|---------|-------------|-------------------|
| **Approach** | MITM Proxy (system-wide) | Application-level hooks |
| **Scope** | ALL network traffic | Specific applications |
| **Detection** | RapidFuzz fuzzy search | Multiple methods |
| **Sites Monitored** | ChatGPT, Twitter, StackOverflow | Any HTTP endpoint |
| **Setup** | System proxy changes | No system changes |
| **Performance** | Intercepts everything | Only checks when needed |
| **Portability** | Requires mitmproxy | Pure Python |

## 🎯 What We're Using Instead

### Our Approach: Application-Level Interception

Instead of a system-wide MITM proxy, we use:

1. **Request Interceptor** (Application-level)
   ```python
   from security.request_interceptor import InterceptedSession
   
   # Drop-in replacement for requests.Session
   session = InterceptedSession()
   response = session.post("https://api.openai.com", json=data)
   # Automatically scanned!
   ```

2. **Middleware Integration** (Framework-level)
   ```python
   # FastAPI middleware
   @app.middleware("http")
   async def check_leaks(request, call_next):
       body = await request.body()
       result = detector.check_similarity(body)
       if result.is_similar:
           raise HTTPException(403, "Blocked")
       return await call_next(request)
   ```

3. **LangChain Callbacks** (Library-level)
   ```python
   class CodeLeakCallback(BaseCallbackHandler):
       def on_llm_start(self, prompts, **kwargs):
           for prompt in prompts:
               if detector.check_similarity(prompt).is_similar:
                   raise ValueError("Blocked!")
   ```

## 🔄 Implementing SigmaShield's MITM Approach in Bifrost

If you want the MITM proxy approach, here's how:

### Option 1: Use mitmproxy (SigmaShield's approach)

```python
# security/mitm_proxy.py
from mitmproxy import http
from security.enhanced_similarity_detector import EnhancedSimilarityDetector

detector = EnhancedSimilarityDetector()
detector.index_directory("./proprietary_code")

class BifrostProxy:
    def request(self, flow: http.HTTPFlow):
        # Check specific sites
        url = flow.request.url.lower()
        
        if "chatgpt.com" in url or "openai.com" in url:
            self.check_chatgpt(flow)
        
        if "x.com" in url or "twitter.com" in url:
            self.check_twitter(flow)
        
        if "stackoverflow.com" in url:
            self.check_stackoverflow(flow)
    
    def check_chatgpt(self, flow):
        try:
            data = json.loads(flow.request.content)
            for msg in data.get('messages', []):
                content = msg.get('content', '')
                result = detector.check_similarity(content)
                if result.is_similar:
                    self.block(flow, "Proprietary code detected")
        except:
            pass
    
    def block(self, flow, reason):
        flow.response = http.Response.make(
            403,
            f"Blocked: {reason}".encode(),
            {"Content-Type": "text/plain"}
        )

addons = [BifrostProxy()]
```

**Run it:**
```bash
# Install mitmproxy
pip install mitmproxy

# Start proxy
mitmdump -s security/mitm_proxy.py

# Configure system proxy to 127.0.0.1:8080
```

### Option 2: Browser Extension (Better for users)

```javascript
// extension.js (Chrome/Firefox)
chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        if (details.method === "POST") {
            // Extract request body
            let body = details.requestBody;
            
            // Send to Python backend for checking
            fetch('http://localhost:5000/check', {
                method: 'POST',
                body: JSON.stringify({content: body})
            }).then(response => {
                if (response.blocked) {
                    // Cancel the request
                    return {cancel: true};
                }
            });
        }
    },
    {urls: ["*://chatgpt.com/*", "*://x.com/*"]},
    ["blocking", "requestBody"]
);
```

### Option 3: Desktop App (Most user-friendly)

```python
# desktop_monitor.py
import pyperclip  # Monitor clipboard
import time

detector = EnhancedSimilarityDetector()
detector.index_directory("./proprietary_code")

last_clipboard = ""

while True:
    current = pyperclip.paste()
    
    if current != last_clipboard:
        # Check if clipboard contains proprietary code
        result = detector.check_similarity(current)
        
        if result.is_similar:
            # Alert user
            show_notification("⚠️ Proprietary code detected in clipboard!")
            
            # Optionally clear clipboard
            pyperclip.copy("")
        
        last_clipboard = current
    
    time.sleep(1)
```

## 📊 Comparison: Which Approach to Use?

### MITM Proxy (SigmaShield)
**Pros:**
- ✅ Monitors ALL traffic (system-wide)
- ✅ Works with any application
- ✅ Can't be bypassed by applications

**Cons:**
- ❌ Requires system proxy changes
- ❌ Intercepts ALL traffic (privacy concerns)
- ❌ Requires mitmproxy installation
- ❌ Can break some applications
- ❌ Requires HTTPS certificate trust

### Application-Level (Our Approach)
**Pros:**
- ✅ No system changes needed
- ✅ Only monitors specific applications
- ✅ Pure Python, portable
- ✅ Easier to deploy

**Cons:**
- ❌ Requires application integration
- ❌ Can be bypassed if not integrated
- ❌ Doesn't monitor browser traffic

### Browser Extension
**Pros:**
- ✅ Monitors browser traffic
- ✅ User-friendly
- ✅ No system changes

**Cons:**
- ❌ Only works in browser
- ❌ Requires extension installation
- ❌ Limited to supported browsers

### Desktop App (Clipboard Monitor)
**Pros:**
- ✅ Simple to use
- ✅ Works everywhere
- ✅ No integration needed

**Cons:**
- ❌ Only monitors clipboard
- ❌ Can be bypassed by typing
- ❌ Requires background process

## 🎯 Recommendation

**For Bifrost (LLM Gateway):**
Use **Application-Level Interception** (our current approach)
- Integrates with your LLM gateway
- No system changes
- Portable and maintainable

**For End-User Protection:**
Consider **Browser Extension** + **Clipboard Monitor**
- User-friendly
- Covers most use cases
- Easy to install

**For Maximum Security:**
Use **MITM Proxy** (SigmaShield approach)
- System-wide protection
- Can't be bypassed
- Requires more setup

## 🚀 Next Steps

Would you like me to implement:

1. **MITM Proxy version** (like SigmaShield)
2. **Browser Extension** (Chrome/Firefox)
3. **Clipboard Monitor** (Desktop app)
4. **Keep current approach** (Application-level)

Let me know which direction you want to go!
