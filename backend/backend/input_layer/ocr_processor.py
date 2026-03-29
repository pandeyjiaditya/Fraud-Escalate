"""
OCR Processor Module - Extract text from images using EasyOCR
"""

import easyocr
from pathlib import Path
from typing import Tuple

# Initialize OCR reader (lazy loading to avoid overhead on non-OCR tasks)
_ocr_reader = None


def get_ocr_reader():
    """
    Lazy load OCR reader to avoid unnecessary initialization.
    EasyOCR models are downloaded on first use.
    """
    global _ocr_reader
    if _ocr_reader is None:
        print("Initializing EasyOCR reader (first run may take a moment)...")
        _ocr_reader = easyocr.Reader(['en'], gpu=False)
    return _ocr_reader


def extract_text_from_image(image_path: str) -> Tuple[str, float]:
    """
    Extract text from an image using OCR.

    Args:
        image_path: Path to the image file

    Returns:
        Tuple of (extracted_text, confidence_score)
        - extracted_text: Text extracted from the image
        - confidence_score: Average confidence of OCR recognition (0-1)
    """
    try:
        # Validate file exists
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Get OCR reader
        reader = get_ocr_reader()

        # Read image with OCR
        print(f"Extracting text from image: {image_path}")
        results = reader.readtext(image_path)

        if not results:
            print("No text detected in image")
            return "", 0.0

        # Extract text and calculate confidence
        extracted_text = "\n".join([text for (_, text, _) in results])
        average_confidence = sum([conf for (_, _, conf) in results]) / len(results)

        print(f"OCR extraction complete. Found {len(results)} text regions.")
        print(f"Average confidence: {average_confidence:.2f}")

        return extracted_text, average_confidence

    except Exception as e:
        print(f"OCR extraction failed: {str(e)}")
        raise


def process_image_for_fraud_analysis(image_path: str) -> dict:
    """
    Process an image and prepare it for fraud analysis pipeline.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary with extracted text and OCR metadata
    """
    extracted_text, confidence = extract_text_from_image(image_path)

    return {
        "type": "image_ocr",
        "content": extracted_text,
        "metadata": {
            "original_file": image_path,
            "ocr_confidence": confidence,
            "ocr_quality": confidence  # Quality metric for downstream processing
        }
    }
