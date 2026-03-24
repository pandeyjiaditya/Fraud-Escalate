CREDENTIAL_KEYWORDS = [
    "enter otp",
    "share otp",
    "provide password",
    "enter pin",
    "account number",
    "card details"
]


def check_credentials(text):

    flags = []

    for keyword in CREDENTIAL_KEYWORDS:
        if keyword in text:
            flags.append("credential_theft")

    return flags