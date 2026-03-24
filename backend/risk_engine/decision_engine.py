from .scoring import calculate_risk_score


def make_decision(layer1, layer2=None):

    score = calculate_risk_score(layer1, layer2)

    l1_conf = layer1.get("confidence", 0)

    l2_conf = 0
    if layer2:
        l2_conf = layer2.get("confidence", 0)

    final_conf = (0.6 * l1_conf) + (0.4 * l2_conf)

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
        "confidence": round(final_conf, 2)
    }