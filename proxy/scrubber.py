import re

dangerous_patterns = [
    "ignore previous instructions",
    "reveal secrets",
    "bypass security",
    "send passwords"
]


def scrub_input(text):
    lowered = text.lower()

    for pattern in dangerous_patterns:
        if pattern in lowered:
            return None

    return text
