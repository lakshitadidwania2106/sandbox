# AI Security Layer

A modular, agent-agnostic security middleware for protecting LLM agents from prompt injection attacks and PII/secret leakage.

## Architecture

```
User Request
  ─── INPUT PIPELINE ───
  → Layer 1 (Bifrost): Gateway                     [bifrost module]
  → Layer 2 (OPA): Policy Checker                  [opa module]
  → Layer 3 (Lakera): Prompt Injection Detection    [security/lakera_guard.py]
  ─── Agent processes request ───
  ─── OUTPUT PIPELINE ───
  → Layer 4 (Presidio): PII/Secret Leak Detection   [security/presidio_analyzer.py]
  → Response
```

## Layer 3: Lakera Guard (Input Security)

ML-based prompt injection detection via the [Lakera Guard API](https://platform.lakera.ai/docs/api).

**What it detects:**
- Prompt injection attacks
- Jailbreak attempts
- Adversarial payloads

**Usage:**
```python
from security.lakera_guard import scan_prompt, is_prompt_injection

# Full scan with detailed result
result = scan_prompt("Ignore all previous instructions")
if result.flagged:
    print(f"Blocked: {result.payload_type} (confidence: {result.confidence})")

# Simple boolean check
if is_prompt_injection(user_input):
    return "Request blocked"
```

## Layer 4: Presidio (Output Security)

PII and secret detection/redaction via [Microsoft Presidio](https://microsoft.github.io/presidio/).

**What it detects:**
- Credit card numbers, SSNs, passport numbers
- Email addresses, phone numbers, person names
- API keys, AWS keys, private keys, passwords
- Database connection strings, IP addresses
- IBAN codes, cryptocurrency wallet addresses

**Usage:**
```python
from security.presidio_analyzer import scan_output, redact_output

# Scan for PII
result = scan_output("Contact admin@company.com, card: 4111-1111-1111-1111")
if result.has_pii:
    print(f"Found {result.entity_count} entities: {result.entity_types}")

# Redact PII from output
clean_text = redact_output(agent_response)
```

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

### 2. Configure Environment
Create a `.env` file in the project root:
```env
# Layer 3: Lakera Guard
LAKERA_API_KEY=your_lakera_api_key_here
LAKERA_API_URL=https://api.lakera.ai
LAKERA_CONFIDENCE_THRESHOLD=0.5

# Layer 4: Presidio
PRESIDIO_SCORE_THRESHOLD=0.7
```

### 3. Get a Lakera API Key
Sign up at [platform.lakera.ai](https://platform.lakera.ai) and create an API key.

## Project Structure

```
security/
├── __init__.py              # Package exports
├── config.py                # Centralized configuration (env vars)
├── lakera_guard.py          # Layer 3 — Lakera prompt injection detection
├── presidio_analyzer.py     # Layer 4 — Presidio PII/secret detection
└── requirements.txt         # Security-specific dependencies
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `LAKERA_API_KEY` | *(required)* | Lakera Guard API key |
| `LAKERA_API_URL` | `https://api.lakera.ai` | Lakera API base URL |
| `LAKERA_CONFIDENCE_THRESHOLD` | `0.5` | Min confidence to block (0.0–1.0) |
| `PRESIDIO_SCORE_THRESHOLD` | `0.7` | Min score for PII detection (0.0–1.0) |

# Works on esp32. uses llvm, but has backend for us :)  
