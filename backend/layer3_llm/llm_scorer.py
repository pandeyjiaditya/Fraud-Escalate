from .ollama_client import call_ollama
import json
import re


def build_scoring_prompt(text, layer0, layer1, layer2):
    """
    Build a detailed prompt for LLM to independently score the fraud risk based on:
    - Raw input text
    - Layer 0 (privacy/features)
    - Layer 1 (heuristic signals)
    - Layer 2 (ML signals)
    """

    flags = layer1.get("flags", []) if layer1 else []
    heuristic_score = layer1.get("heuristic_score", 0) if layer1 else 0
    heuristic_confidence = layer1.get("confidence", 0) if layer1 else 0

    ml_text_score = 0
    ml_text_confidence = 0
    url_ml_score = 0
    deepfake_score = 0

    if layer2:
        ml_text_score = layer2.get("ml_text_score", 0)
        ml_text_confidence = layer2.get("ml_text_confidence", 0)
        url_ml_score = layer2.get("url_ml_score", 0)
        deepfake_score = layer2.get("deepfake_score", 0)

    features = layer0.get("features", {}) if layer0 else {}

    prompt = f"""
You are a cybersecurity expert analyzing fraud risk. Based on the provided signals and content, provide an independent fraud risk assessment.

--- MESSAGE CONTENT ---
{text}

--- EXTRACTED FEATURES (Layer 0) ---
- Entity Count: {features.get('entity_count', 'N/A')}
- Link Count: {features.get('link_count', 'N/A')}
- Urgency Keywords: {features.get('urgency_keywords', [])}
- Request Type: {features.get('request_type', 'N/A')}
- Contains Credential Request: {features.get('credential_request', False)}

--- HEURISTIC SIGNALS (Layer 1) ---
- Detected Flags: {flags}
- Heuristic Score: {heuristic_score}/100
- Heuristic Confidence: {heuristic_confidence}

--- ML MODEL SIGNALS (Layer 2) ---
- ML Text Score: {ml_text_score}/100
- ML Text Confidence: {ml_text_confidence}
- URL ML Score: {url_ml_score}/100
- Deepfake Detection Score: {deepfake_score}/100

--- TASK ---
Analyze this message and provide your independent fraud risk assessment. Consider:
1. Content characteristics and language patterns
2. Alignment/disagreement with Layer 1 heuristics
3. Consistency with Layer 2 ML signals
4. Your domain expertise in fraud detection

Return ONLY a JSON object with:
{{
    "llm_score": <0-100 fraud risk score based on your analysis>,
    "confidence": <0.0-1.0 confidence in your assessment>,
    "reasoning": "<brief explanation of your scoring>"
}}

Do not include any other text. Only the JSON object.
"""

    return prompt


def parse_llm_response(response_text):
    """
    Extract JSON from LLM response and validate scores.
    Returns dict with llm_score, llm_confidence, reasoning
    """
    try:
        # Try to extract JSON from response (in case LLM adds extra text)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)

            # Handle error responses from Ollama client
            if "error" in result:
                return {
                    "llm_score": result.get("llm_score", 50),
                    "llm_confidence": result.get("confidence", 0.3),
                    "reasoning": result.get("reasoning", "LLM service unavailable")
                }

            # Validate and normalize normal responses
            llm_score = float(result.get("llm_score", 50))
            confidence = float(result.get("confidence", 0.5))
            reasoning = str(result.get("reasoning", ""))

            # Clamp values
            llm_score = max(0, min(100, llm_score))
            confidence = max(0.0, min(1.0, confidence))

            return {
                "llm_score": llm_score,
                "llm_confidence": confidence,
                "reasoning": reasoning
            }
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback if parsing fails
    return {
        "llm_score": 50.0,
        "llm_confidence": 0.3,
        "reasoning": "LLM scoring failed, using neutral score"
    }


def run_llm_scorer(text, layer0=None, layer1=None, layer2=None):
    """
    Layer 3 Part 1: Independent LLM-based fraud scoring

    Args:
        text: clean text content to analyze
        layer0: dict with privacy/feature outputs
        layer1: dict with heuristic outputs
        layer2: dict with ML model outputs

    Returns:
        dict with llm_score, llm_confidence, reasoning
    """

    print("[*] Generating LLM fraud score...")
    prompt = build_scoring_prompt(text, layer0, layer1, layer2)

    # Call LLM
    response = call_ollama(prompt)

    print(f"[*] LLM Scorer Response: {response[:200]}...")

    # Parse response
    result = parse_llm_response(response)

    print(f"[✓] LLM score: {result.get('llm_score')}, confidence: {result.get('llm_confidence')}")

    return result
