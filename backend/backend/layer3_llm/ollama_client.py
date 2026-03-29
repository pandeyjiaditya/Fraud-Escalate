import requests

OLLAMA_URL = "http://localhost:11434/api/chat"


def call_ollama(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "mistral",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
    )

    return response.json()["message"]["content"]