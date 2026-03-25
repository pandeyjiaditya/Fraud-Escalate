# 🛡️ Fraud Escalate — Multi-Layer Fraud Detection System

A multi-layer AI-powered fraud detection backend built with **FastAPI**. It analyzes text (and media) input through a structured pipeline of heuristics, machine learning, and LLM-based reasoning to detect phishing, credential theft, financial scams, and other fraud signals.

---

## 🚀 Features

- **Multi-modal input support** — text, PDF, DOCX, images, **audio** (with Whisper transcription), and video
- **Audio-to-Text** — Automatic transcription using OpenAI's Whisper model (supports MP3, WAV, FLAC, AAC, OGG, M4A, WMA)
- **Privacy-first** — PII stripped before any analysis (emails, Aadhaar, PAN, IFSC, card numbers, OTPs)
- **Rule-based heuristics** — fast, interpretable fraud signal detection
- **Smart ML routing** — ML model only invoked when heuristic score is ambiguous
- **LLM explanation** — Mistral (via Ollama) generates a human-readable explanation of every decision
- **Risk engine** — combines all signals into a final risk score and decision (ALLOW / MONITOR / REVIEW / BLOCK)

---

## 🏗️ Project Structure

```
Fraud Escalate/
└── backend/
    ├── main.py                     # FastAPI app & pipeline orchestration
    ├── requirements.txt
    │
    ├── input_layer/                # Step 1 — Input handling
    │   ├── input_handler.py        # Routes text/file to correct reader
    │   ├── file_segregator.py      # Detects input type (text/image/audio/video)
    │   └── file_readers.py         # Readers for TXT, PDF, DOCX
    │
    ├── layer0_privacy/             # Step 2 — Privacy & feature extraction
    │   ├── pii_removal.py          # Strips email, phone, Aadhaar, PAN, IFSC, card, OTP
    │   ├── normalization.py        # Lowercasing, whitespace cleanup
    │   ├── feature_extraction.py   # Extracts boolean features (urgency, sensitive keywords)
    │   └── hashing.py              # Input fingerprinting
    │
    ├── layer1_heuristics/          # Step 3 — Rule-based detection
    │   ├── heuristic_engine.py     # Aggregates all rule scores
    │   ├── phishing_rules.py       # Phishing keyword patterns
    │   ├── credential_rules.py     # Credential theft patterns
    │   ├── url_rules.py            # Suspicious/long URL detection
    │   ├── intent_rules.py         # Financial intent signals
    │   └── urgency_rules.py        # Urgency language detection
    │
    ├── layer2_ml/                  # Step 4 — ML classification
    │   ├── ml_engine.py            # TF-IDF + classifier inference + feature boosting
    │   ├── model_loader.py         # Loads saved vectorizer & model
    │   ├── text_model.py           # Model training/evaluation helpers
    │   └── train.py                # Training entry point
    │
    ├── layer3_llm/                 # Step 6 — LLM explanation
    │   ├── llm_engine.py           # Orchestrates prompt → Ollama → explanation
    │   ├── prompt_builder.py       # Builds structured prompt from all layer outputs
    │   └── ollama_client.py        # HTTP client for local Ollama (Mistral)
    │
    ├── risk_engine/                # Step 5 — Final decision
    │   ├── decision_engine.py      # Maps scores to ALLOW/MONITOR/REVIEW/BLOCK
    │   └── scoring.py              # Dynamic weighted scoring (heuristics + ML)
    │
    └── datasets/
        └── phishing_data.csv       # Training dataset
```

---

## ⚙️ Analysis Pipeline

```
Input
  │
  ▼
[Input Layer]        — Detect type, read content (text/PDF/DOCX/image/audio/video)
  │
  ▼
[Layer 0 — Privacy]  — Remove PII, normalize text, extract features
  │
  ▼
[Layer 1 — Heuristics] — Score against phishing, credential, URL, intent, urgency rules
  │
  ├─ Score ≥ 120 → BLOCK immediately (skip ML)
  ├─ Score ≤ 20  → ALLOW immediately (skip ML)
  └─ Score 21–119 → continue ↓
  │
  ▼
[Layer 2 — ML]       — TF-IDF vectorization + classifier + feature boosting
  │
  ▼
[Risk Engine]        — Dynamic weighted score → ALLOW / MONITOR / REVIEW / BLOCK
  │
  ▼
[Layer 3 — LLM]      — Mistral generates a plain-English explanation
  │
  ▼
Final JSON Response
```

### Decision Thresholds

| Risk Score | Decision   |
| ---------- | ---------- |
| 0 – 30     | ✅ ALLOW   |
| 31 – 60    | 👁️ MONITOR |
| 61 – 80    | 🔍 REVIEW  |
| 81 – 100   | 🚫 BLOCK   |

---

## 🔌 API Endpoints

| Method | Endpoint        | Description                                      |
| ------ | --------------- | ------------------------------------------------ |
| GET    | `/`             | Health check                                     |
| GET    | `/health`       | Status check                                     |
| POST   | `/analyze`      | Analyze text input                               |
| POST   | `/analyze-file` | Upload and analyze files (audio, PDF, DOCX, TXT) |

### Example Request (Text)

```bash
curl -X POST "http://127.0.0.1:8000/analyze?text=Your+account+has+been+compromised+click+here+to+verify+your+OTP"
```

### Example Request (Audio File)

```bash
curl -X POST "http://127.0.0.1:8000/analyze-file" \
  -F "file=@suspicious_call.mp3"
```

**Python Example:**

```python
import requests

with open("audio_message.mp3", "rb") as f:
    files = {"file": ("audio.mp3", f, "audio/mpeg")}
    response = requests.post("http://127.0.0.1:8000/analyze-file", files=files)
    print(response.json())
```

### Example Response

```json
{
  "input": { "type": "text", "content": "...", "metadata": { "timestamp": "..." } },
  "layer0": { "clean_text": "...", "features": { "has_urgent_words": true, ... } },
  "layer1": { "heuristic_score": 90, "flags": ["phishing", "urgency", "credential_theft"] },
  "layer2": { "ml_probability": 0.87, "ml_prediction": "fraud", "confidence": 0.74 },
  "final": { "risk_score": 88.5, "decision": "BLOCK", "reason": "Combined heuristic + ML analysis" },
  "layer3": { "explanation": "This message exhibits strong phishing indicators..." }
}
```

---

## 🧰 Tech Stack

| Category      | Libraries / Tools                            |
| ------------- | -------------------------------------------- |
| API Framework | FastAPI, Uvicorn                             |
| ML / NLP      | scikit-learn, XGBoost, Transformers, PyTorch |
| LLM           | Ollama (Mistral, local)                      |
| Audio-to-Text | OpenAI Whisper                               |
| Privacy / PII | Presidio Analyzer & Anonymizer, regex        |
| File Parsing  | pdfplumber, python-docx                      |
| Audio         | librosa, ffmpeg                              |
| URL Analysis  | tldextract                                   |
| Data          | pandas, numpy                                |

---

## 🛠️ Setup & Running

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you plan to use audio transcription, you also need **ffmpeg** installed on your system:

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 2. Start Ollama with Mistral (for LLM layer)

```bash
ollama run mistral
```

### 3. Start the API server

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

---

## 📊 PII Redacted Before Analysis

The privacy layer strips the following before any ML or LLM processing:

- Email addresses
- Indian phone numbers (10-digit, starting with 6–9)
- Aadhaar numbers (12-digit)
- PAN card numbers
- IFSC codes
- Bank account numbers (9–18 digits)
- Credit/debit card numbers
- OTPs (4–6 digits)

---

## 📁 Heuristic Scoring Map

| Flag                                   | Score         |
| -------------------------------------- | ------------- |
| `strong_phishing`                      | +50           |
| `credential_theft`                     | +50           |
| `suspicious_url`                       | +40           |
| `phishing`                             | +30           |
| `financial_intent`                     | +20           |
| `urgency`                              | +20           |
| `long_url`                             | +10           |
| **urgency + credential_theft (combo)** | **+20 bonus** |

---

## 📄 License

MIT
