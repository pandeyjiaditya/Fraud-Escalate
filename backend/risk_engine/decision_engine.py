from .scoring import calculate_risk_score


def make_decision(layer1, layer2=None):

    heuristic_score = layer1["heuristic_score"]

    # 🔥 Smart routing
    if heuristic_score >= 120:
        return {
            "risk_score": 95,
            "decision": "BLOCK",
            "reason": "High confidence fraud (rules)"
        }

    if heuristic_score <= 20:
        return {
            "risk_score": 10,
            "decision": "ALLOW",
            "reason": "Low risk (rules)"
        }

    # 🔥 Use ML only when needed
    score = calculate_risk_score(layer1, layer2)

    # Decision thresholds
    if score <= 30:
        decision = "ALLOW"

    elif score <= 60:
        decision = "MONITOR"

    elif score <= 80:
        decision = "REVIEW"

    else:
        decision = "BLOCK"

    return {
        "risk_score": score,
        "decision": decision,
        "reason": "Combined heuristic + ML analysis"
    }