from .prompt_builder import build_prompt
from .ollama_client import call_ollama


def calculate_llm_confidence(explanation, final):

    score = final.get("risk_score", 0)

    base = score / 100

    length_factor = min(len(explanation) / 200, 0.2)

    return round(min(base + length_factor, 1.0), 2)


def run_llm(text, layer1, layer2, final):

    prompt = build_prompt(text, layer1, layer2, final)

    explanation = call_ollama(prompt)

    confidence = calculate_llm_confidence(explanation, final)

    return {
        "explanation": explanation,
        "confidence": confidence
    }