from .prompt_builder import build_prompt_explanation
from .ollama_client import call_ollama


def calculate_llm_confidence(explanation, final):

    score = final.get("risk_score", 0)

    base = score / 100

    length_factor = min(len(explanation) / 200, 0.2)

    return round(min(base + length_factor, 1.0), 2)


def run_llm_explanation(text, layer0, layer1, layer2, layer3_scoring, final):
    """
    Layer 3 Part 2: LLM-based explanation of final fraud decision

    Args:
        text: clean text content
        layer0: dict with privacy/features
        layer1: dict with heuristic outputs
        layer2: dict with ML model outputs
        layer3_scoring: dict with LLM scoring (llm_score, llm_confidence, reasoning)
        final: dict with final risk score and decision from Risk Engine

    Returns:
        dict with explanation and confidence
    """

    prompt = build_prompt_explanation(text, layer0, layer1, layer2, layer3_scoring, final)

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
    layer3_scoring = {"llm_score": 0, "llm_confidence": 0, "reasoning": ""}
    return run_llm_explanation(text, layer0, layer1, layer2, layer3_scoring, final)