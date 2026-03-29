def build_prompt(text, layer1, layer2, final):
    """Backward compatible prompt builder (old signature)"""
    return build_prompt_explanation(text, {}, layer1, layer2, {"score_3": 0, "confidence_3": 0, "summary_1": "", "summary_2": ""}, final)


def build_prompt_explanation(text, layer0, layer1, layer2, layer3_scoring, final):
    """
    Build FINAL explanation prompt using all layer outputs + Layer 3 summaries.

    This is used for the SECOND (final) LLM call.

    Args:
        text: clean message text
        layer0: dict with privacy/features
        layer1: dict with heuristic outputs
        layer2: dict with ML model outputs
        layer3_scoring: dict with Layer 3 analysis:
            - summary_1: LLM explanation of heuristic findings
            - summary_2: LLM explanation of ML findings
            - score_3: LLM's fraud risk score
            - confidence_3: LLM's confidence
        final: dict with final risk score and decision from Risk Engine
    """

    # Layer 0 features
    features = layer0.get("features", {}) if layer0 else {}

    # Layer 1 heuristics
    flags = layer1.get("flags", []) if layer1 else []
    heuristic_score = layer1.get("heuristic_score", 0) if layer1 else 0
    heuristic_confidence = layer1.get("confidence", 0) if layer1 else 0

    # Layer 2 ML signals
    ml_text_score = 0
    ml_text_confidence = 0
    url_ml_score = 0
    deepfake_score = 0

    if layer2:
        ml_text_score = layer2.get("ml_text_score", 0)
        ml_text_confidence = layer2.get("ml_text_confidence", 0)
        url_ml_score = layer2.get("url_ml_score", 0)
        deepfake_score = layer2.get("deepfake_score", 0)

    # Layer 3 LLM Analysis (from FIRST LLM call)
    summary_1 = layer3_scoring.get("summary_1", "") if layer3_scoring else ""
    summary_2 = layer3_scoring.get("summary_2", "") if layer3_scoring else ""
    score_3 = layer3_scoring.get("score_3", 0) if layer3_scoring else 0
    confidence_3 = layer3_scoring.get("confidence_3", 0) if layer3_scoring else 0

    # Final Risk Engine output
    risk_score = final.get("risk_score", 0)
    decision = final.get("decision", "")
    final_conf = final.get("confidence", 0)

    prompt = f"""
You are a cybersecurity expert specializing in fraud detection.

Based on comprehensive analysis from multiple detection layers, provide a clear, professional explanation of the fraud risk assessment.

--- MESSAGE CONTENT ---
{text}

--- SIGNAL ANALYSIS ---

Layer 1 (Heuristic Detection):
- Detected Flags: {flags}
- Score: {heuristic_score}/100
- Confidence: {heuristic_confidence}
- Analysis: {summary_1}

Layer 2 (ML Models):
- Text Score: {ml_text_score}/100
- URL Score: {url_ml_score}/100
- Deepfake Score: {deepfake_score}/100
- Analysis: {summary_2}

Layer 3 (LLM Analysis):
- LLM Score: {score_3}/100
- LLM Confidence: {confidence_3}

--- FINAL DECISION (Risk Engine Fusion) ---
- Final Risk Score: {risk_score}/100
- Decision: {decision}
- Confidence: {final_conf}

--- INSTRUCTIONS ---
1. Synthesize findings from all layers (heuristics, ML, and LLM analysis provided above)
2. Explain why the Risk Engine reached the "{decision}" decision
3. Highlight key signals that contributed most
4. Note any signal agreement or disagreement
5. Describe the specific fraud indicators detected (urgency, phishing, credential requests, suspicious links, etc.)
6. Keep explanation concise (4–6 lines)
7. Use simple, professional language suitable for end users

--- OUTPUT FORMAT ---
Explanation:
"""

    return prompt