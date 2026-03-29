FINANCIAL_KEYWORDS = [
    "bank",
    "account",
    "credit",
    "debit",
    "loan",
    "payment",
    "wallet",
    "transaction"
]


def check_intent(text):

    for word in FINANCIAL_KEYWORDS:
        if word in text:
            return ["financial_intent"]

    return []