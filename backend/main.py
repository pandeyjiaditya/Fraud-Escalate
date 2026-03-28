from fastapi import FastAPI, UploadFile, File
import shutil
import os
from pathlib import Path
import subprocess

# Input Layer
from input_layer.input_handler import process_text_input, process_file_input

# Layer 0
from layer0_privacy.normalization import process_privacy_layer

# Layer 1
from layer1_heuristics.heuristic_engine import run_heuristics

# Layer 2
from layer2_ml.ml_engine import run_ml_model

# Risk Engine
from risk_engine.decision_engine import make_decision

# Layer 3 (LLM)
from layer3_llm.llm_engine import run_llm


app = FastAPI(
    title="Fraud Detection System",
    version="3.0"
)


# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def home():
    return {"message": "Fraud Detection System Running"}


@app.get("/health")
def health():
    return {"status": "OK"}


# -----------------------------
# FULL PIPELINE (ALL LAYERS)
# -----------------------------

@app.post("/analyze")
def analyze(text: str):

    # 🔹 Step 1: Input Layer
    input_data = process_text_input(text)
    context_type = input_data.get("type", "email")

    # 🔹 Step 2: Layer 0 (Privacy + Features)
    layer0_output = process_privacy_layer(input_data)

    # 🔹 Step 3: Layer 1 (Heuristic Detection)
    layer1_output = run_heuristics(layer0_output)
    heuristic_score = layer1_output.get("heuristic_score", 0)

    # 🔥 Step 4: Smart Routing for ML
    if heuristic_score >= 120:
        layer2_output = {
            "ml_text_score": 95.0,
            "ml_text_confidence": 1.0,
            "note": "Skipped ML (high risk from heuristics)"
        }

    elif heuristic_score <= 20:
        layer2_output = {
            "ml_text_score": 5.0,
            "ml_text_confidence": 1.0,
            "note": "Skipped ML (low risk from heuristics)"
        }

    else:
        layer2_output = run_ml_model(layer0_output)

    # Add URL scoring to layer2 output
    url_analysis = input_data.get("metadata", {}).get("url_analysis", {})
    if url_analysis and url_analysis.get("has_urls"):
        layer2_output["url_ml_score"] = url_analysis.get("url_ml_score", 0)
        layer2_output["url_ml_confidence"] = url_analysis.get("url_ml_confidence", 0)

    # Prepare meta info for context-aware scoring
    url_analysis = input_data.get("metadata", {}).get("url_analysis", {})
    meta = {
        "has_url": url_analysis.get("has_urls", False),
        "ocr_used": input_data.get("type") in ["audio_transcribed", "file_pdf"],
        "ocr_quality": layer0_output.get("ocr_quality", 0.8)
    }

    # 🔹 Step 5: Risk Engine (Final Decision)
    final_output = make_decision(layer1_output, layer2_output, context_type, meta)

    # 🔹 Step 6: Layer 3 (LLM Explanation)
    llm_output = run_llm(
        text=layer0_output.get("clean_text", ""),
        layer1=layer1_output,
        layer2=layer2_output,
        final=final_output
    )

    return {
        "input": input_data,
        "layer0": layer0_output,
        "layer1": layer1_output,
        "layer2": layer2_output,
        "final": final_output,
        "layer3": llm_output
    }


# -----------------------------
# FILE UPLOAD ENDPOINT (For Audio, PDF, DOCX, etc.)
# -----------------------------
@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    """
    Analyze uploaded file (audio, PDF, DOCX, TXT).
    Audio files are automatically transcribed using Whisper.
    """
    # Create temp directory if it doesn't exist
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    # Save uploaded file temporarily
    file_path = temp_dir / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the file
        input_data = process_file_input(str(file_path))

        # If the input is not audio/image/video, it should have content as text
        if input_data["type"] in ["audio_transcribed", "text", "url", "email", "image_ocr"]:
            text_content = input_data["content"]
            context_type = input_data.get("type", "file")
            if context_type == "audio_transcribed":
                context_type = "audio"

            # 🔹 Step 2: Layer 0 (Privacy + Features)
            layer0_output = process_privacy_layer(input_data)

            # 🔹 Step 3: Layer 1 (Heuristic Detection)
            layer1_output = run_heuristics(layer0_output)
            heuristic_score = layer1_output.get("heuristic_score", 0)

            # 🔥 Step 4: Smart Routing for ML
            if heuristic_score >= 120:
                layer2_output = {
                    "ml_text_score": 95.0,
                    "ml_text_confidence": 1.0,
                    "note": "Skipped ML (high risk from heuristics)"
                }

            elif heuristic_score <= 20:
                layer2_output = {
                    "ml_text_score": 5.0,
                    "ml_text_confidence": 1.0,
                    "note": "Skipped ML (low risk from heuristics)"
                }

            else:
                layer2_output = run_ml_model(layer0_output)

            # Add URL scoring to layer2 output
            url_analysis = input_data.get("metadata", {}).get("url_analysis", {})
            if url_analysis and url_analysis.get("has_urls"):
                layer2_output["url_ml_score"] = url_analysis.get("url_ml_score", 0)
                layer2_output["url_ml_confidence"] = url_analysis.get("url_ml_confidence", 0)

            # Add deepfake scoring for audio
            deepfake_analysis = input_data.get("metadata", {}).get("deepfake_analysis", {})
            if deepfake_analysis and deepfake_analysis.get("deepfake_score") is not None:
                layer2_output["deepfake_score"] = deepfake_analysis.get("deepfake_score", 0) * 100
                layer2_output["deepfake_confidence"] = deepfake_analysis.get("metadata", {}).get("deepfake_confidence", 0)

            # Prepare meta info for context-aware scoring
            url_analysis = input_data.get("metadata", {}).get("url_analysis", {})
            meta = {
                "has_url": url_analysis.get("has_urls", False),
                "ocr_used": input_data.get("type") in ["audio_transcribed", "file_pdf", "image_ocr"],
                "ocr_quality": layer0_output.get("ocr_quality", input_data.get("metadata", {}).get("ocr_quality", 0.8))
            }

            # 🔹 Step 5: Risk Engine (Final Decision)
            final_output = make_decision(layer1_output, layer2_output, context_type, meta)

            # 🔹 Step 6: Layer 3 (LLM Explanation)
            llm_output = run_llm(
                text=layer0_output.get("clean_text", ""),
                layer1=layer1_output,
                layer2=layer2_output,
                final=final_output
            )

            return {
                "input": input_data,
                "layer0": layer0_output,
                "layer1": layer1_output,
                "layer2": layer2_output,
                "final": final_output,
                "layer3": llm_output
            }
        else:
            # For image/video, return basic info (no fraud analysis yet)
            return {
                "input": input_data,
                "message": f"{input_data['type']} processing not yet implemented"
            }

    finally:
        # Cleanup: Remove temporary file
        if file_path.exists():
            file_path.unlink()