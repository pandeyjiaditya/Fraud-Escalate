from layer1_heuristics.heuristic_engine import run_heuristics

data = {
    "type": "text",
    "clean_text": "verify your account immediately and enter otp at http://fakebank.com",
    "features": {}
}

result = run_heuristics(data)

print(result)