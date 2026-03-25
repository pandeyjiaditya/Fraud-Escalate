from .scoring import calculate_risk_score


def make_decision(layer1, layer2=None, context_type: str = "email", meta: dict = None):
    """
    Make escalation decision based on risk score

    Args:
        layer1: dict with heuristic_score and confidence
        layer2: dict with ml signals (ml_text_score, llm_score, etc.)
        context_type: "email" | "file" | "audio"
        meta: optional dict with OCR info, URL presence, etc.

    Returns:
        dict with risk_score, decision, and confidence
    """

    score = calculate_risk_score(layer1, layer2, context_type, meta)

    l1_conf = layer1.get("confidence", 0) if layer1 else 0

    l2_conf = 0
    if layer2:
        # Average confidence across available signals
        confidences = [v for k, v in layer2.items() if "confidence" in k]
        l2_conf = sum(confidences) / len(confidences) if confidences else 0

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
        "confidence": round(final_conf, 2),
        "context_type": context_type
    }