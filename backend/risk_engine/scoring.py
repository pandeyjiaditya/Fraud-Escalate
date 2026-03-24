def calculate_risk_score(layer1, layer2=None):

    heuristic_score = layer1["heuristic_score"]

    # 🔥 CASE 1: Very high heuristic → skip ML
    if heuristic_score >= 120:
        return 95  # almost certain fraud

    # 🔥 CASE 2: Very low heuristic → safe
    if heuristic_score <= 20:
        return 10

    # 🔥 CASE 3: Medium → use ML
    ml_prob = layer2["ml_probability"] if layer2 else 0.5

    heuristic_scaled = min(heuristic_score, 100)
    ml_scaled = ml_prob * 100

    # Dynamic weighting
    if heuristic_score > 70:
        weight_h = 0.7
        weight_ml = 0.3
    else:
        weight_h = 0.5
        weight_ml = 0.5

    final_score = (weight_h * heuristic_scaled) + (weight_ml * ml_scaled)

    return round(final_score, 2)