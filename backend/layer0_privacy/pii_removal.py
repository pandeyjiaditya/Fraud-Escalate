import re


def remove_pii(text: str):

    # -----------------------------
    # EMAIL
    # -----------------------------
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "<EMAIL>",
        text
    )

    # -----------------------------
    # PHONE NUMBER (India)
    # 10 digits starting with 6-9
    # -----------------------------
    text = re.sub(
        r"\b[6-9]\d{9}\b",
        "<PHONE_NUMBER>",
        text
    )

    # -----------------------------
    # AADHAAR (12 digits, optional spaces)
    # Example: 1234 5678 9123
    # -----------------------------
    text = re.sub(
        r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        "<AADHAAR>",
        text
    )

    # -----------------------------
    # PAN CARD (ABCDE1234F)
    # -----------------------------
    text = re.sub(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
        "<PAN>",
        text
    )

    # -----------------------------
    # IFSC CODE (SBIN0001234)
    # -----------------------------
    text = re.sub(
        r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
        "<IFSC>",
        text
    )

    # -----------------------------
    # BANK ACCOUNT NUMBER
    # (9 to 18 digits)
    # -----------------------------
    text = re.sub(
        r"\b\d{9,18}\b",
        "<BANK_ACCOUNT>",
        text
    )

    # -----------------------------
    # CARD NUMBERS (credit/debit)
    # -----------------------------
    text = re.sub(
        r"\b(?:\d{4}[\s-]?){3,4}\b",
        "<CARD_NUMBER>",
        text
    )

    # -----------------------------
    # OTP (4–6 digits)
    # -----------------------------
    text = re.sub(
        r"\b\d{4,6}\b",
        "<OTP>",
        text
    )

    return text