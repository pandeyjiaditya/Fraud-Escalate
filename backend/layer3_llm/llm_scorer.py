from .ollama_client import call_ollama
import json
import re


def build_combined_reasoning_prompt(text, layer0, layer1, layer2):
    """
    REFACTORED: Build single LLM prompt for BOTH Layer 1 & Layer 2 analysis + scoring.

    This is the FIRST (and only first) LLM call in the pipeline.

    Args:
        text: raw email text
        layer0: dict with privacy/features
        layer1: dict with heuristic outputs (score_1, confidence_1, keywords_1)
        layer2: dict with ML model outputs (score_2, confidence_2, keywords_2)

    Returns:
        Generator prompt that combines all reasoning + scoring
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
You are a cybersecurity expert analyzing fraud risk across multiple detection layers.

--- MESSAGE CONTENT ---
{text}

--- EXTRACTED FEATURES (Layer 0) ---
- Entity Count: {features.get('entity_count', 'N/A')}
- Link Count: {features.get('link_count', 'N/A')}
- Urgency Keywords: {features.get('urgency_keywords', [])}
- Request Type: {features.get('request_type', 'N/A')}
- Contains Credential Request: {features.get('credential_request', False)}

--- HEURISTIC LAYER (L1) FINDINGS ---
- Detected Flags: {flags}
- Heuristic Score: {heuristic_score}/100
- Confidence: {heuristic_confidence}

--- ML LAYER (L2) FINDINGS ---
- ML Text Score: {ml_text_score}/100
- ML Text Confidence: {ml_text_confidence}
- URL ML Score: {url_ml_score}/100
- Deepfake Detection Score: {deepfake_score}/100

--- TASK ---
You must provide:

1. SUMMARY_1: Explain the Layer 1 heuristic findings:
   - Why each flag was triggered
   - What text evidence supports it
   - Risk level for each indicator

2. SUMMARY_2: Explain the Layer 2 ML findings:
   - Why the ML model scored this way
   - Linguistic/content patterns detected
   - How it aligns/disagrees with heuristics

3. SCORE_3 & CONFIDENCE_3: Your independent fraud risk assessment considering:
   - Content characteristics and language patterns
   - Alignment of L1 and L2 signals
   - Your domain expertise

Return ONLY a JSON object with:
{{
    "summary_1": "<comprehensive explanation of heuristic findings>",
    "summary_2": "<comprehensive explanation of ML findings>",
    "score_3": <0-100 fraud risk score based on your analysis>,
    "confidence_3": <0.0-1.0 confidence in your assessment>
}}

Do not include any other text. Only the JSON object.
"""

    return prompt


def parse_llm_response(response_text):
    """
    Extract JSON from LLM response and validate scores.

    Returns dict with:
    - summary_1 (Layer 1 reasoning)
    - summary_2 (Layer 2 reasoning)
    - score_3 (LLM's independent score)
    - confidence_3 (confidence)
    """
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)

            # Handle error responses
            if "error" in result:
                return {
                    "summary_1": result.get("summary_1", "Error analyzing heuristics"),
                    "summary_2": result.get("summary_2", "Error analyzing ML"),
                    "score_3": result.get("score_3", 50),
                    "confidence_3": result.get("confidence_3", 0.3)
                }

            # Validate and normalize responses
            summary_1 = str(result.get("summary_1", ""))
            summary_2 = str(result.get("summary_2", ""))
            score_3 = float(result.get("score_3", 50))
            confidence_3 = float(result.get("confidence_3", 0.5))

            # Clamp values
            score_3 = max(0, min(100, score_3))
            confidence_3 = max(0.0, min(1.0, confidence_3))

            return {
                "summary_1": summary_1,
                "summary_2": summary_2,
                "score_3": score_3,
                "confidence_3": confidence_3
            }
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback
    return {
        "summary_1": "Unable to analyze heuristics",
        "summary_2": "Unable to analyze ML predictions",
        "score_3": 50.0,
        "confidence_3": 0.3
    }


def run_llm_scorer(text, layer0=None, layer1=None, layer2=None):
    """
    Layer 3 - FIRST LLM CALL (Unified):

    Combines L1 and L2 reasoning + LLM scoring in a SINGLE call.

    Args:
        text: clean text content to analyze
        layer0: dict with privacy/feature outputs
        layer1: dict with heuristic outputs (score_1, confidence_1, flags)
        layer2: dict with ML model outputs (score_2, confidence_2)

    Returns:
        dict with:
        - summary_1: explanation of heuristic findings
        - summary_2: explanation of ML findings
        - score_3: LLM's fraud risk score (0-100)
        - confidence_3: confidence in assessment
    """

    print("[*] Running Layer 3 (UNIFIED): LLM Reasoning + Scoring...")
    prompt = build_combined_reasoning_prompt(text, layer0, layer1, layer2)

    # SINGLE LLM CALL (replaces 3 calls: layer1_reasoning, layer2_reasoning, llm_scorer)
    response = call_ollama(prompt)

    print(f"[*] Layer 3 LLM Response: {response[:200]}...")

    # Parse response
    result = parse_llm_response(response)

    print(f"[✓] LLM score_3: {result.get('score_3')}, confidence_3: {result.get('confidence_3')}")

    return result
