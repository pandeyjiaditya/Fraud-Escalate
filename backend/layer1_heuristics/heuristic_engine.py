from .phishing_rules import check_phishing
from .credential_rules import check_credentials
from .url_rules import check_url
from .intent_rules import check_intent
from .urgency_rules import check_urgency


def run_heuristics(data):

    text = data["clean_text"]

    score = 0
    flags = []

    if "urgent" in text:
        score += 20
        flags.append("urgency")

    if "otp" in text or "password" in text:
        score += 26.67
        flags.append("credential_theft")

    if "http" in text:
        score += 20
        flags.append("suspicious_url")

    if "bank" in text or "account" in text:
        score += 13.33
        flags.append("financial_intent")

    if "suspended" in text or "blocked" in text:
        score += 20
        flags.append("strong_phishing")

    confidence = min(score / 100, 1.0)
    score = min(score, 100)

    return {
        "heuristic_score": score,
        "flags": flags,
        "confidence": round(confidence, 2)
    }