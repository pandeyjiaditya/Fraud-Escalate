import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer2_ml.ml_engine import run_ml_model

data = {
    "type": "text",
    "clean_text": "verify your account immediately"
}

result = run_ml_model(data)

print(result)