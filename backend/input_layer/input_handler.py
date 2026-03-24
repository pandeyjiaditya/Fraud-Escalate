from datetime import datetime

from .file_segregator import detect_input_type
from .file_readers import read_txt, read_pdf, read_docx


def process_text_input(data: str):
    input_type = detect_input_type(data)

    structured_input = {
        "type": input_type,
        "content": data,
        "metadata": {
            "timestamp": str(datetime.now())
        }
    }

    return structured_input


def process_file_input(file_path: str):
    file_path_lower = file_path.lower()
    
    # Image detection
    if file_path_lower.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")):
        return {
            "type": "image",
            "content": file_path,
            "metadata": {"timestamp": str(datetime.now())}
        }
        
    # Video detection
    elif file_path_lower.endswith((".mp4", ".avi", ".mov", ".mkv", ".webm")):
        return {
            "type": "video",
            "content": file_path,
            "metadata": {"timestamp": str(datetime.now())}
        }
        
    # Audio detection
    elif file_path_lower.endswith((".mp3", ".wav", ".flac", ".aac", ".ogg")):
        return {
            "type": "audio",
            "content": file_path,
            "metadata": {"timestamp": str(datetime.now())}
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