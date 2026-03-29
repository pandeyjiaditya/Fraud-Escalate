from .prompt_builder import build_prompt_explanation
from .ollama_client import call_ollama


def calculate_llm_confidence(explanation, final):

    score = final.get("risk_score", 0)

    base = score / 100

    length_factor = min(len(explanation) / 200, 0.2)

    return round(min(base + length_factor, 1.0), 2)


def run_llm_explanation(text, layer0, layer1, layer2, layer3_scoring, final):
    """
    Layer 3 Part 2 - SECOND & FINAL LLM CALL:

    Generates final user-facing summary that explains the combined analysis and decision.

    Args:
        text: clean text content
        layer0: dict with privacy/features
        layer1: dict with heuristic outputs
        layer2: dict with ML model outputs
        layer3_scoring: dict with Layer 3 LLM scoring results:
            - summary_1: explanation of heuristic findings
            - summary_2: explanation of ML findings
            - score_3: LLM's fraud risk score
            - confidence_3: confidence
        final: dict with final risk score and decision from Risk Engine

    Returns:
        dict with final_summary and confidence
    """

    prompt = build_prompt_explanation(text, layer0, layer1, layer2, layer3_scoring, final)

    # SECOND LLM CALL (only remaining LLM call after refactoring)
    explanation = call_ollama(prompt)

    confidence = calculate_llm_confidence(explanation, final)

    return {
        "explanation": explanation,
        "confidence": confidence
    }


# Backward compatibility - keep old signature but implement new one
def run_llm(text, layer1, layer2, final):
    """Deprecated: Use run_llm_explanation instead"""
    layer0 = {}
    layer3_scoring = {"score_3": 0, "confidence_3": 0, "summary_1": "", "summary_2": ""}
    return run_llm_explanation(text, layer0, layer1, layer2, layer3_scoring, final)