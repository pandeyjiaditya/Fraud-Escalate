"""
STRICT JSON PIPELINE - Single JSON file flows through all layers
Each layer receives JSON -> processes -> updates JSON -> passes forward
"""

from .ollama_client import call_ollama
import json
import re


# ============================================================================
# STEP 1: Initialize Pipeline JSON
# ============================================================================
def initialize_pipeline_json(input_content):
    """
    Create the initial JSON that will flow through entire pipeline.
    This is the SINGLE SOURCE OF TRUTH for the entire analysis.
    """
    return {
        "input_content": input_content,
        "layer_1": {
            "score": None,
            "confidence": None,
            "keywords": []
        },
        "layer_2": {
            "score": None,
            "confidence": None,
            "keywords": None
        },
        "layer_3": {
            "score": None,
            "confidence": None,
            "reasoning": None
        },
        "final_score": None,
        "final_summary": None
    }


# ============================================================================
# STEP 2: Layer 1 (Heuristics) - Updates pipeline_json with layer_1 data
# ============================================================================
def run_layer1_heuristics(pipeline_json, layer0_output):
    """
    Layer 1 receives JSON -> processes heuristics -> updates layer_1 in JSON -> returns JSON

    Args:
        pipeline_json: The flowing JSON pipeline
        layer0_output: Clean text and features from layer 0

    Returns:
        Updated pipeline_json with layer_1 filled
    """
    # Import Layer 1 logic
    from layer1_heuristics.heuristic_engine import run_heuristics

    print("[*] LAYER 1: Running heuristics...")

    # Call heuristic engine
    layer1_result = run_heuristics(layer0_output)

    # Update JSON with layer_1 data
    pipeline_json["layer_1"]["score"] = layer1_result.get("heuristic_score", 0)
    pipeline_json["layer_1"]["confidence"] = layer1_result.get("confidence", 0)
    pipeline_json["layer_1"]["keywords"] = layer1_result.get("flags", [])

    print(f"[✓] Layer 1 -> Score: {pipeline_json['layer_1']['score']}, Keywords: {pipeline_json['layer_1']['keywords']}")

    return pipeline_json


# ============================================================================
# STEP 3: Layer 2 (ML) - Updates pipeline_json with layer_2 data
# ============================================================================
def run_layer2_ml(pipeline_json, layer0_output):
    """
    Layer 2 receives JSON -> processes ML -> updates layer_2 in JSON -> returns JSON

    Args:
        pipeline_json: The flowing JSON pipeline
        layer0_output: Clean text and features from layer 0

    Returns:
        Updated pipeline_json with layer_2 filled
    """
    # Import Layer 2 logic
    from layer2_ml.ml_engine import run_ml_model

    print("[*] LAYER 2: Running ML model...")

    # Call ML engine
    layer2_result = run_ml_model(layer0_output)

    # Update JSON with layer_2 data
    pipeline_json["layer_2"]["score"] = layer2_result.get("ml_text_score", 0)
    pipeline_json["layer_2"]["confidence"] = layer2_result.get("ml_text_confidence", 0)
    pipeline_json["layer_2"]["keywords"] = layer2_result.get("ml_prediction", "unknown")

    print(f"[✓] Layer 2 -> Score: {pipeline_json['layer_2']['score']}, Prediction: {pipeline_json['layer_2']['keywords']}")

    return pipeline_json


# ============================================================================
# STEP 4: Layer 3 FIRST CALL (LLM Reasoning) - Updates pipeline_json with layer_3 data
# ============================================================================
def build_layer3_reasoning_prompt(pipeline_json):
    """Build prompt for LLM with full pipeline context"""
    prompt = f"""
You are a cybersecurity expert analyzing fraud/phishing risk.

CONTENT TO ANALYZE:
{pipeline_json.get('input_content', '')}

LAYER 1 (Heuristics) Score: {pipeline_json['layer_1'].get('score', 0)}/100
Layer 1 Keywords: {pipeline_json['layer_1'].get('keywords', [])}
Layer 1 Confidence: {pipeline_json['layer_1'].get('confidence', 0)}

LAYER 2 (ML Model) Score: {pipeline_json['layer_2'].get('score', 0)}/100
Layer 2 Prediction: {pipeline_json['layer_2'].get('keywords', 'unknown')}
Layer 2 Confidence: {pipeline_json['layer_2'].get('confidence', 0)}

TASK:
Generate your independent fraud risk assessment:
1. Analyze the content and all layer signals
2. Provide your own score (0-100)
3. Provide confidence (0.0-1.0) using these criteria:
   - HIGH CONFIDENCE (0.80-1.0): Multiple layers agree, strong fraud indicators, clear patterns
   - MODERATE-HIGH CONFIDENCE (0.65-0.80): Layers mostly agree, some negative indicators present
   - MODERATE CONFIDENCE (0.50-0.65): Mixed signals, unclear indicators, needs review
   - LOW CONFIDENCE (0.30-0.50): Conflicting signals, unclear intent, requires manual review
   - VERY LOW (<0.30): Insufficient data or completely benign
4. Provide detailed reasoning of fraud indicators

CONFIDENCE BOOSTERS:
- If 2+ layers agree on fraud → boost confidence to 0.75+
- If multiple strong keywords present → boost confidence to 0.80+
- If Layer 1 or Layer 2 has high confidence → adopt similar confidence
- If all layers strongly agree → confidence should be 0.85+

Return ONLY valid JSON with NO additional text:
{{
    "score": <0-100>,
    "confidence": <0.0-1.0>,
    "reasoning": "<detailed analysis>"
}}
"""
    return prompt


def parse_llm_layer3_response(response_text):
    """Extract JSON from LLM response"""
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
    except Exception as e:
        print(f"[!] Failed to parse Layer 3 response: {e}")
    return None


def boost_confidence_by_agreement(pipeline_json, llm_confidence):
    """
    ✅ BOOST CONFIDENCE based on agreement between layers

    If multiple layers agree on fraud/safe decision, increase confidence
    """
    l1_score = pipeline_json['layer_1'].get('score', 0)
    l2_score = pipeline_json['layer_2'].get('score', 0)
    l3_score = pipeline_json['layer_3'].get('score', 0)

    l1_conf = pipeline_json['layer_1'].get('confidence', 0)
    l2_conf = pipeline_json['layer_2'].get('confidence', 0)

    # Determine consensus
    fraud_votes = sum([
        1 for score in [l1_score, l2_score, l3_score] if score >= 50
    ])

    # Boost if consensus exists
    if fraud_votes >= 2:  # At least 2 layers agree on fraud
        llm_confidence = min(llm_confidence + 0.15, 1.0)
        print(f"[✓] Boosted confidence by agreement: {llm_confidence}")
    elif fraud_votes == 0:  # All agree it's safe
        llm_confidence = min(llm_confidence + 0.10, 1.0)
        print(f"[✓] Boosted confidence by safe agreement: {llm_confidence}")

    # Also boost if L1 or L2 have high confidence
    if l1_conf >= 0.75 or l2_conf >= 0.75:
        llm_confidence = min(llm_confidence + 0.10, 1.0)
        print(f"[✓] Boosted confidence by high layer confidence: {llm_confidence}")

    return round(llm_confidence, 2)


def run_layer3_reasoning(pipeline_json):
    """
    Layer 3 FIRST LLM CALL receives JSON -> processes with LLM -> updates layer_3 in JSON -> returns JSON

    Args:
        pipeline_json: The flowing JSON pipeline with layer_1 and layer_2 filled

    Returns:
        Updated pipeline_json with layer_3 filled
    """
    print("[*] LAYER 3 (LLM CALL 1): Generating reasoning...")

    prompt = build_layer3_reasoning_prompt(pipeline_json)
    response = call_ollama(prompt)

    print(f"[*] LLM Response: {response[:200]}...")

    result = parse_llm_layer3_response(response)

    if result is None:
        # ✅ IMPROVED FALLBACK: Boost confidence from 0.3 to 0.5
        pipeline_json["layer_3"]["score"] = 50.0
        pipeline_json["layer_3"]["confidence"] = 0.50  # Increased from 0.3
        pipeline_json["layer_3"]["reasoning"] = "Unable to generate reasoning"
        return pipeline_json

    # Update JSON with layer_3 data
    pipeline_json["layer_3"]["score"] = result.get("score", 50.0)
    llm_confidence = result.get("confidence", 0.50)  # Improved default from 0.3

    # ✅ Boost confidence based on layer agreement
    llm_confidence = boost_confidence_by_agreement(pipeline_json, llm_confidence)

    pipeline_json["layer_3"]["confidence"] = llm_confidence
    pipeline_json["layer_3"]["reasoning"] = result.get("reasoning", "")

    print(f"[✓] Layer 3 -> Score: {pipeline_json['layer_3']['score']}, Confidence: {pipeline_json['layer_3']['confidence']}")

    return pipeline_json


# ============================================================================
# STEP 5: Risk Scoring (NO LLM) - Updates pipeline_json with final_score
# ============================================================================
def calculate_final_score(pipeline_json):
    """
    Risk scoring receives JSON -> calculates aggregate score -> updates final_score in JSON -> returns JSON

    Weights: Layer1=0.35, Layer2=0.35, Layer3=0.3

    Args:
        pipeline_json: The flowing JSON pipeline with all 3 layers filled

    Returns:
        Updated pipeline_json with final_score filled
    """
    print("[*] RISK SCORING: Aggregating all layer scores...")

    score_1 = pipeline_json.get("layer_1", {}).get("score", 0)
    score_2 = pipeline_json.get("layer_2", {}).get("score", 0)
    score_3 = pipeline_json.get("layer_3", {}).get("score", 0)

    # Weighted aggregation
    final_score = (0.35 * score_1) + (0.35 * score_2) + (0.3 * score_3)
    final_score = round(final_score, 1)

    # Update JSON with final_score
    pipeline_json["final_score"] = final_score

    print(f"[✓] Final Score: {final_score} (L1: {score_1}, L2: {score_2}, L3: {score_3})")

    return pipeline_json


# ============================================================================
# STEP 6: Layer 3 SECOND CALL (LLM Summary) - Updates pipeline_json with final_summary
# ============================================================================
def build_final_summary_prompt(pipeline_json):
    """Build prompt for final LLM summary with full analysis results"""
    prompt = f"""
You are a cybersecurity expert. Provide a SINGLE comprehensive explanation based on all analysis layers.

ANALYSIS RESULTS:
- Layer 1 (Heuristics): {pipeline_json['layer_1'].get('score', 0)}/100 (Confidence: {pipeline_json['layer_1'].get('confidence', 0)})
- Layer 2 (ML Model): {pipeline_json['layer_2'].get('score', 0)}/100 (Confidence: {pipeline_json['layer_2'].get('confidence', 0)})
- Layer 3 (LLM Analysis): {pipeline_json['layer_3'].get('score', 0)}/100 (Confidence: {pipeline_json['layer_3'].get('confidence', 0)})
- FINAL RISK SCORE: {pipeline_json.get('final_score', 0)}/100

Layer 1 Detection Keywords: {pipeline_json['layer_1'].get('keywords', [])}
Layer 2 ML Prediction: {pipeline_json['layer_2'].get('keywords', 'unknown')}
Layer 3 Reasoning: {pipeline_json['layer_3'].get('reasoning', '')}

TASK:
Generate a clear, professional explanation (3-5 sentences) that:
1. States the FINAL SCORE and risk level
2. Explains contributions from each layer
3. Describes overall fraud risk
4. Provides actionable recommendation

Return ONLY valid JSON with NO additional text:
{{
    "summary": "<comprehensive explanation>"
}}
"""
    return prompt


def parse_llm_summary_response(response_text):
    """Extract JSON from LLM response"""
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
    except Exception as e:
        print(f"[!] Failed to parse summary response: {e}")
    return None


def run_final_summary(pipeline_json):
    """
    Layer 3 SECOND LLM CALL receives JSON -> generates summary -> updates final_summary in JSON -> returns JSON

    Args:
        pipeline_json: Complete JSON with all scores calculated

    Returns:
        Updated pipeline_json with final_summary filled
    """
    print("[*] LAYER 3 (LLM CALL 2): Generating final summary...")

    prompt = build_final_summary_prompt(pipeline_json)
    response = call_ollama(prompt)

    print(f"[*] LLM Summary Response: {response[:200]}...")

    result = parse_llm_summary_response(response)

    if result is None or not result.get("summary"):
        # ✅ IMPROVED FALLBACK: Better default summary with higher confidence
        final_score = pipeline_json.get('final_score', 0)
        risk_level = "HIGH" if final_score >= 70 else "MEDIUM" if final_score >= 40 else "LOW"
        pipeline_json["final_summary"] = (
            f"Final Risk Score: {final_score}/100 ({risk_level} risk). "
            f"Analysis complete across all layers (Layer 1: {pipeline_json['layer_1'].get('score', 0)}/100, "
            f"Layer 2: {pipeline_json['layer_2'].get('score', 0)}/100, "
            f"Layer 3: {pipeline_json['layer_3'].get('score', 0)}/100). "
            f"Recommendation: {('Block this content' if final_score >= 70 else 'Review manually' if final_score >= 40 else 'Content appears safe')}."
        )
        return pipeline_json

    # Update JSON with final_summary
    pipeline_json["final_summary"] = result.get("summary", "")

    print(f"[✓] Layer 3 Summary generated")

    return pipeline_json


# ============================================================================
# STEP 7: Convert Final JSON to Response Format
# ============================================================================
def convert_pipeline_to_response(pipeline_json, layer0_output, layer1_output, layer2_output, input_data, context_type):
    """
    Convert the final pipeline JSON to frontend response format.

    This extracts data from the single JSON pipeline and formats for frontend.
    """

    layer_1 = pipeline_json.get("layer_1", {})
    layer_2 = pipeline_json.get("layer_2", {})
    layer_3 = pipeline_json.get("layer_3", {})
    final_score = pipeline_json.get("final_score", 0)

    # Determine decision based on final_score
    if final_score >= 70:
        decision = "BLOCK"
        risk_level = "HIGH"
        risk_color = "red"
    elif final_score >= 40:
        decision = "REVIEW"
        risk_level = "MEDIUM"
        risk_color = "orange"
    else:
        decision = "SAFE"
        risk_level = "LOW"
        risk_color = "green"

    # Calculate final confidence (weighted average)
    l1_conf = layer_1.get("confidence", 0)
    l2_conf = layer_2.get("confidence", 0)
    l3_conf = layer_3.get("confidence", 0)
    final_confidence = round((0.35 * l1_conf) + (0.35 * l2_conf) + (0.3 * l3_conf), 2)

    final_output = {
        "risk_score": final_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "decision": decision,
        "confidence": final_confidence,
        "context_type": context_type
    }

    # Build response with all layer data
    return {
        "input": input_data,
        "layer0": layer0_output,
        "layer1": {
            "heuristic_score": layer_1.get("score", 0),
            "confidence": layer_1.get("confidence", 0),
            "flags": layer_1.get("keywords", [])
        },
        "layer1_reasoning": {
            "flag_analysis": {flag: "detected" for flag in layer_1.get("keywords", [])},
            "overall_assessment": f"Heuristic score: {layer_1.get('score', 0)}/100"
        },
        "layer2": {
            "ml_text_score": layer_2.get("score", 0),
            "ml_text_confidence": layer_2.get("confidence", 0),
            "ml_prediction": layer_2.get("keywords", "unknown")
        },
        "layer2_reasoning": {
            "text_analysis": layer2_output.get("reasoning", ""),
            "ml_patterns_detected": [],
            "comparison_with_heuristics": f"ML score: {layer_2.get('score', 0)}/100 vs Heuristic: {layer_1.get('score', 0)}/100",
            "risk_level": "high" if layer_2.get("score", 0) >= 70 else "medium" if layer_2.get("score", 0) >= 40 else "low"
        },
        "layer3_scoring": {
            "llm_score": layer_3.get("score", 0),
            "llm_confidence": layer_3.get("confidence", 0),
            "reasoning": layer_3.get("reasoning", ""),
            "layer_1_score": layer_1.get("score", 0),
            "layer_2_score": layer_2.get("score", 0),
            "layer_3_score": layer_3.get("score", 0),
            "final_score": final_score
        },
        "layer3_explanation": {
            "explanation": pipeline_json.get("final_summary", ""),
            "confidence": final_confidence
        },
        "final": final_output
    }
