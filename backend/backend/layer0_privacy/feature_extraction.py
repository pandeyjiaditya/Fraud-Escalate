import re


def extract_features(text: str):

    features = {}

    features["length"] = len(text)

    features["has_url"] = bool(re.search(r"http", text))

    features["has_urgent_words"] = any(
        word in text
        for word in ["urgent", "verify", "password", "account", "bank"]
    )

    features["has_numbers"] = bool(re.search(r"\d", text))

    # 🔥 Important feature
    features["has_sensitive_keywords"] = any(
        word in text
        for word in ["card", "otp", "pin", "account number"]
    )

    return features