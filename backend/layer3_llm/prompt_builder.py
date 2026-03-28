def build_prompt(text, layer1, layer2, final):

    flags = layer1.get("flags", [])
    heuristic_score = layer1.get("heuristic_score", 0)
    heuristic_confidence = layer1.get("confidence", 0)

    ml_prob = 0
    ml_conf = 0

    if layer2:
        ml_prob = layer2.get("ml_probability", 0)
        ml_conf = layer2.get("confidence", 0)

    risk_score = final.get("risk_score", 0)
    decision = final.get("decision", "")
    final_conf = final.get("confidence", 0)

    prompt = f"""
You are a cybersecurity expert specializing in fraud detection.

Analyze the following message and provide a clear, professional explanation.

--- MESSAGE ---
{text}

--- DETECTION SIGNALS ---
Heuristic Flags: {flags}
Heuristic Score: {heuristic_score}
Heuristic Confidence: {heuristic_confidence}

ML Probability of Fraud: {ml_prob}
ML Confidence: {ml_conf}

Final Risk Score: {risk_score}
Final Decision: {decision}
Final Confidence: {final_conf}

--- INSTRUCTIONS ---
1. Explain WHY this message is fraud or safe.
2. Highlight key fraud indicators (e.g., urgency, phishing, suspicious links, credential requests).
3. Mention how the decision was derived from signals.
4. Keep explanation concise (3–5 lines).
5. Use simple, professional language.

--- OUTPUT FORMAT ---
Explanation:
"""

    return prompt