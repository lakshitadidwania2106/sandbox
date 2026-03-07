CANARY_TOKEN = "superpassword123#CANARY"


def detect_leak(text):
    if CANARY_TOKEN in text:
        return True

    return False
