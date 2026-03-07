"""
Security Package - AI Security Middleware
==========================================

This package provides agent-agnostic security layers for protecting
LLM agents from prompt injection attacks and PII/secret leakage.

Layers provided:
    - Layer 3 (Lakera Guard): ML-based prompt injection detection on INPUT
    - Layer 4 (Presidio): PII/secret leak detection and redaction on OUTPUT

Usage:
    from security.lakera_guard import scan_prompt
    from security.presidio_analyzer import scan_output, redact_output
"""

# --- Layer 3: Lakera Guard (Prompt Injection Detection) ---
from security.lakera_guard import scan_prompt

# --- Layer 4: Presidio (PII/Secret Leak Detection) ---
from security.presidio_analyzer import scan_output, redact_output

__all__ = [
    "scan_prompt",
    "scan_output",
    "redact_output",
]
