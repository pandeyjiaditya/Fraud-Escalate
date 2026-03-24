from .phishing_rules import check_phishing
from .credential_rules import check_credentials
from .url_rules import check_url
from .intent_rules import check_intent
from .urgency_rules import check_urgency


def run_heuristics(data):

    if data["type"] in ["image", "audio", "video"]:
        return {"heuristic_score": 0, "flags": []}

    text = data["clean_text"]

    flags = []

    # Run all rules
    flags += check_phishing(text)
    flags += check_credentials(text)
    flags += check_url(text)
    flags += check_intent(text)
    flags += check_urgency(text)

    flags = list(set(flags))

    # 🔥 Advanced scoring
    score = 0

    scoring_map = {
        "strong_phishing": 50,
        "phishing": 30,
        "credential_theft": 50,
        "suspicious_url": 40,
        "long_url": 10,
        "financial_intent": 20,
        "urgency": 20
    }

    for flag in flags:
        score += scoring_map.get(flag, 0)

    # 🔥 Bonus rule (multi-signal attack)
    if "urgency" in flags and "credential_theft" in flags:
        score += 20

    return {
        "heuristic_score": score,
        "flags": flags
    }