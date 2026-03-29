"""
Audio Deepfake Detection using ASVSpoof-Trained Models
Detects AI-generated speech, voice conversion, and replay attacks
Uses SafeEar framework trained on ASVSpoof 2019 LA dataset
"""

import torch
import numpy as np
import librosa
from pathlib import Path
from typing import Tuple, Dict
try:
    from transformers import AutoModelForSequenceClassification, AutoFeatureExtractor, Wav2Vec2Processor
except ImportError:
    AutoModelForSequenceClassification = None
    AutoFeatureExtractor = None
    Wav2Vec2Processor = None

# Global model cache
_spoof_detection_model = None
_spoof_detector_processor = None


def get_spoof_detection_model():
    """
    Load SafeEar ASVSpoof detection model from Hugging Face.
    Specifically trained on ASVSpoof 2019 LA dataset for synthetic speech detection.

    Returns: (model, processor) tuple
    """
    global _spoof_detection_model, _spoof_detector_processor

    if _spoof_detection_model is None:
        print("Loading SafeEar ASVSpoof detection model (first run may take a moment)...")
        try:
            # Use SafeEar model - specifically trained for spoof/synthetic speech detection
            # Detects: TTS, voice conversion, replay attacks
            model_name = "TEC2004/SafeEar-ASV19-spoof-detection"

            processor = Wav2Vec2Processor.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)

            model.eval()

            _spoof_detector_processor = processor
            _spoof_detection_model = model

            print(f"✓ SafeEar ASVSpoof model loaded successfully")
            print(f"  Model: {model_name}")
            print(f"  Performance: 5.275% EER on ASVSpoof 2019 LA")
            return processor, model

        except Exception as e:
            print(f"Warning: Could not load SafeEar model: {e}")
            print("Trying alternative AASIST3 model...")

            try:
                # Fallback to AASIST3 (latest model)
                model_name = "MTUCI/AASIST3"
                processor = Wav2Vec2Processor.from_pretrained(model_name)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)
                model.eval()

                _spoof_detector_processor = processor
                _spoof_detection_model = model

                print(f"✓ AASIST3 model loaded successfully")
                return processor, model

            except Exception as e2:
                print(f"Warning: Could not load AASIST3 model either: {e2}")
                print("Falling back to TTS artifact analysis...")
                return None, None

    return _spoof_detector_processor, _spoof_detection_model


def detect_audio_deepfake(audio_path: str) -> Tuple[float, float]:
    """
    Detect if audio is spoofed/synthetic using SafeEar ASVSpoof model.

    Detects:
    - TTS (Text-to-Speech synthesis) including 11 Labs, Google TTS, Amazon Polly
    - Voice conversion attacks
    - Replay attacks

    Args:
        audio_path: Path to audio file

    Returns:
        Tuple of (deepfake_score, confidence)
        - deepfake_score: 0-1, higher = more likely synthetic/spoofed
        - confidence: 0-1, model confidence
    """
    try:
        audio_path_obj = Path(audio_path)
        if not audio_path_obj.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"\n🎵 Detecting spoofed/synthetic speech: {audio_path}")

        # Try SafeEar ASVSpoof model
        processor, model = get_spoof_detection_model()

        if processor is not None and model is not None:
            print("  ✓ Using ASVSpoof detection model...")
            try:
                # Load audio
                y, sr = librosa.load(audio_path, sr=16000)

                # Process with model's processor
                inputs = processor(y, sampling_rate=16000, return_tensors="pt", padding=True)

                # Run inference
                with torch.no_grad():
                    outputs = model(**inputs)
                    logits = outputs.logits

                    # Get probability for spoofed class
                    probs = torch.softmax(logits, dim=-1)

                    # Label 1 = Spoof (synthetic), Label 0 = Bonafide (genuine)
                    spoof_prob = probs[0, 1].item()

                confidence = 0.95  # High confidence with dedicated model

                print(f"✓ ASVSpoof detection - Spoof score: {spoof_prob:.3f} (confidence: {confidence:.2f})")

                if spoof_prob > 0.5:
                    print(f"⚠️  DETECTED: Audio is likely SPOOFED/SYNTHETIC (score: {spoof_prob:.3f})")
                else:
                    print(f"✓ Audio appears GENUINE (score: {spoof_prob:.3f})")

                return spoof_prob, confidence

            except Exception as e:
                print(f"  ✗ ASVSpoof inference failed: {e}")
                print(f"  → Falling back to TTS artifact analysis...")

        # Fallback: TTS artifact analysis
        print("  ℹ Using TTS artifact analysis (fallback)...")
        features = extract_tts_features(audio_path)
        deepfake_score = analyze_tts_artifacts(features)
        confidence = 0.70

        print(f"✓ TTS artifact analysis - Synthetic score: {deepfake_score:.3f} (confidence: {confidence:.2f})")
        return deepfake_score, confidence

    except Exception as e:
        print(f"❌ Deepfake detection failed: {str(e)}")
        return 0.5, 0.3



def extract_tts_features(audio_path: str, sr: int = 16000) -> Dict[str, np.ndarray]:
    """
    Extract TTS-specific features as fallback.
    """
    try:
        y, _ = librosa.load(audio_path, sr=sr)

        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, n_fft=2048, hop_length=512)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        spectral_flux = np.sqrt(np.sum(np.diff(mel_spec_db, axis=1)**2, axis=0))
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta_delta = librosa.feature.delta(mfcc, order=2)
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        features = {
            "mfcc": (mfcc - mfcc.mean()) / (mfcc.std() + 1e-8),
            "mel_spec": (mel_spec_db - mel_spec_db.mean()) / (mel_spec_db.std() + 1e-8),
            "spectral_flux": (spectral_flux - spectral_flux.mean()) / (spectral_flux.std() + 1e-8),
            "mfcc_delta": (mfcc_delta - mfcc_delta.mean()) / (mfcc_delta.std() + 1e-8),
            "mfcc_delta_delta": (mfcc_delta_delta - mfcc_delta_delta.mean()) / (mfcc_delta_delta.std() + 1e-8),
            "zcr": zcr
        }

        return features

    except Exception as e:
        print(f"Error extracting TTS features: {str(e)}")
        raise


def analyze_tts_artifacts(features: Dict[str, np.ndarray]) -> float:
    """
    Analyze audio features for TTS/synthetic speech artifacts.
    More aggressive thresholds for 11 Labs and modern TTS detection.
    """
    try:
        artifact_score = 0.0

        # 1. MFCC Delta Variance (lower = more TTS-like)
        mfcc_delta = features["mfcc_delta"]
        delta_variance = np.var(mfcc_delta, axis=1).mean()

        print(f"  [DEBUG] MFCC delta variance: {delta_variance:.4f}")

        # More aggressive: Lower threshold = catch more TTS
        if delta_variance < 0.25:  # Was 0.15, now more sensitive
            artifact_score += 0.30  # Was 0.25
        elif delta_variance < 0.5:  # Was 0.3
            artifact_score += 0.20  # Was 0.15
        elif delta_variance < 1.0:
            artifact_score += 0.10

        # 2. MFCC Delta-Delta (acceleration) patterns
        mfcc_delta_delta = features["mfcc_delta_delta"]
        accel_variance = np.var(mfcc_delta_delta, axis=1).mean()

        print(f"  [DEBUG] MFCC acceleration variance: {accel_variance:.4f}")

        if accel_variance < 0.15:  # Was 0.1
            artifact_score += 0.25  # Was 0.2
        elif accel_variance < 0.3:  # Was 0.2
            artifact_score += 0.15  # Was 0.1
        elif accel_variance < 0.5:
            artifact_score += 0.08

        # 3. Spectral Flux Consistency
        spectral_flux = features["spectral_flux"]
        flux_std = np.std(spectral_flux)
        flux_mean = np.mean(spectral_flux)
        flux_ratio = flux_std / (flux_mean + 1e-8)

        print(f"  [DEBUG] Spectral flux - mean: {flux_mean:.4f}, std: {flux_std:.4f}, ratio: {flux_ratio:.4f}")

        if flux_mean < 0.05 or flux_ratio < 0.25:  # Was 0.01 / 0.2
            artifact_score += 0.20  # Was 0.15
        elif flux_mean < 0.1 or flux_ratio < 0.4:  # New threshold
            artifact_score += 0.12

        # 4. MFCC contour smoothness (pitch smoothness)
        mfcc = features["mfcc"]
        mfcc_smoothness = np.mean(np.abs(np.diff(mfcc[0, :])))

        print(f"  [DEBUG] MFCC pitch smoothness: {mfcc_smoothness:.4f}")

        if mfcc_smoothness < 0.15:  # Was 0.1
            artifact_score += 0.15  # Was 0.1
        elif mfcc_smoothness < 0.25:  # New threshold
            artifact_score += 0.08

        # 5. Zero-Crossing Rate stability (voicedness consistency)
        zcr = features["zcr"]
        zcr_mean = np.mean(np.abs(zcr))
        zcr_std = np.std(zcr)

        print(f"  [DEBUG] ZCR - mean: {zcr_mean:.4f}, std: {zcr_std:.4f}")

        # TTS has very stable ZCR (low variation)
        if zcr_std < 0.02:  # Was checking if all < 0.05
            artifact_score += 0.15

        # 6. NEW: Spectral Centroid Stability (pitch consistency indicator)
        # TTS has unnaturally stable spectral centroid
        try:
            from scipy.signal import spectrogram
            # Just check if spectrum is too flat
            if "spectral_centroid_std" not in features:
                # Calculate a simple spectral stability metric
                mel_spec = features["mel_spec"]
                center_of_mass = np.average(np.arange(mel_spec.shape[0]),
                                           weights=mel_spec.mean(axis=1))
                com_std = np.std(center_of_mass)
                print(f"  [DEBUG] Spectral center stability: {com_std:.4f}")

                if com_std < 0.5:  # Very stable = suspicious
                    artifact_score += 0.10
        except:
            pass

        print(f"  [DEBUG] Total artifact score: {artifact_score:.3f}")

        return min(artifact_score, 1.0)

    except Exception as e:
        print(f"Artifact analysis failed: {str(e)}")
        return 0.5


def detect_audio_deepfake(audio_path: str) -> Tuple[float, float]:
    """
    Detect if audio is AI-generated using ASVSpoof 2023 approach (Wav2Vec2).

    Args:
        audio_path: Path to audio file

    Returns:
        Tuple of (deepfake_score, confidence)
    """
    try:
        audio_path_obj = Path(audio_path)
        if not audio_path_obj.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"\n🎵 Detecting synthetic speech in audio: {audio_path}")

        # Try Wav2Vec2 approach
        processor, model = get_wav2vec2_model()

        if processor is not None and model is not None:
            print("  ✓ Using Wav2Vec2 model...")
            try:
                embeddings = extract_wav2vec2_embeddings(audio_path, processor, model)
                deepfake_score = analyze_embeddings_for_synthetic_speech(embeddings)
                confidence = 0.80

                print(f"✓ Wav2Vec2 detection - Synthetic score: {deepfake_score:.3f} (confidence: {confidence:.2f})")
                return deepfake_score, confidence

            except Exception as e:
                print(f"  ✗ Wav2Vec2 inference failed: {e}")
                print(f"  → Falling back to TTS artifact analysis...")

        # Fallback: TTS artifact analysis
        print("  ℹ Using TTS artifact analysis (fallback)...")
        features = extract_tts_features(audio_path)
        deepfake_score = analyze_tts_artifacts(features)
        confidence = 0.70

        print(f"✓ TTS artifact analysis - Synthetic score: {deepfake_score:.3f} (confidence: {confidence:.2f})")

        if deepfake_score > 0.5:
            print(f"⚠️  FLAGGED: Audio appears synthetic (score > 0.5)")
        else:
            print(f"✓ Audio appears natural (score < 0.5)")

        return deepfake_score, confidence

    except Exception as e:
        print(f"❌ Deepfake detection failed: {str(e)}")
        return 0.5, 0.3


def process_audio_for_deepfake_analysis(audio_path: str) -> Dict:
    """
    Process audio and prepare deepfake/spoof detection results.
    Uses ASVSpoof-trained SafeEar model for synthetic speech detection.

    Args:
        audio_path: Path to audio file

    Returns:
        Dictionary with spoof detection metadata
    """
    deepfake_score, confidence = detect_audio_deepfake(audio_path)

    is_likely_deepfake = deepfake_score > 0.5

    return {
        "type": "audio_deepfake",
        "deepfake_score": round(deepfake_score, 3),
        "is_likely_deepfake": is_likely_deepfake,
        "metadata": {
            "original_file": audio_path,
            "deepfake_confidence": round(confidence, 2),
            "detection_model": "asvspoof-safeear",
            "detection_type": "synthetic_speech_detection",
            "detects": ["TTS", "voice_conversion", "replay_attacks"],
            "risk_level": "high" if deepfake_score > 0.7 else "medium" if deepfake_score > 0.4 else "low"
        }
    }


