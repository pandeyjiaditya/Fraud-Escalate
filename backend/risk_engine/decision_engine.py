from .scoring import calculate_risk_score


def generate_final_reasoning(score, layer1, layer2, decision):
    """
    Generate reasoning for the final decision.
    """
    heuristic_score = layer1.get("heuristic_score", 0) if layer1 else 0
    ml_score = layer2.get("ml_text_score", 0) if layer2 else 0

    reasoning_parts = []

    # Heuristic contribution
    if heuristic_score >= 100:
        reasoning_parts.append(f"Strong heuristic signals detected (score: {heuristic_score}/150)")
    elif heuristic_score >= 50:
        reasoning_parts.append(f"Moderate heuristic flags found (score: {heuristic_score}/150)")

    # ML contribution
    if ml_score >= 75:
        reasoning_parts.append(f"ML model classified as high fraud risk ({ml_score:.1f}/100)")
    elif ml_score >= 50:
        reasoning_parts.append(f"ML model detected suspicious patterns ({ml_score:.1f}/100)")

    # Decision rationale
    if decision == "BLOCK":
        reasoning = f"Critical fraud indicators detected. {' and '.join(reasoning_parts)}. Recommend immediate blocking."
    elif decision == "REVIEW":
        reasoning = f"Elevated fraud risk signals. {' and '.join(reasoning_parts)}. Manual review required."
    elif decision == "MONITOR":
        reasoning = f"Some suspicious patterns detected. {' and '.join(reasoning_parts)}. Continue monitoring."
    else:
        reasoning = "Content appears legitimate based on available signals. Proceed normally."

    return reasoning


def make_decision(layer1, layer2=None, context_type: str = "email", meta: dict = None):
    """
    Make escalation decision based on risk score

    Args:
        layer1: dict with heuristic_score and confidence
        layer2: dict with ml signals (ml_text_score, llm_score, etc.)
        context_type: "email" | "file" | "audio"
        meta: optional dict with OCR info, URL presence, etc.

    Returns:
        dict with risk_score, decision, confidence, and reasoning
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

    # Generate reasoning for final decision
    reasoning = generate_final_reasoning(score, layer1, layer2, decision)

    return {
        "risk_score": score,
        "decision": decision,
        "confidence": round(final_conf, 2),
        "context_type": context_type,
        "reasoning": reasoning
    }