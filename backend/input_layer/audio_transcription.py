"""
Audio transcription using OpenAI's Whisper model.
Converts audio files to text for fraud detection analysis.
"""

import whisper
import os
from typing import Optional


class AudioTranscriber:
    """Handles audio-to-text conversion using Whisper."""

    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model.

        Args:
            model_size: Whisper model size to use. Options:
                - "tiny": Fastest, least accurate
                - "base": Good balance (default)
                - "small": Better accuracy
                - "medium": High accuracy
                - "large": Best accuracy, slowest
        """
        self.model_size = model_size
        self._model = None

    def _load_model(self):
        """Lazy load the Whisper model."""
        if self._model is None:
            print(f"Loading Whisper model: {self.model_size}...")
            self._model = whisper.load_model(self.model_size)
            print(f"Whisper model loaded successfully.")
        return self._model

    def transcribe_audio(self, file_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribe audio file to text.

        Args:
            file_path: Path to audio file (mp3, wav, flac, aac, ogg, etc.)
            language: Optional language code (e.g., "en", "hi"). Auto-detected if None.

        Returns:
            dict with keys:
                - text: Transcribed text
                - language: Detected/specified language
                - segments: List of timestamped segments
                - confidence: Average confidence score (if available)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        model = self._load_model()

        # Transcribe with Whisper
        print(f"Transcribing audio: {file_path}")
        result = model.transcribe(
            file_path,
            language=language,
            fp16=False  # Use fp32 for better CPU compatibility
        )

        # Calculate average confidence if available
        avg_confidence = None
        if "segments" in result and result["segments"]:
            confidences = [
                seg.get("avg_logprob", 0)
                for seg in result["segments"]
            ]
            if confidences:
                # Convert log probabilities to approximate confidence (0-1)
                avg_confidence = sum(confidences) / len(confidences)

        return {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "confidence": avg_confidence
        }


# Singleton instance
_transcriber = None

def get_transcriber(model_size: str = "base") -> AudioTranscriber:
    """Get or create a singleton AudioTranscriber instance."""
    global _transcriber
    if _transcriber is None:
        _transcriber = AudioTranscriber(model_size)
    return _transcriber


def transcribe_audio_file(file_path: str, language: Optional[str] = None) -> str:
    """
    Simple wrapper to transcribe audio file and return text.

    Args:
        file_path: Path to audio file
        language: Optional language code

    Returns:
        Transcribed text
    """
    transcriber = get_transcriber()
    result = transcriber.transcribe_audio(file_path, language)
    return result["text"]
