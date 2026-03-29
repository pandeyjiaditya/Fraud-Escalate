"""
Unified JSON Pipeline Orchestrator - Simplified Version
Single explanation based on all layer scores (L1, L2, L3)
"""

from .ollama_client import call_ollama
import json
import re


def build_structured_pipeline(input_content, layer1_output, layer2_output, layer0_output=None):
    """
    Step 3: Build structured JSON that will be the single source of truth.

    This JSON is passed through the pipeline and updated at each stage.
    """
    return {
        "input_content": input_content,
        "layer_1": {
            "score": layer1_output.get("heuristic_score", 0),
            "confidence": layer1_output.get("confidence", 0),
            "keywords": layer1_output.get("flags", [])
        },
        "layer_2": {
            "score": layer2_output.get("ml_text_score", 0),
            "confidence": layer2_output.get("ml_text_confidence", 0),
            "keywords": layer2_output.get("ml_prediction", "unknown")
        },
        "layer_3": {},
        "final_score": None,
        "final_summary": None
    }


def build_layer3_reasoning_prompt(pipeline_json):
    """
    Build prompt for LLM FIRST CALL (Step 4).

    LLM receives ENTIRE structured JSON and must:
    1. Analyze input_content, layer_1 data, layer_2 data
    2. Generate its own score_3
    3. Generate reasoning (will be used in final explanation)
    """

    prompt = f"""
You are a cybersecurity expert analyzing fraud/phishing risk.

CONTENT TO ANALYZE:
{pipeline_json.get('input_content', '')}

LAYER 1 (Heuristics) Score: {pipeline_json['layer_1'].get('score', 0)}/100
Heuristic Keywords Detected: {pipeline_json['layer_1'].get('keywords', [])}

LAYER 2 (ML Model) Score: {pipeline_json['layer_2'].get('score', 0)}/100
ML Prediction: {pipeline_json['layer_2'].get('keywords', 'unknown')}

TASK:
Generate your independent fraud risk assessment:
1. Analyze the content and layer signals
2. Provide your own score (0-100)
3. Provide confidence (0.0-1.0)
4. Provide detailed reasoning of what fraud indicators you see

Return ONLY valid JSON:
{{
    "input_content": "{pipeline_json.get('input_content', '')}",
    "layer_1": {json.dumps(pipeline_json.get('layer_1', {}))},
    "layer_2": {json.dumps(pipeline_json.get('layer_2', {}))},
    "layer_3": {{
        "score": <0-100>,
        "confidence": <0.0-1.0>,
        "reasoning": "<detailed analysis of fraud indicators detected>"
    }},
    "final_score": null,
    "final_summary": null
}}

Do NOT modify layer_1 or layer_2. Only fill in layer_3.
Do NOT include any text outside the JSON.
"""

    return prompt


def parse_layer3_response(response_text):
    """
    Extract updated JSON from LLM Layer 3 response.
    """
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            return result
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[!] Failed to parse layer 3 response: {e}")

    return None


def run_layer3_reasoning(pipeline_json):
    """
    Step 4: FIRST LLM CALL

    LLM takes structured JSON and fills layer_3 with score and reasoning.

    Args:
        pipeline_json: Structured JSON with layer_1 and layer_2 filled

    Returns:
        Updated pipeline_json with layer_3 filled
    """

    print("[*] Layer 3 (FIRST LLM CALL): Generating score and reasoning...")

    prompt = build_layer3_reasoning_prompt(pipeline_json)
    response = call_ollama(prompt)

    print(f"[*] Layer 3 LLM Response: {response[:300]}...")

    updated_json = parse_layer3_response(response)

    if updated_json is None:
        # Fallback
        pipeline_json["layer_3"] = {
            "score": 50.0,
            "confidence": 0.3,
            "reasoning": "Unable to generate reasoning"
        }
        return pipeline_json

    return updated_json


def calculate_final_score(pipeline_json):
    """
    Step 5: Scoring Engine (NO LLM)

    Aggregate scores from all three layers into final_score.
    Weights: L1=0.35, L2=0.35, L3=0.3

    Args:
        pipeline_json: JSON with layer_1, layer_2, layer_3 filled

    Returns:
        Updated pipeline_json with final_score filled
    """

    print("[*] Step 5: Aggregating scores...")

    score_1 = pipeline_json.get("layer_1", {}).get("score", 0)
    score_2 = pipeline_json.get("layer_2", {}).get("score", 0)
    score_3 = pipeline_json.get("layer_3", {}).get("score", 0)

    # Weighted aggregation
    final_score = (0.35 * score_1) + (0.35 * score_2) + (0.3 * score_3)
    final_score = round(final_score, 1)

    pipeline_json["final_score"] = final_score

    print(f"[✓] Final score calculated: {final_score} (L1: {score_1}, L2: {score_2}, L3: {score_3})")

    return pipeline_json


def build_final_summary_prompt(pipeline_json):
    """
    Build prompt for LLM SECOND CALL (Step 6).

    LLM generates explanation based on ALL layer scores and final score.
    """

    layer_1 = pipeline_json.get("layer_1", {})
    layer_2 = pipeline_json.get("layer_2", {})
    layer_3 = pipeline_json.get("layer_3", {})
    final_score = pipeline_json.get("final_score", 0)

    prompt = f"""
You are a cybersecurity expert. Provide a SINGLE comprehensive explanation based on all layer analysis scores.

ANALYSIS RESULTS:
- Layer 1 (Heuristics) Score: {layer_1.get('score', 0)}/100 | Confidence: {layer_1.get('confidence', 0)}
- Layer 2 (ML Model) Score: {layer_2.get('score', 0)}/100 | Confidence: {layer_2.get('confidence', 0)}
- Layer 3 (LLM Analysis) Score: {layer_3.get('score', 0)}/100 | Confidence: {layer_3.get('confidence', 0)}
- FINAL SCORE: {final_score}/100

Layer 1 Detection: {layer_1.get('keywords', [])}
Layer 2 Prediction: {layer_2.get('keywords', 'unknown')}
Layer 3 Analysis: {layer_3.get('reasoning', '')}

TASK:
Generate a clear, professional explanation (3-5 sentences) that:
1. States the FINAL SCORE and what it means
2. Explains how each layer contributed (Layer 1, Layer 2, Layer 3)
3. Describes overall fraud risk based on ALL signals combined
4. Provides actionable assessment

Return ONLY valid JSON:
{{
    "final_summary": "<comprehensive explanation referencing all three layer scores and final score>"
}}

Do NOT modify any scores. Do NOT include any text outside JSON.
"""

    return prompt


def parse_final_summary_response(response_text):
    """
    Extract updated JSON with final_summary from LLM response.
    """
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            return result
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[!] Failed to parse final summary response: {e}")

    return None


def run_final_summary(pipeline_json):
    """
    Step 6: SECOND & FINAL LLM CALL

    LLM generates final_summary based on all layer scores.

    Args:
        pipeline_json: Complete JSON with all layers and final_score filled

    Returns:
        Updated pipeline_json with final_summary filled
    """

    print("[*] Step 6 (SECOND LLM CALL): Generating final explanation...")

    prompt = build_final_summary_prompt(pipeline_json)
    response = call_ollama(prompt)

    print(f"[*] Final Summary LLM Response: {response[:300]}...")

    updated_json = parse_final_summary_response(response)

    if updated_json is None or not updated_json.get("final_summary"):
        # Fallback summary
        pipeline_json["final_summary"] = (
            f"Analysis complete. Layer 1 Score: {pipeline_json['layer_1'].get('score', 0)}/100, "
            f"Layer 2 Score: {pipeline_json['layer_2'].get('score', 0)}/100, "
            f"Layer 3 Score: {pipeline_json['layer_3'].get('score', 0)}/100. "
            f"Final Risk Score: {pipeline_json.get('final_score', 0)}/100."
        )
        return pipeline_json

    return updated_json


def convert_pipeline_to_response(pipeline_json, layer0_output, layer1_output, layer2_output, input_data, context_type, final_output=None):
    """
    Convert internal JSON pipeline to frontend-compatible response format.
    Includes all layer data + final output from Risk Engine.
    """

    layer_1 = pipeline_json.get("layer_1", {})
    layer_2 = pipeline_json.get("layer_2", {})
    layer_3 = pipeline_json.get("layer_3", {})
    final_score = pipeline_json.get("final_score", 0)

    # If final_output not provided, calculate it
    if final_output is None:
        # Calculate final decision
        if final_score >= 70:
            decision = "BLOCK"
        elif final_score >= 40:
            decision = "REVIEW"
        else:
            decision = "SAFE"

        # Calculate final confidence
        l1_conf = layer_1.get("confidence", 0)
        l2_conf = layer_2.get("confidence", 0)
        l3_conf = layer_3.get("confidence", 0)
        final_confidence = round((0.35 * l1_conf) + (0.35 * l2_conf) + (0.3 * l3_conf), 2)

        # Determine risk level and color
        if final_score >= 70:
            risk_level = "HIGH"
            risk_color = "red"
        elif final_score >= 40:
            risk_level = "MEDIUM"
            risk_color = "orange"
        else:
            risk_level = "LOW"
            risk_color = "green"

        final_output = {
            "risk_score": final_score,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "decision": decision,
            "confidence": final_confidence,
            "context_type": context_type
        }

    return {
        "input": input_data,
        "layer0": layer0_output,
        "layer1": {
            "heuristic_score": layer_1.get("score", 0),
            "confidence": layer_1.get("confidence", 0),
            "flags": layer_1.get("keywords", [])
        },
        "layer2": {
            "ml_text_score": layer_2.get("score", 0),
            "ml_text_confidence": layer_2.get("confidence", 0),
            "ml_prediction": layer_2.get("keywords", "unknown")
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
            "confidence": final_output.get("confidence", 0.5)
        },
        "final": final_output
    }
