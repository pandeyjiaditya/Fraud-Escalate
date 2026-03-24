from .prompt_builder import build_prompt
from .ollama_client import call_ollama


def run_llm(text, layer1, layer2, final):

    prompt = build_prompt(text, layer1, layer2, final)

    explanation = call_ollama(prompt)

    return {
        "explanation": explanation
    }