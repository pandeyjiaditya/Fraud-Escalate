from datetime import datetime


def calculate_layer0_confidence(features):

    score = 0

    if features.get("has_url"):
        score += 0.2

    if features.get("has_urgent_words"):
        score += 0.2

    if features.get("has_sensitive_keywords"):
        score += 0.3

    if features.get("has_numbers"):
        score += 0.1

    score += min(features.get("length", 0) / 100, 0.2)

    return round(min(score, 1.0), 2)


def process_privacy_layer(data):

    text = data.get("content", "")

    clean_text = text.lower()

    features = {
        "length": len(clean_text),
        "has_url": "http" in clean_text,
        "has_urgent_words": any(word in clean_text for word in ["urgent", "immediately"]),
        "has_sensitive_keywords": any(word in clean_text for word in ["otp", "password", "card"]),
        "has_numbers": any(char.isdigit() for char in clean_text)
    }

    confidence = calculate_layer0_confidence(features)

    return {
        "type": "text",
        "original_text": text,
        "clean_text": clean_text,
        "features": features,
        "confidence": confidence,
        "metadata": {
            "timestamp": str(datetime.now())
        }
    }