from fastapi import FastAPI

# Input Layer
from input_layer.input_handler import process_text_input

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

    # 🔹 Step 2: Layer 0 (Privacy + Features)
    layer0_output = process_privacy_layer(input_data)

    # 🔹 Step 3: Layer 1 (Heuristic Detection)
    layer1_output = run_heuristics(layer0_output)
    heuristic_score = layer1_output.get("heuristic_score", 0)

    # 🔥 Step 4: Smart Routing for ML
    if heuristic_score >= 120:
        layer2_output = {
            "ml_probability": 1.0,
            "ml_prediction": "fraud",
            "confidence": 1.0,
            "note": "Skipped ML (high risk from heuristics)"
        }

    elif heuristic_score <= 20:
        layer2_output = {
            "ml_probability": 0.0,
            "ml_prediction": "safe",
            "confidence": 1.0,
            "note": "Skipped ML (low risk from heuristics)"
        }

    else:
        layer2_output = run_ml_model(layer0_output)

    # 🔹 Step 5: Risk Engine (Final Decision)
    final_output = make_decision(layer1_output, layer2_output)

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