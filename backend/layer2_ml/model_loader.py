import pickle
import os

# 🔥 Get backend root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MODEL_DIR = os.path.join(BASE_DIR, "models")


def load_models():

    vectorizer_path = os.path.join(MODEL_DIR, "vectorizer.pkl")
    model_path = os.path.join(MODEL_DIR, "text_model.pkl")

    print("🔍 Looking for models in:", MODEL_DIR)

    if not os.path.exists(vectorizer_path) or not os.path.exists(model_path):
        raise Exception(f"❌ ML model not found in {MODEL_DIR}. Run train.py first.")

    with open(vectorizer_path, "rb") as f:
        vectorizer = pickle.load(f)

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    return vectorizer, model