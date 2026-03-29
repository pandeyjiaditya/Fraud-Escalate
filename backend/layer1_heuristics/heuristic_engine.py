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
        score += 27
        flags.append("credential_theft")

    if "http" in text:
        score += 20
        flags.append("suspicious_url")

    if "bank" in text or "account" in text:
        score += 13
        flags.append("financial_intent")

    if "suspended" in text or "blocked" in text:
        score += 20
        flags.append("strong_phishing")

    # ✅ IMPROVED CONFIDENCE: Base on number of flags + score strength
    # Number of flags detected = more certain
    flag_count = len(flags)
    score_strength = min(score / 100, 1.0)  # Normalize score

    # Confidence increases with more flags and higher scores
    if flag_count >= 3:
        confidence = min(0.85 + (flag_count * 0.05), 1.0)  # 3+ flags = 0.85-0.95
    elif flag_count == 2:
        confidence = min(0.70 + (score_strength * 0.15), 1.0)  # 2 flags = 0.70-0.85
    elif flag_count == 1:
        confidence = min(0.50 + (score_strength * 0.25), 1.0)  # 1 flag = 0.50-0.75
    else:
        confidence = min(0.40 + (score_strength * 0.30), 1.0)  # No flags = 0.40-0.70

    score = min(int(score), 100)

    return {
        "heuristic_score": score,
        "flags": flags,
        "confidence": round(confidence, 2)
    }