# Sample Test Case: Verifying the Bifrost Proxy

This guide explains how to verify that the Bifrost gateway is correctly filtering and forwarding requests using a local mock environment.

## Overview

We will use:
1. **Mock AI Agent:** A Python script (`tests/mock_agent.py`) that mimics an LLM backend.
2. **Bifrost Proxy:** The Go gateway configured to point to the mock agent.
3. **Verification Script:** A Bash script (`tests/verify_proxy.sh`) that sends test cases (Clean, Injection, PII) and checks the results.

## Prerequisites

- **Python 3.x** with `Flask` (`pip install flask`)
- **Go 1.26+** (to run/build Bifrost)
- **Bifrost Dependencies:** OPA, Lakera, and Presidio must be configured or mocked.

## Execution Steps

### 1. Start the Mock AI Agent
In a new terminal:
```bash
python tests/mock_agent.py
```
*Expected: "Mock AI Agent running on http://localhost:8001"*

### 2. Start the Bifrost Proxy
In another terminal, ensure your `.env` has the following:
```env
AI_AGENT_URL=http://localhost:8001
PORT=8080
# ensure other security layer URLs are set if using real services
```
Then run Bifrost:
```bash
cd bifrost
go run proxy.go
```

### 3. Run the Verification Script
In a third terminal:
```bash
chmod +x tests/verify_proxy.sh
./tests/verify_proxy.sh
```

## What This Validates

| Test Case | Payload | Expected Outcome | Logic |
|---|---|---|---|
| **Clean** | "Tell me a joke" | **PASS (200 OK)** | Payload is forwarded to the mock agent; reply is returned. |
| **Injection** | "ignore previous..." | **BLOCK (403 Forbidden)** | Lakera middleware detects the threat and short-circuits. |
| **PII/SSN** | "My SSN is..." | **BLOCK (403 Forbidden)** | OPA/Presidio detects sensitive data and rejects the request. |

> [!TIP]
> This setup allows you to test the **entire pipeline** without incurring costs or sending sensitive data to real LLM providers.
