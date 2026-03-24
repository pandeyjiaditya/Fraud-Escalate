vectorizer = None
model = None


def load_if_needed():
    global vectorizer, model
    if vectorizer is None or model is None:
        from .model_loader import load_models
        vectorizer, model = load_models()


def run_ml_model(data):

    try:
        load_if_needed()

        # Skip media
        if data["type"] in ["image", "audio", "video"]:
            return {
                "ml_probability": 0,
                "ml_prediction": "unknown",
                "confidence": 0
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

        # 🔥 Confidence score
        confidence = abs(prob - 0.5) * 2

        prediction = "fraud" if prob > 0.5 else "safe"

        return {
            "ml_probability": round(prob, 3),
            "ml_prediction": prediction,
            "confidence": round(confidence, 3)
        }

    except Exception as e:
        return {
            "ml_probability": 0,
            "ml_prediction": "error",
            "confidence": 0,
            "error": str(e)
        }