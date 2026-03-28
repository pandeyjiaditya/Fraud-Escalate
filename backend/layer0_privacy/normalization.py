import re
from .pii_removal import remove_pii
from .feature_extraction import extract_features


def normalize_text(text: str):

    text = text.lower()

    # remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# 🔹 Main Layer 0 processor
def process_privacy_layer(input_data):

    # Skip media inputs
    if input_data["type"] in ["image", "audio", "video"]:
        return input_data

    text = input_data["content"]

    # Step 1: Remove PII
    clean_text = remove_pii(text)

    # Step 2: Normalize
    normalized_text = normalize_text(clean_text)

    # Step 3: Feature extraction
    features = extract_features(normalized_text)

    # Calculate confidence (based on how much was cleaned)
    pii_removed = len(text) - len(clean_text)
    clean_confidence = max(0, 1.0 - (pii_removed / max(len(text), 1))) if len(text) > 0 else 1.0

    return {
        "type": input_data["type"],
        "original_text": text,
        "clean_text": normalized_text,
        "features": features,
        "clean_text_confidence": clean_confidence * 100,  # For frontend compatibility
        "word_count": len(normalized_text.split()),  # For frontend compatibility
        "pii_detected": pii_removed > 0,
        "character_reduction": {
            "original_length": len(text),
            "cleaned_length": len(clean_text),
            "normalized_length": len(normalized_text)
        },
        "metadata": input_data["metadata"]
    }