def build_prompt(text, layer1, layer2, final):

    flags = layer1.get("flags", [])
    score = final.get("risk_score", 0)
    decision = final.get("decision", "")

    prompt = f"""
You are a cybersecurity expert.

Analyze the following message and explain why it is fraud or safe.

Message:
{text}

Detected Signals:
- Flags: {flags}
- Risk Score: {score}
- Decision: {decision}

Give a short explanation in 2-3 lines.
"""

    return prompt