# 🛡️ Bifrost Security Testing Dashboard

## ✅ NEW UI CREATED - Giskard.ai Style!

### 3-Column Layout:

```
┌─────────────────────────────────────────────────────────┐
│  🛡️ Bifrost Security Testing Dashboard      ● ACTIVE   │
├──────────────┬──────────────────────┬──────────────────┤
│              │                      │                  │
│  ⚔️ ATTACKS  │    🤖 AI AGENT      │   🚨 ALERTS     │
│              │                      │                  │
│ • Injection  │  [Test Input Box]   │  • Blocked      │
│ • Jailbreak  │                      │  • Warnings     │
│ • PII Leak   │  [Run Test Button]  │  • Pass         │
│ • Combined   │                      │                  │
│              │  [Agent Response]    │  [Live Feed]    │
│              │                      │                  │
└──────────────┴──────────────────────┴──────────────────┘
```

## Features:

### LEFT PANEL - Attack Vectors
- ⚔️ Pre-loaded attack scenarios
- Click to load into test input
- Color-coded severity (HIGH/MEDIUM/LOW)
- 7 attack types:
  - Direct Prompt Injection
  - Jailbreak Attempt
  - Credit Card Leakage
  - Email & Phone PII
  - SSN Exposure
  - Combined Attack
  - Normal Query (safe)

### CENTER PANEL - Agent Testing
- 📊 Stats bar (Total/Blocked/Scrubbed/Passed)
- 📝 Test input textarea
- 🚀 Run Security Test button
- 📤 Agent response display
- Real-time processing feedback

### RIGHT PANEL - Security Alerts
- 🚨 Live alert feed
- Color-coded alerts:
  - 🚫 Red = Blocked
  - ⚠️ Yellow = Warning/Scrubbed
  - ✅ Green = Passed
- Timestamp for each alert
- Security layer details
- Auto-scrolling (keeps last 10)

## How to Use:

### 1. Start the Dashboard:
```bash
./start_dashboard.sh
```

### 2. Open Browser:
```
http://localhost:5000/dashboard
```

### 3. Test Security:

**Option A - Use Pre-loaded Attacks:**
1. Click any attack in left panel
2. Click "Run Security Test"
3. Watch alerts appear in right panel

**Option B - Custom Input:**
1. Type your own test in center panel
2. Click "Run Security Test"
3. See results

## What You'll See:

### Example Flow:

1. **Click "Direct Prompt Injection"** (left panel)
   - Loads: "Ignore all previous instructions..."
   
2. **Click "Run Security Test"** (center)
   - Stats update: Total +1
   - Processing animation shows
   
3. **Alert Appears** (right panel):
   ```
   🚫 Request Blocked
   Prompt injection detected
   
   lakera: BLOCKED
   opa: PASS
   presidio_input: PASS
   ```

4. **Stats Update**:
   - Total: 1
   - Blocked: 1
   - Scrubbed: 0
   - Passed: 0

### Try Different Attacks:

**Jailbreak** → 🚫 Blocked by Lakera
**Credit Card** → ⚠️ Scrubbed by Presidio
**Normal Query** → ✅ Passes all layers

## URLs:

- **Original App**: http://localhost:5000
- **Security Dashboard**: http://localhost:5000/dashboard

## Design Inspired By:

✅ Dark theme (like Giskard.ai)
✅ 3-column layout
✅ Attack vectors on left
✅ Testing interface in center
✅ Live alerts on right
✅ Real-time stats
✅ Color-coded severity
✅ Professional security testing UI

## Files:

- `templates/dashboard.html` - New security testing UI
- `templates/index.html` - Original Amazon simulator
- `app.py` - Updated with `/dashboard` and `/api/test` routes
- `start_dashboard.sh` - Startup script

## Perfect For:

- 🔍 Security testing
- 🎯 Demo purposes
- 📊 Monitoring attacks
- 🛡️ Showing Bifrost in action
- 👥 Client presentations

**Your Bifrost security gateway now has a professional testing dashboard!** 🎯
