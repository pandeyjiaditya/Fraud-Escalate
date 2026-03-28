from .ollama_client import call_ollama
import json
import re


def build_layer1_reasoning_prompt(text, layer1_output):
    """
    Build prompt for LLM to generate reasoning for Layer 1 heuristic flags.

    Args:
        text: clean message text
        layer1_output: dict with flags and heuristic_score
    """
    flags = layer1_output.get("flags", [])
    score = layer1_output.get("heuristic_score", 0)

    flags_description = {
        "urgency": "The message contains urgent/time-critical language (e.g., 'immediate', 'urgent', 'now')",
        "credential_theft": "The message requests sensitive credentials (e.g., OTP, password, account details)",
        "suspicious_url": "The message contains suspicious URLs or links (http/https detected)",
        "financial_intent": "The message targets financial accounts or banking (e.g., 'bank', 'account')",
        "strong_phishing": "The message contains strong phishing indicators (e.g., 'suspended', 'blocked', 'verify')"
    }

    flags_info = "\n".join([f"- {flag}: {flags_description.get(flag, flag)}" for flag in flags])

    prompt = f"""
You are a cybersecurity analyst explaining fraud detection heuristics.

--- MESSAGE CONTENT ---
{text}

--- LAYER 1 HEURISTIC FLAGS DETECTED ---
{flags_info}
Overall Heuristic Score: {score}/100

--- TASK ---
Analyze the message and provide a brief explanation for each detected flag. For each flag, explain:
1. The specific evidence in the message
2. Why this indicates potential fraud/phishing
3. The risk level (low/medium/high)

Return ONLY a JSON object with:
{{
    "flag_analysis": {{
        "<flag_name>": "<explanation of why this flag was triggered and its risk>",
        ...
    }},
    "overall_assessment": "<2-3 sentence summary of the heuristic findings>"
}}

Example:
{{
    "flag_analysis": {{
        "urgency": "The message uses 'immediate action required' which creates artificial time pressure - a common phishing tactic (HIGH RISK)",
        "credential_theft": "Directly requests password verification - legitimate services never ask for passwords (HIGH RISK)"
    }},
    "overall_assessment": "Multiple high-risk indicators detected indicating probable phishing attempt targeting credential theft."
}}

Do not include any other text. Only the JSON object.
"""

    return prompt


def build_layer2_reasoning_prompt(text, layer1_output, layer2_output):
    """
    Build prompt for LLM to generate reasoning for Layer 2 ML predictions.

    Args:
        text: clean message text
        layer1_output: Layer 1 output for context
        layer2_output: dict with ML predictions and scores
    """
    ml_text_score = layer2_output.get("ml_text_score", 0)
    ml_text_confidence = layer2_output.get("ml_text_confidence", 0)
    url_ml_score = layer2_output.get("url_ml_score", 0)
    deepfake_score = layer2_output.get("deepfake_score", 0)
    ml_prediction = layer2_output.get("ml_prediction", "unknown")

    layer1_flags = layer1_output.get("flags", []) if layer1_output else []

    prompt = f"""
You are an ML fraud detection expert explaining machine learning model predictions.

--- MESSAGE CONTENT ---
{text}

--- LAYER 1 CONTEXT (HEURISTICS) ---
Previous Heuristic Flags: {layer1_flags}

--- LAYER 2 ML MODEL PREDICTIONS ---
- Text Classification Score: {ml_text_score}/100
- Text Prediction: {ml_prediction}
- ML Confidence: {ml_text_confidence}
- URL ML Score: {url_ml_score}/100
- Deepfake Detection Score: {deepfake_score}/100

--- TASK ---
Analyze the message and ML predictions. Explain:
1. Why the text classifier assigned this score
2. What linguistic/content patterns indicate fraud (or legitimate)
3. Relationship with Layer 1 heuristic flags (agreement/disagreement)
4. Additional ML model insights (language sophistication, mimicry level, etc.)

Return ONLY a JSON object with:
{{
    "text_analysis": "<explanation of ML text score and prediction>",
    "ml_patterns_detected": ["<pattern 1>", "<pattern 2>", ...],
    "comparison_with_heuristics": "<how ML findings align or differ from Layer 1>",
    "risk_level": "<low/medium/high based on ML signals>",
    "model_confidence_assessment": "<assessment of ML confidence level>"
}}

Do not include any other text. Only the JSON object.
"""

    return prompt


def parse_layer_reasoning_response(response_text):
    """
    Extract JSON from LLM reasoning response.
    Handles both normal LLM responses and fallback error responses.
    """
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)

            # Return result as-is, whether it's an error response or normal response
            return result
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[!] Failed to parse layer reasoning response: {e}")

    # Fallback if parsing completely fails
    return {
        "error": "Failed to parse LLM reasoning",
        "flag_analysis": {},
        "overall_assessment": "Error parsing LLM response",
        "text_analysis": "Error parsing LLM response",
        "ml_patterns_detected": [],
        "comparison_with_heuristics": "",
        "risk_level": "unknown"
    }


def run_layer1_reasoning(text, layer1_output):
    """
    Layer 3: Generate LLM reasoning for Layer 1 heuristic flags.

    Args:
        text: clean text content
        layer1_output: Layer 1 heuristic output with flags

    Returns:
        dict with flag_analysis and overall_assessment
    """
    if not layer1_output.get("flags"):
        return {
            "flag_analysis": {},
            "overall_assessment": "No heuristic flags detected."
        }

    print("[*] Generating Layer 1 reasoning...")
    prompt = build_layer1_reasoning_prompt(text, layer1_output)
    response = call_ollama(prompt)

    print(f"[*] Layer 1 LLM Response: {response[:200]}...")
    result = parse_layer_reasoning_response(response)
    print(f"[✓] Layer 1 reasoning parsed: {bool(result)}")

    return result


def run_layer2_reasoning(text, layer1_output, layer2_output):
    """
    Layer 3: Generate LLM reasoning for Layer 2 ML predictions.

    Args:
        text: clean text content
        layer1_output: Layer 1 output for context
        layer2_output: Layer 2 ML output with predictions

    Returns:
        dict with ML analysis and patterns
    """
    print("[*] Generating Layer 2 reasoning...")
    prompt = build_layer2_reasoning_prompt(text, layer1_output, layer2_output)
    response = call_ollama(prompt)

    print(f"[*] Layer 2 LLM Response: {response[:200]}...")
    result = parse_layer_reasoning_response(response)
    print(f"[✓] Layer 2 reasoning parsed: {bool(result)}")

    return result
