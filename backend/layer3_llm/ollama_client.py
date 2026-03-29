import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_TIMEOUT = 60  # 60 second timeout (mistral response time)
OLLAMA_MODEL = "mistral"  # Using mistral model


def call_ollama(prompt):
    """
    Call Ollama LLM with error handling and timeout.
    Returns the LLM response or a fallback response on error.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT
        )

        # Check if request was successful
        if response.status_code != 200:
            print(f"[!] Ollama API error: {response.status_code}")
            print(f"[!] Response: {response.text}")
            return json.dumps({
                "error": f"Ollama API returned {response.status_code}",
                "llm_score": 50,
                "confidence": 0.3,
                "reasoning": "LLM service error"
            })

        # Extract message content
        result = response.json()
        message_content = result.get("message", {}).get("content", "")

        print(f"[+] Ollama response received ({len(message_content)} chars)")
        print(f"[+] Response preview: {message_content[:200]}...")

        return message_content

    except requests.Timeout:
        print("[!] Ollama request timed out (60s)")
        return json.dumps({
            "error": "Ollama timeout",
            "llm_score": 50,
            "confidence": 0.3,
            "reasoning": "LLM response timed out"
        })
    except requests.ConnectionError as e:
        print("[!] Cannot connect to Ollama at http://localhost:11434")
        print(f"[!] Error: {str(e)}")
        print("[!] Make sure Ollama is running: ollama serve")
        return json.dumps({
            "error": "Ollama not running",
            "llm_score": 50,
            "confidence": 0.3,
            "reasoning": "LLM service unavailable - Ollama not running"
        })
    except Exception as e:
        print(f"[!] Ollama error: {str(e)}")
        import traceback
        traceback.print_exc()
        return json.dumps({
            "error": str(e),
            "llm_score": 50,
            "confidence": 0.3,
            "reasoning": f"LLM error: {str(e)}"
        })