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

    return {
        "type": input_data["type"],
        "original_text": text,
        "clean_text": normalized_text,
        "features": features,
        "metadata": input_data["metadata"]
    }