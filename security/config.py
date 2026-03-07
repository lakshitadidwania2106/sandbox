"""
Security Configuration
======================

Centralized configuration for all security layers.
Loads settings from environment variables with sensible defaults.

Environment Variables:
    LAKERA_API_KEY              : API key for Lakera Guard service (required for Layer 3)
    LAKERA_API_URL              : Base URL for Lakera Guard API (default: https://api.lakera.ai)
    LAKERA_CONFIDENCE_THRESHOLD : Minimum confidence to flag input as malicious (default: 0.5)
    PRESIDIO_SCORE_THRESHOLD    : Minimum score for Presidio entity detection (default: 0.7)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# =============================================================================
# Layer 3: Lakera Guard Configuration
# =============================================================================

# TODO: Ensure LAKERA_API_KEY is set in your .env file before using Layer 3.
#       Sign up at https://platform.lakera.ai to get your API key.
LAKERA_API_KEY = os.getenv("LAKERA_API_KEY", "")

# Base URL for the Lakera Guard API
# TODO: Update this if you're using a self-hosted Lakera instance.
LAKERA_API_URL = os.getenv("LAKERA_API_URL", "https://api.lakera.ai")

# Confidence threshold for flagging prompt injection (0.0 to 1.0)
# Lower values = more aggressive blocking, Higher values = more permissive
# TODO: Tune this threshold based on your use case and false positive tolerance.
LAKERA_CONFIDENCE_THRESHOLD = float(
    os.getenv("LAKERA_CONFIDENCE_THRESHOLD", "0.8")
)


# =============================================================================
# Layer 4: Presidio Configuration
# =============================================================================

# Minimum confidence score for Presidio entity detection (0.0 to 1.0)
# Lower values = more sensitive detection, Higher values = fewer false positives
# TODO: Tune this threshold based on your application's sensitivity requirements.
PRESIDIO_SCORE_THRESHOLD = float(
    os.getenv("PRESIDIO_SCORE_THRESHOLD", "0.3")
)

# List of PII entity types to detect in LLM output
# TODO: Add or remove entity types based on what your application might leak.
#       Full list: https://microsoft.github.io/presidio/supported_entities/
PRESIDIO_ENTITIES = [
    "CREDIT_CARD",          # Credit card numbers
    "EMAIL_ADDRESS",        # Email addresses
    "PHONE_NUMBER",         # Phone numbers
    "US_SSN",               # US Social Security numbers
    "IP_ADDRESS",           # IP addresses
    "IBAN_CODE",            # International bank account numbers
    "CRYPTO",               # Cryptocurrency wallet addresses
    "PERSON",               # Person names
    "US_PASSPORT",          # US passport numbers
    "US_DRIVER_LICENSE",    # US driver's license numbers
    "LOCATION",             # Addresses and locations
    "DATE_TIME",            # Dates and times
    "NRP",                  # Nationalities, religious or political groups
    "URL",                  # URLs
    "US_BANK_NUMBER",       # Bank account numbers
    "AU_ABN",               # Australian Business Number
    "AU_ACN",               # Australian Company Number
    "AU_TFN",               # Australian Tax File Number
    "AU_MEDICARE",          # Australian Medicare Number
]

# Redaction placeholder format
# TODO: Customize the redaction placeholder to match your output format.
PRESIDIO_REDACT_PLACEHOLDER = "<REDACTED:{entity_type}>"
