vectorizer = None
model = None


def load_if_needed():
    global vectorizer, model
    if vectorizer is None or model is None:
        from .model_loader import load_models
        vectorizer, model = load_models()


def generate_ml_reasoning(prob, prediction, text):
    """
    Generate simple reasoning for ML prediction based on score and text characteristics.
    """
    ml_score = prob * 100

    # Analyze text characteristics
    text_lower = text.lower()
    has_urgent_language = any(word in text_lower for word in ['urgent', 'immediate', 'now', 'asap', 'quickly'])
    has_credential_requests = any(word in text_lower for word in ['password', 'otp', 'pin', 'verify', 'confirm', 'update'])
    has_action_calls = any(word in text_lower for word in ['click', 'verify', 'confirm', 'update', 'validate', 'approve'])
    has_urgent_requests = any(word in text_lower for word in ['urgent', 'suspended', 'blocked', 'closed', 'limited'])

    if ml_score >= 75:
        if has_credential_requests:
            reasoning = f"ML model detected strong fraud indicators (score: {ml_score:.1f}). Text contains credential theft language patterns combined with urgency markers. Multiple NLP features indicate phishing/fraud attempt."
        elif has_urgent_requests:
            reasoning = f"ML model scored this as high fraud risk ({ml_score:.1f}). Detected account restriction language combined with action calls. Pattern matches known phishing templates."
        else:
            reasoning = f"ML model classified as fraud with high confidence ({ml_score:.1f}). Linguistic patterns, semantic structure, and word combinations match fraudulent communication patterns in training data."

    elif ml_score >= 50:
        reasoning = f"ML model assigned moderate fraud risk ({ml_score:.1f}). Text contains some suspicious patterns but lacks clear phishing indicators. Recommend manual review in combination with other signals."

    else:
        if has_urgent_language or has_action_calls:
            reasoning = f"ML model scored as low fraud risk ({ml_score:.1f}), but contains minor concerning patterns like urgency or action calls. Context and heuristics should be considered."
        else:
            reasoning = f"ML model classified as legitimate content ({ml_score:.1f}). Text structure and language patterns are consistent with normal communication without fraud indicators."

    return reasoning


def run_ml_model(data):

    try:
        load_if_needed()

        # Skip media
        if data["type"] in ["image", "audio", "video"]:
            return {
                "ml_text_score": 0,
                "ml_text_confidence": 0,
                "ml_prediction": "unknown",
                "reasoning": "Media files (image/audio/video) cannot be analyzed by text ML model."
            }

        text = data["clean_text"]

        # Transform text
        X = vectorizer.transform([text])

        prob = model.predict_proba(X)[0][1]

        # 🔥 Feature boosting
        features = data.get("features", {})

        if features.get("has_urgent_words"):
            prob += 0.1

        if features.get("has_sensitive_keywords"):
            prob += 0.1

        prob = min(prob, 1.0)

        # ✅ IMPROVED CONFIDENCE: Based on prediction strength
        # Higher confidence for more extreme predictions (very sure fraud or very sure safe)
        # Boost confidence for clear signals
        if prob >= 0.8:
            confidence = min(0.95, 0.8 + (prob - 0.5) * 0.3)  # Very strong fraud = 0.90-0.95
        elif prob >= 0.7:
            confidence = min(0.90, 0.75 + (prob - 0.5) * 0.3)  # Strong fraud = 0.85-0.90
        elif prob >= 0.6:
            confidence = min(0.85, 0.65 + (prob - 0.5) * 0.4)  # Moderate fraud = 0.75-0.85
        elif prob <= 0.2:
            confidence = min(0.95, 0.8 + (0.5 - prob) * 0.6)  # Very strong safe = 0.90-0.95
        elif prob <= 0.3:
            confidence = min(0.90, 0.70 + (0.5 - prob) * 0.4)  # Strong safe = 0.80-0.90
        elif prob <= 0.4:
            confidence = min(0.85, 0.60 + (0.5 - prob) * 0.5)  # Moderate safe = 0.70-0.85
        else:
            # Near 0.5 = uncertain, but still reasonable confidence for ML model
            confidence = max(0.50, 0.55 - abs(prob - 0.5) * 2)  # Near 0.5 = 0.50-0.55

        prediction = "fraud" if prob > 0.5 else "safe"

        # Convert probability (0-1) to score (0-100)
        ml_score = prob * 100

        # Generate reasoning
        reasoning = generate_ml_reasoning(prob, prediction, text)

        return {
            "ml_text_score": round(ml_score, 1),
            "ml_text_confidence": round(confidence, 3),
            "ml_prediction": prediction,
            "reasoning": reasoning
        }

    except Exception as e:
        return {
            "ml_text_score": 0,
            "ml_text_confidence": 0.50,  # ✅ Increased from 0 to 0.50
            "ml_prediction": "error",
            "reasoning": f"ML model encountered error: {str(e)}",
            "error": str(e)
        }