import re

def detect_input_type(data: str):
    # URL detection
    if re.search(r'https?://', data):
        return "url"

    # Email detection
    if "@" in data and "." in data:
        return "email"

    # Default text
    return "text"