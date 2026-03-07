blocked_keywords = [
    "password",
    "secret",
    "api key"
]


def check_output(text):
    for word in blocked_keywords:
        if word in text.lower():
            return False

    return True
