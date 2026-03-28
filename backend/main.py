from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor
import threading

# Input Layer
from input_layer.input_handler import process_text_input, process_file_input

# Layer 0
from layer0_privacy.normalization import process_privacy_layer

# Layer 1
from layer1_heuristics.heuristic_engine import run_heuristics

# Layer 2
from layer2_ml.ml_engine import run_ml_model

# Layer 3 (LLM) - Split into scorer, reasoners, and explanation
from layer3_llm.llm_scorer import run_llm_scorer
from layer3_llm.layer_reasoner import run_layer1_reasoning, run_layer2_reasoning
from layer3_llm.llm_engine import run_llm_explanation

# Risk Engine
from risk_engine.decision_engine import make_decision


app = FastAPI(
    title="Fraud Detection System",
    version="3.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

# Model pre-loading flags
models_preloaded = False


def preload_models():
    """Pre-load heavyweight models on startup (background task)"""
    global models_preloaded
    if models_preloaded:
        return
    print("[*] Pre-loading models in background...")
    try:
        from layer2_ml.model_loader import load_models
        load_models()
        print("[✓] ML models pre-loaded")
    except Exception as e:
        print(f"[!] Model pre-loading error: {e}")
    models_preloaded = True


# Pre-load models on first request
@app.on_event("startup")
async def startup_event():
    """Pre-cache models on app startup"""
    preload_models()


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
    """OPTIMIZED: Parallelized layer processing"""

    # 🔹 Step 1: Input Layer
    input_data = process_text_input(text)
    context_type = input_data.get("type", "email")

    # Store url_analysis for response, but remove from metadata to avoid duplication in layers
    url_analysis_input = input_data.get("metadata", {}).pop("url_analysis", {})

    # 🔹 Step 2: Layer 0 (Privacy + Features) - FAST, run first
    layer0_output = process_privacy_layer(input_data)

    # 🔹 Step 3: PARALLELIZE Layer 1 and Layer 2 processing
    print("[*] Running Layer 1 & 2 in PARALLEL...")
    layer1_output = None
    layer2_output = None
    heuristic_score = 0

    # Run Layer 1 and Layer 2 in parallel threads
    def run_layer1():
        nonlocal layer1_output, heuristic_score
        layer1_output = run_heuristics(layer0_output)
        heuristic_score = layer1_output.get("heuristic_score", 0)

    def run_layer2():
        nonlocal layer2_output
        # Smart routing based on heuristic score (wait for layer1 if needed)
        import time
        timeout = 0
        while layer1_output is None and timeout < 100:  # Wait max 10s for layer1
            time.sleep(0.1)
            timeout += 1

        hs = layer1_output.get("heuristic_score", 0) if layer1_output else 0
        if hs >= 120:
            layer2_output = {
                "ml_text_score": 95.0,
                "ml_text_confidence": 1.0,
                "note": "Skipped ML (high risk from heuristics)"
            }
        elif hs <= 20:
            layer2_output = {
                "ml_text_score": 5.0,
                "ml_text_confidence": 1.0,
                "note": "Skipped ML (low risk from heuristics)"
            }
        else:
            layer2_output = run_ml_model(layer0_output)

    # Start both in parallel
    t1 = threading.Thread(target=run_layer1, daemon=True)
    t2 = threading.Thread(target=run_layer2, daemon=True)
    t1.start()
    t2.start()
    t1.join(timeout=30)  # Wait max 30s
    t2.join(timeout=30)

    # Add URL scoring to layer2 output if available
    if url_analysis_input and url_analysis_input.get("has_urls"):
        layer2_output["url_ml_score"] = url_analysis_input.get("url_ml_score", 0)
        layer2_output["url_ml_confidence"] = url_analysis_input.get("url_ml_confidence", 0)

    # 🔹 Step 4: PARALLELIZE LLM Reasoning for Layer 1 & 2
    print("[*] Running LLM Reasoning for Layers 1 & 2 in PARALLEL...")
    layer1_reasoning = None
    layer2_reasoning = None

    def run_l1_reasoning():
        nonlocal layer1_reasoning
        layer1_reasoning = run_layer1_reasoning(
            text=layer0_output.get("clean_text", ""),
            layer1_output=layer1_output
        )

    def run_l2_reasoning():
        nonlocal layer2_reasoning
        layer2_reasoning = run_layer2_reasoning(
            text=layer0_output.get("clean_text", ""),
            layer1_output=layer1_output,
            layer2_output=layer2_output
        )

    # Start both in parallel
    t3 = threading.Thread(target=run_l1_reasoning, daemon=True)
    t4 = threading.Thread(target=run_l2_reasoning, daemon=True)
    t3.start()
    t4.start()
    t3.join(timeout=30)
    t4.join(timeout=30)

    # Add reasoning to layer2 output for frontend display
    layer2_output["reasoning"] = layer2_reasoning

    # 🔹 Step 5: Layer 3 Part 1 (LLM Scoring)
    layer3_scoring = run_llm_scorer(
        text=layer0_output.get("clean_text", ""),
        layer0=layer0_output,
        layer1=layer1_output,
        layer2=layer2_output
    )

    # Add LLM score to layer2 for Risk Engine fusion
    layer2_output["llm_score"] = layer3_scoring.get("llm_score", 0)
    layer2_output["llm_confidence"] = layer3_scoring.get("llm_confidence", 0)

    # Prepare meta info for context-aware scoring
    meta = {
        "has_url": url_analysis_input.get("has_urls", False),
        "ocr_used": input_data.get("type") in ["audio_transcribed", "file_pdf"],
        "ocr_quality": layer0_output.get("ocr_quality", 0.8)
    }

    # 🔹 Step 6: Risk Engine (Final Decision with all layer signals)
    final_output = make_decision(layer1_output, layer2_output, context_type, meta)

    # 🔹 Step 7: Layer 3 Part 2 (LLM Explanation) - Explain final decision
    layer3_explanation = run_llm_explanation(
        text=layer0_output.get("clean_text", ""),
        layer0=layer0_output,
        layer1=layer1_output,
        layer2=layer2_output,
        layer3_scoring=layer3_scoring,
        final=final_output
    )

    # Restore url_analysis to input_data for response
    input_data["metadata"]["url_analysis"] = url_analysis_input

    return {
        "input": input_data,
        "layer0": layer0_output,
        "layer1": layer1_output,
        "layer1_reasoning": layer1_reasoning,
        "layer2": layer2_output,
        "layer2_reasoning": layer2_reasoning,
        "layer3_scoring": layer3_scoring,
        "final": final_output,
        "layer3_explanation": layer3_explanation
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

        # Store url_analysis for response, but remove from metadata to avoid duplication in layers
        url_analysis_input = input_data.get("metadata", {}).pop("url_analysis", {})
        deepfake_analysis_input = input_data.get("metadata", {}).pop("deepfake_analysis", {})

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

            # 🔹 Step 3.5: Layer 3 - LLM Reasoning for Layer 1
            layer1_reasoning = run_layer1_reasoning(
                text=layer0_output.get("clean_text", ""),
                layer1_output=layer1_output
            )

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
            if url_analysis_input and url_analysis_input.get("has_urls"):
                layer2_output["url_ml_score"] = url_analysis_input.get("url_ml_score", 0)
                layer2_output["url_ml_confidence"] = url_analysis_input.get("url_ml_confidence", 0)

            # Add deepfake scoring for audio
            if deepfake_analysis_input and deepfake_analysis_input.get("deepfake_score") is not None:
                layer2_output["deepfake_score"] = deepfake_analysis_input.get("deepfake_score", 0) * 100
                layer2_output["deepfake_confidence"] = deepfake_analysis_input.get("metadata", {}).get("deepfake_confidence", 0)

            # 🔹 Step 4.5: Layer 3 - LLM Reasoning for Layer 2
            layer2_reasoning = run_layer2_reasoning(
                text=layer0_output.get("clean_text", ""),
                layer1_output=layer1_output,
                layer2_output=layer2_output
            )

            # Add reasoning to layer2 output for frontend display
            layer2_output["reasoning"] = layer2_reasoning

            # 🔹 Step 5: Layer 3 Part 1 (LLM Scoring) - Independent fraud risk assessment
            layer3_scoring = run_llm_scorer(
                text=layer0_output.get("clean_text", ""),
                layer0=layer0_output,
                layer1=layer1_output,
                layer2=layer2_output
            )

            # Add LLM score to layer2 for Risk Engine fusion
            layer2_output["llm_score"] = layer3_scoring.get("llm_score", 0)
            layer2_output["llm_confidence"] = layer3_scoring.get("llm_confidence", 0)

            # Prepare meta info for context-aware scoring
            meta = {
                "has_url": url_analysis_input.get("has_urls", False),
                "ocr_used": input_data.get("type") in ["audio_transcribed", "file_pdf", "image_ocr"],
                "ocr_quality": layer0_output.get("ocr_quality", input_data.get("metadata", {}).get("ocr_quality", 0.8))
            }

            # 🔹 Step 6: Risk Engine (Final Decision with all layer signals)
            final_output = make_decision(layer1_output, layer2_output, context_type, meta)

            # 🔹 Step 7: Layer 3 Part 2 (LLM Explanation) - Explain final decision
            layer3_explanation = run_llm_explanation(
                text=layer0_output.get("clean_text", ""),
                layer0=layer0_output,
                layer1=layer1_output,
                layer2=layer2_output,
                layer3_scoring=layer3_scoring,
                final=final_output
            )

            # Restore url_analysis and deepfake_analysis to input_data for response
            input_data["metadata"]["url_analysis"] = url_analysis_input
            input_data["metadata"]["deepfake_analysis"] = deepfake_analysis_input

            return {
                "input": input_data,
                "layer0": layer0_output,
                "layer1": layer1_output,
                "layer1_reasoning": layer1_reasoning,
                "layer2": layer2_output,
                "layer2_reasoning": layer2_reasoning,
                "layer3_scoring": layer3_scoring,
                "final": final_output,
                "layer3_explanation": layer3_explanation
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