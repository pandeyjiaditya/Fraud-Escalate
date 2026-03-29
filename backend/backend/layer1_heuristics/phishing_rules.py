PHISHING_PATTERNS = [
    "verify your account",
    "update your account",
    "click here",
    "login immediately",
    "account suspended",
    "security alert",
    "unauthorized access"
]


def check_phishing(text):

    matches = [p for p in PHISHING_PATTERNS if p in text]

    if len(matches) >= 2:
        return ["strong_phishing"]

    elif len(matches) == 1:
        return ["phishing"]

    return []