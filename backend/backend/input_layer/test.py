from input_layer.input_handler import process_text_input, process_file_input

text_tests = [
    "Verify your bank account immediately",
    "https://paypal-login-security.com",
    "support@bank.com"
]

for t in text_tests:
    result = process_text_input(t)
    print(result)

file_tests = [
    "test_document.txt",
    "scam_image.jpg",
    "phishing_video.mp4",
    "suspicious_audio.wav"
]

print("\n--- File Tests ---")
for f in file_tests:
    # Notice we expect an exception for missing actual files like 'test_document.txt' 
    # since we would attempt to read it if it's a doc format.
    # To avoid crashing the test reading fake files, let's only test media formats that return outright.
    if f.endswith((".jpg", ".mp4", ".wav")):
        result = process_file_input(f)
        print(result)