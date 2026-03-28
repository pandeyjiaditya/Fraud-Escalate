import re
import requests
from typing import Dict, List, Tuple, Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# URL regex pattern
URL_PATTERN = r"https?://\S+(?=[\s,.\)\]]*(?:$|\s|\)|\.|\,|\]))"

# TinyBERT model for phishing/legitimacy detection
MODEL_NAME = "huawei-noah/TinyBERT_General_6L_768D"
PHISHING_MODEL = "bert-base-uncased"  # Fallback for fine-tuning

_tokenizer = None
_model = None


def _load_tinybert_model():
    """Lazy load TinyBERT model on first use"""
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        try:
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            _model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
            _model.eval()
            print(f"[*] TinyBERT model loaded: {MODEL_NAME}")
        except Exception as e:
            print(f"[!] Failed to load TinyBERT: {e}. Using fallback model...")
            _tokenizer = AutoTokenizer.from_pretrained(PHISHING_MODEL)
            _model = AutoModelForSequenceClassification.from_pretrained(PHISHING_MODEL, num_labels=2)
            _model.eval()


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    urls = re.findall(URL_PATTERN, text)
    return list(set(urls))  # Remove duplicates


def fetch_url_content(url: str, timeout: int = 3) -> Optional[str]:
    """
    Fetch website content from URL

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds (reduced from 5 to 3 for faster fails)

    Returns:
        Website text content or None if fetch fails
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        response.raise_for_status()

        # Extract text, limit to first 1000 chars
        text = response.text[:1000]
        return text
    except requests.RequestException as e:
        print(f"[!] Failed to fetch URL {url}: {e}")
        return None


def score_url_with_tinybert(url: str, website_content: Optional[str]) -> Tuple[int, float]:
    """
    Score URL for phishing/legitimacy using TinyBERT

    Args:
        url: The URL being analyzed
        website_content: Website content fetched from URL

    Returns:
        Tuple of (score: 1-100, confidence: 0.0-1.0)
        Score: higher = more suspicious/phishing-like
    """
    _load_tinybert_model()

    # If no content fetched, use URL characteristics for scoring
    if website_content is None:
        url_score = _score_url_characteristics(url)
        return url_score, 0.4  # Lower confidence for URL-only analysis

    try:
        # Prepare input: URL + website content
        input_text = f"Website URL: {url}. Content: {website_content[:500]}"

        # Tokenize
        inputs = _tokenizer(
            input_text,
            max_length=512,
            truncation=True,
            return_tensors="pt"
        )

        # Predict
        with torch.no_grad():
            outputs = _model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1).cpu().numpy()[0]

        # logits[0] = legitimate, logits[1] = phishing/suspicious
        phishing_prob = float(probabilities[1])

        # Convert to 1-100 scale (higher = more suspicious)
        score = int(phishing_prob * 100)
        confidence = max(probabilities)

        return score, float(confidence)

    except Exception as e:
        print(f"⚠ Error scoring URL with TinyBERT: {e}")
        # Fallback to URL characteristics
        url_score = _score_url_characteristics(url)
        return url_score, 0.3


def _score_url_characteristics(url: str) -> int:
    """
    Score URL based on characteristics (fallback method)
    Returns 1-100 score where higher = more suspicious
    """
    score = 50  # Neutral baseline

    # Suspicious keywords
    suspicious_keywords = [
        "login", "verify", "confirm", "update", "secure", "account",
        "paypal", "bank", "amazon", "apple", "microsoft"
    ]

    url_lower = url.lower()

    # Check for suspicious keywords
    keyword_count = sum(1 for kw in suspicious_keywords if kw in url_lower)
    score += keyword_count * 5

    # Long URLs are often suspicious
    if len(url) > 50:
        score += 10
    elif len(url) > 100:
        score += 20

    # Obfuscated domains
    if ".tk" in url or ".ml" in url or ".ga" in url or ".cf" in url:
        score += 15

    # IP addresses instead of domain names
    if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url):
        score += 25

    # URL shorteners
    if any(shortener in url for shortener in ["bit.ly", "tinyurl", "goo.gl", "short.link"]):
        score += 20

    # No HTTPS
    if url.startswith("http://"):
        score += 10

    score = min(score, 100)  # Cap at 100
    return score


def process_url_for_fraud_analysis(text: str) -> Dict:
    """
    Main function: Extract URLs, fetch content, and score with TinyBERT
    OPTIMIZED: Uses parallel processing instead of sequential

    Args:
        text: Input text that may contain URLs

    Returns:
        Dict with:
        - urls: List of detected URLs
        - url_scores: List of (url, score, confidence) tuples
        - url_ml_score: Overall score 1-100 (average if multiple URLs)
        - url_ml_confidence: Overall confidence 0.0-1.0
        - has_urls: Boolean
    """
    urls = extract_urls(text)

    if not urls:
        return {
            "urls": [],
            "url_scores": [],
            "url_ml_score": None,
            "url_ml_confidence": None,
            "has_urls": False
        }

    print(f"[*] Detected {len(urls)} URL(s) - Processing in PARALLEL (max 4 concurrent)")

    url_scores = []

    # Parallel URL processing using ThreadPoolExecutor
    # Max 4 concurrent requests to avoid overwhelming network
    with ThreadPoolExecutor(max_workers=min(4, len(urls))) as executor:
        # Submit all URL fetch tasks
        future_to_url = {
            executor.submit(fetch_url_content, url): url for url in urls
        }

        # Process results as they complete
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                website_content = future.result()
                # Score with TinyBERT
                score, confidence = score_url_with_tinybert(url, website_content)
                url_scores.append((url, score, confidence))
                print(f"      {url}: Score {score}/100, Confidence: {confidence:.2f}")
            except Exception as e:
                print(f"      {url}: Error - {e}")
                url_scores.append((url, 50, 0.3))  # Default score for errors

    # Calculate overall score and confidence
    scores = [s for _, s, _ in url_scores]
    confidences = [c for _, _, c in url_scores]

    overall_score = sum(scores) / len(scores) if scores else 0
    overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    return {
        "urls": urls,
        "url_scores": url_scores,
        "url_ml_score": overall_score,
        "url_ml_confidence": overall_confidence,
        "has_urls": len(urls) > 0
    }

    # Calculate overall score and confidence
    scores = [s for _, s, _ in url_scores]
    confidences = [c for _, _, c in url_scores]

    overall_score = sum(scores) / len(scores) if scores else 0
    overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    return {
        "urls": urls,
        "url_scores": url_scores,
        "url_ml_score": overall_score,
        "url_ml_confidence": overall_confidence,
        "has_urls": len(urls) > 0
    }
