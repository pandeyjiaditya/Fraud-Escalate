import re

# Pre-compiled regex patterns (compiled once at module import)
PATTERNS = {
    'email': re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    'phone': re.compile(r"\b[6-9]\d{9}\b"),
    'aadhaar': re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    'pan': re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"),
    'ifsc': re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
    'bank_account': re.compile(r"\b\d{9,18}\b"),
    'card_number': re.compile(r"\b(?:\d{4}[\s-]?){3,4}\b"),
    'otp': re.compile(r"\b\d{4,6}\b"),
}


def remove_pii(text: str):

    # EMAIL
    text = PATTERNS['email'].sub("<EMAIL>", text)

    # PHONE NUMBER (India)
    text = PATTERNS['phone'].sub("<PHONE_NUMBER>", text)

    # AADHAAR (12 digits, optional spaces)
    text = PATTERNS['aadhaar'].sub("<AADHAAR>", text)

    # PAN CARD (ABCDE1234F)
    text = PATTERNS['pan'].sub("<PAN>", text)

    # IFSC CODE (SBIN0001234)
    text = PATTERNS['ifsc'].sub("<IFSC>", text)

    # BANK ACCOUNT NUMBER (9 to 18 digits)
    text = PATTERNS['bank_account'].sub("<BANK_ACCOUNT>", text)

    # CARD NUMBERS (credit/debit)
    text = PATTERNS['card_number'].sub("<CARD_NUMBER>", text)

    # OTP (4–6 digits)
    text = PATTERNS['otp'].sub("<OTP>", text)

    return text