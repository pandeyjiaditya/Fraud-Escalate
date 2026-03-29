def build_prompt(text, layer1, layer2, final):
    """Backward compatible prompt builder (old signature)"""
    return build_prompt_explanation(text, {}, layer1, layer2, {"llm_score": 0}, final)


def build_prompt_explanation(text, layer0, layer1, layer2, layer3_scoring, final):
    """
    Build comprehensive explanation prompt using all layer outputs.

    Args:
        text: clean message text
        layer0: dict with privacy/features
        layer1: dict with heuristic outputs
        layer2: dict with ML model outputs
        layer3_scoring: dict with LLM scoring (llm_score, llm_confidence, reasoning)
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

    # Layer 3 LLM Scoring
    llm_score = layer3_scoring.get("llm_score", 0)
    llm_confidence = layer3_scoring.get("llm_confidence", 0)
    llm_reasoning = layer3_scoring.get("reasoning", "")

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

Layer 0 (Privacy & Features):
- Entities: {features.get('entity_count', 'N/A')}
- Links: {features.get('link_count', 'N/A')}
- Urgency Keywords: {features.get('urgency_keywords', [])}
- Credential Request: {features.get('credential_request', False)}

Layer 1 (Heuristic Detection):
- Flags: {flags}
- Score: {heuristic_score}/100
- Confidence: {heuristic_confidence}

Layer 2 (ML Models):
- Text Score: {ml_text_score}/100
- URL Score: {url_ml_score}/100
- Deepfake Score: {deepfake_score}/100

Layer 3 (LLM Analysis):
- LLM Score: {llm_score}/100
- LLM Confidence: {llm_confidence}
- LLM Reasoning: {llm_reasoning}

--- FINAL DECISION (Risk Engine Fusion) ---
- Final Risk Score: {risk_score}/100
- Decision: {decision}
- Confidence: {final_conf}

--- INSTRUCTIONS ---
1. Explain why the Risk Engine reached this decision.
2. Highlight the key signal layers that contributed most.
3. Note any signal agreement or disagreement.
4. Describe the fraud indicators (urgency, phishing, credential requests, suspicious links, deepfake, etc.).
5. Keep explanation concise (4–6 lines).
6. Use simple, professional language.

--- OUTPUT FORMAT ---
Explanation:
"""

    return prompt