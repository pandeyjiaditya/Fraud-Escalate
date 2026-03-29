from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor
import threading
import json

# Input Layer
from input_layer.input_handler import process_text_input, process_file_input

# Layer 0
from layer0_privacy.normalization import process_privacy_layer

# Layer 1
from layer1_heuristics.heuristic_engine import run_heuristics

# Layer 2
from layer2_ml.ml_engine import run_ml_model

# Layer 3 (LLM) - Now consolidated into single unified call
from layer3_llm.llm_scorer import run_llm_scorer
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


@app.get("/debug")
def debug_response():
    """Debug endpoint - returns a complete sample response structure"""
    return {
        "input": {
            "type": "email",
            "content": "Hello, this is a test message",
            "metadata": {}
        },
        "layer0": {
            "clean_text": "hello this is a test message",
            "word_count": 5,
            "clean_text_confidence": 0.95,
            "pii_detected": False,
            "features": {
                "has_url": False,
                "has_urgent_words": False,
                "has_numbers": False,
                "has_sensitive_keywords": False
            }
        },
        "layer1": {
            "heuristic_score": 20,
            "flags": [],
            "confidence": 0.2
        },
        "layer1_reasoning": {
            "flag_analysis": {},
            "overall_assessment": "No heuristic flags detected"
        },
        "layer2": {
            "ml_text_score": 25.5,
            "ml_text_confidence": 0.85,
            "ml_prediction": "safe"
        },
        "layer2_reasoning": {
            "text_analysis": "Text appears safe",
            "ml_patterns_detected": [],
            "comparison_with_heuristics": "Agrees with heuristics",
            "risk_level": "low"
        },
        "layer3_scoring": {
            "llm_score": 30.0,
            "llm_confidence": 0.8,
            "reasoning": "Limited fraud indicators detected"
        },
        "final": {
            "risk_score": 25.0,
            "risk_level": "LOW",
            "risk_color": "green",
            "decision": "SAFE",
            "confidence": 0.75,
            "context_type": "email",
            "reasoning": "Content appears legitimate based on available signals. Proceed normally."
        },
        "layer3_explanation": {
            "explanation": "This is a benign test message with no fraud indicators",
            "confidence": 0.85
        }
    }


@app.post("/analyze")
def analyze(text: str):
    """OPTIMIZED: Parallelized layer processing with error handling"""

    try:
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
            try:
                layer1_output = run_heuristics(layer0_output)
                heuristic_score = layer1_output.get("heuristic_score", 0)
            except Exception as e:
                print(f"[!] Layer 1 error: {e}")
                layer1_output = {
                    "heuristic_score": 0,
                    "flags": [],
                    "confidence": 0,
                    "error": str(e)
                }

        def run_layer2():
            nonlocal layer2_output
            try:
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
            except Exception as e:
                print(f"[!] Layer 2 error: {e}")
                layer2_output = {
                    "ml_text_score": 0,
                    "ml_text_confidence": 0,
                    "error": str(e)
                }

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

        # 🔹 Step 4: Layer 3 UNIFIED LLM (FIRST LLM CALL)
        print("[*] Running Layer 3 (UNIFIED): LLM Reasoning + Scoring...")
        layer3_scoring = None

        try:
            layer3_scoring = run_llm_scorer(
                text=layer0_output.get("clean_text", ""),
                layer0=layer0_output,
                layer1=layer1_output,
                layer2=layer2_output
            )
        except Exception as e:
            print(f"[!] Layer 3 scoring error: {e}")
            layer3_scoring = {
                "summary_1": f"Error analyzing heuristics: {str(e)}",
                "summary_2": f"Error analyzing ML: {str(e)}",
                "score_3": 50.0,
                "confidence_3": 0
            }

        # Add LLM score to layer2 for Risk Engine fusion
        layer2_output["llm_score"] = layer3_scoring.get("score_3", 0)
        layer2_output["llm_confidence"] = layer3_scoring.get("confidence_3", 0)

        # Prepare meta info for context-aware scoring
        meta = {
            "has_url": url_analysis_input.get("has_urls", False),
            "ocr_used": input_data.get("type") in ["audio_transcribed", "file_pdf"],
            "ocr_quality": layer0_output.get("ocr_quality", 0.8)
        }

        # 🔹 Step 5: Risk Engine (Final Decision with all layer signals)
        try:
            final_output = make_decision(layer1_output, layer2_output, context_type, meta)
        except Exception as e:
            print(f"[!] Risk Engine error: {e}")
            final_output = {
                "risk_score": 50.0,
                "risk_level": "MEDIUM",
                "risk_color": "orange",
                "decision": "REVIEW",
                "confidence": 0.5,
                "context_type": context_type,
                "reasoning": f"Error in risk calculation: {str(e)}"
            }

        # 🔹 Step 6: Layer 3 Part 2 (SECOND LLM CALL - Final Explanation)
        try:
            layer3_explanation = run_llm_explanation(
                text=layer0_output.get("clean_text", ""),
                layer0=layer0_output,
                layer1=layer1_output,
                layer2=layer2_output,
                layer3_scoring=layer3_scoring,
                final=final_output
            )
        except Exception as e:
            print(f"[!] Layer 3 explanation error: {e}")
            layer3_explanation = {
                "explanation": f"Error generating explanation: {str(e)}"
            }

        # Restore url_analysis to input_data for response
        input_data["metadata"]["url_analysis"] = url_analysis_input

        return {
            "input": input_data,
            "layer0": layer0_output,
            "layer1": layer1_output,
            "layer2": layer2_output,
            "layer3_scoring": layer3_scoring,
            "final": final_output,
            "layer3_explanation": layer3_explanation
        }

    except Exception as e:
        print(f"[!] CRITICAL ERROR in /analyze: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "message": "Analysis failed - see error details"
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

        try:
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
                try:
                    layer1_output = run_heuristics(layer0_output)
                except Exception as e:
                    print(f"[!] Layer 1 error: {e}")
                    layer1_output = {
                        "heuristic_score": 0,
                        "flags": [],
                        "confidence": 0,
                        "error": str(e)
                    }
                heuristic_score = layer1_output.get("heuristic_score", 0)

                # 🥥 Step 4: Smart Routing for ML
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
                    try:
                        layer2_output = run_ml_model(layer0_output)
                    except Exception as e:
                        print(f"[!] Layer 2 error: {e}")
                        layer2_output = {
                            "ml_text_score": 0,
                            "ml_text_confidence": 0,
                            "error": str(e)
                        }

                # Add URL scoring to layer2 output
                if url_analysis_input and url_analysis_input.get("has_urls"):
                    layer2_output["url_ml_score"] = url_analysis_input.get("url_ml_score", 0)
                    layer2_output["url_ml_confidence"] = url_analysis_input.get("url_ml_confidence", 0)

                # Add deepfake scoring for audio
                if deepfake_analysis_input and deepfake_analysis_input.get("deepfake_score") is not None:
                    layer2_output["deepfake_score"] = deepfake_analysis_input.get("deepfake_score", 0) * 100
                    layer2_output["deepfake_confidence"] = deepfake_analysis_input.get("metadata", {}).get("deepfake_confidence", 0)

                # 🔹 Step 5: Layer 3 UNIFIED LLM (FIRST LLM CALL)
                print("[*] Running Layer 3 (UNIFIED): LLM Reasoning + Scoring...")
                try:
                    layer3_scoring = run_llm_scorer(
                        text=layer0_output.get("clean_text", ""),
                        layer0=layer0_output,
                        layer1=layer1_output,
                        layer2=layer2_output
                    )
                except Exception as e:
                    print(f"[!] Layer 3 scoring error: {e}")
                    layer3_scoring = {
                        "summary_1": f"Error analyzing heuristics: {str(e)}",
                        "summary_2": f"Error analyzing ML: {str(e)}",
                        "score_3": 50.0,
                        "confidence_3": 0
                    }

                # Add LLM score to layer2 for Risk Engine fusion
                layer2_output["llm_score"] = layer3_scoring.get("score_3", 0)
                layer2_output["llm_confidence"] = layer3_scoring.get("confidence_3", 0)

                # Prepare meta info for context-aware scoring
                meta = {
                    "has_url": url_analysis_input.get("has_urls", False),
                    "ocr_used": input_data.get("type") in ["audio_transcribed", "file_pdf", "image_ocr"],
                    "ocr_quality": layer0_output.get("ocr_quality", input_data.get("metadata", {}).get("ocr_quality", 0.8))
                }

                # 🔹 Step 6: Risk Engine (Final Decision with all layer signals)
                try:
                    final_output = make_decision(layer1_output, layer2_output, context_type, meta)
                except Exception as e:
                    print(f"[!] Risk Engine error: {e}")
                    final_output = {
                        "risk_score": 50.0,
                        "risk_level": "MEDIUM",
                        "risk_color": "orange",
                        "decision": "REVIEW",
                        "confidence": 0.5,
                        "context_type": context_type,
                        "reasoning": f"Error in risk calculation: {str(e)}"
                    }

                # 🔹 Step 7: Layer 3 Part 2 (SECOND LLM CALL - Final Explanation)
                try:
                    layer3_explanation = run_llm_explanation(
                        text=layer0_output.get("clean_text", ""),
                        layer0=layer0_output,
                        layer1=layer1_output,
                        layer2=layer2_output,
                        layer3_scoring=layer3_scoring,
                        final=final_output
                    )
                except Exception as e:
                    print(f"[!] Layer 3 explanation error: {e}")
                    layer3_explanation = {
                        "explanation": f"Error generating explanation: {str(e)}"
                    }

                # Restore url_analysis and deepfake_analysis to input_data for response
                input_data["metadata"]["url_analysis"] = url_analysis_input
                input_data["metadata"]["deepfake_analysis"] = deepfake_analysis_input

                return {
                    "input": input_data,
                    "layer0": layer0_output,
                    "layer1": layer1_output,
                    "layer2": layer2_output,
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

        except Exception as e:
            print(f"[!] Error processing file: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "message": "File analysis failed",
                "traceback": traceback.format_exc()
            }

    finally:
        # Cleanup: Remove temporary file
        if file_path.exists():
            file_path.unlink()


# -----------------------------
# EMAIL MANAGEMENT ENDPOINTS
# -----------------------------
def load_emails():
    """Load emails from JSON file"""
    try:
        with open("emails.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


@app.get("/emails")
def get_all_emails():
    """Get all emails from JSON file"""
    emails = load_emails()
    return {
        "count": len(emails),
        "emails": emails
    }


@app.get("/emails/{email_id}")
def get_email(email_id: int):
    """Get a specific email by ID"""
    emails = load_emails()
    for email in emails:
        if email["id"] == email_id:
            return email
    return {"error": "Email not found"}


@app.post("/emails/{email_id}/analyze")
def analyze_email(email_id: int):
    """Analyze a specific email - sends only body through pipeline"""
    emails = load_emails()
    email = None
    for e in emails:
        if e["id"] == email_id:
            email = e
            break

    if not email:
        return {"error": "Email not found"}

    # Send ONLY the body through the analysis pipeline
    text = email['body']

    # Call the main analyze function with just the body
    response = analyze(text)

    # Add email metadata to response
    response["email"] = {
        "id": email["id"],
        "subject": email["subject"],
        "body": email["body"]
    }

    return response