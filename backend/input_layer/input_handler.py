from datetime import datetime

from .file_segregator import detect_input_type
from .file_readers import read_txt, read_pdf, read_docx
from .audio_transcription import transcribe_audio_file
from .ocr_processor import process_image_for_fraud_analysis
from .url_processor import process_url_for_fraud_analysis


def process_text_input(data: str):
    input_type = detect_input_type(data)

    # Extract and score URLs BEFORE Layer 0
    url_analysis = process_url_for_fraud_analysis(data)

    structured_input = {
        "type": input_type,
        "content": data,
        "metadata": {
            "timestamp": str(datetime.now()),
            "url_analysis": url_analysis
        }
    }

    return structured_input


def process_file_input(file_path: str):
    file_path_lower = file_path.lower()

    # Image detection - Extract text via OCR
    if file_path_lower.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")):
        print(f"Processing image file: {file_path}")
        ocr_result = process_image_for_fraud_analysis(file_path)
        print(f"Image OCR completed: {len(ocr_result['content'])} characters extracted")

        # Add timestamp to metadata
        ocr_result["metadata"]["timestamp"] = str(datetime.now())

        # Extract and score URLs from OCR content
        url_analysis = process_url_for_fraud_analysis(ocr_result["content"])
        ocr_result["metadata"]["url_analysis"] = url_analysis

        return ocr_result

    # Video detection
    elif file_path_lower.endswith((".mp4", ".avi", ".mov", ".mkv", ".webm")):
        return {
            "type": "video",
            "content": file_path,
            "metadata": {"timestamp": str(datetime.now())}
        }

    # Audio detection - Transcribe and process as text
    elif file_path_lower.endswith((".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma")):
        print(f"Processing audio file: {file_path}")
        transcribed_text = transcribe_audio_file(file_path)
        print(f"Audio transcribed successfully: {len(transcribed_text)} characters")

        # Extract and score URLs from transcribed text
        url_analysis = process_url_for_fraud_analysis(transcribed_text)

        # Process transcribed text through the same pipeline
        return {
            "type": "audio_transcribed",
            "content": transcribed_text,
            "metadata": {
                "timestamp": str(datetime.now()),
                "original_file": file_path,
                "url_analysis": url_analysis
            }
        }

    if file_path_lower.endswith(".txt"):
        content = read_txt(file_path)
    elif file_path_lower.endswith(".pdf"):
        content = read_pdf(file_path)
    elif file_path_lower.endswith(".docx"):
        content = read_docx(file_path)
    else:
        raise ValueError("Unsupported file type")

    return process_text_input(content)