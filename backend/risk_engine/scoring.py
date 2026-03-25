import math
from typing import Dict, List, Optional


# -----------------------
# Utilities (internal)
# -----------------------

def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _normalize_score(score: Optional[float]) -> float:
    return _clamp((score or 0) / 100.0, 0.0, 1.0)


def _normalize_conf(c: Optional[float]) -> float:
    return _clamp(c or 0.0, 0.0, 1.0)


def _safe_div(n: float, d: float) -> float:
    return n / d if d > 1e-12 else 0.0


def _logistic(x: float, k: float, theta: float) -> float:
    z = _clamp(k * (x - theta), -60.0, 60.0)
    return 1.0 / (1.0 + math.exp(-z))


def _weighted_variance(p: List[float], w: List[float]) -> float:
    if sum(w) == 0:
        return 1.0
    mean = _safe_div(sum(pi * wi for pi, wi in zip(p, w)), sum(w))
    return _safe_div(sum(wi * (pi - mean) ** 2 for pi, wi in zip(p, w)), sum(w))


# -----------------------
# Signal Schemas
# -----------------------

_SIGNAL_SCHEMAS = {
    "email": [
        {"name": "heuristic", "base_weight": 0.35},
        {"name": "ml_text",   "base_weight": 0.40},
        {"name": "llm",       "base_weight": 0.25},
        {"name": "url_ml",    "base_weight": 0.45},
    ],
    "file": [
        {"name": "heuristic", "base_weight": 0.30},
        {"name": "ml_text",   "base_weight": 0.40},
        {"name": "llm",       "base_weight": 0.20},
    ],
    "audio": [
        {"name": "heuristic",   "base_weight": 0.20},
        {"name": "ml_text",     "base_weight": 0.25},
        {"name": "deepfake_ml", "base_weight": 0.50},
        {"name": "llm",         "base_weight": 0.15},
    ]
}


# -----------------------
# Public API
# -----------------------

def calculate_risk_score(layer1, layer2=None, context_type: str = "email", meta: Optional[Dict] = None) -> float:
    """
    Compute risk score (0–100) using advanced signal fusion

    Args:
        layer1: dict with heuristic and confidence
        layer2: dict with ml signals (ml_text, llm, url_ml, deepfake_ml, etc.)
        context_type: "email" | "file" | "audio"
        meta: optional dict with OCR info, URL presence, etc.

    Returns:
        float: risk score (0–100)
    """

    schema = _SIGNAL_SCHEMAS.get(context_type)
    if not schema:
        schema = _SIGNAL_SCHEMAS.get("email")

    meta = meta or {}

    # ---- Meta controls
    ocr_used = meta.get("ocr_used", False)
    ocr_quality = meta.get("ocr_quality", 0.8)
    has_url = meta.get("has_url", None)

    discard_text_signals = ocr_used and ocr_quality < 0.2

    gamma = 2.5

    weighted_scores = []
    weights = []
    dominance = 0.0

    # -----------------------
    # Build signals
    # -----------------------

    # Prepare scores and confidences from layers
    scores = {}
    confidences = {}

    # Layer 1 signals
    if layer1:
        scores["heuristic"] = layer1.get("heuristic_score", 0)
        confidences["heuristic"] = layer1.get("confidence", 0)

    # Layer 2 signals
    if layer2:
        if "ml_text_score" in layer2:
            scores["ml_text"] = layer2["ml_text_score"]
            confidences["ml_text"] = layer2.get("ml_text_confidence", 0)
        if "llm_score" in layer2:
            scores["llm"] = layer2["llm_score"]
            confidences["llm"] = layer2.get("llm_confidence", 0)
        if "url_ml_score" in layer2:
            scores["url_ml"] = layer2["url_ml_score"]
            confidences["url_ml"] = layer2.get("url_ml_confidence", 0)
        if "deepfake_score" in layer2:
            scores["deepfake_ml"] = layer2["deepfake_score"]
            confidences["deepfake_ml"] = layer2.get("deepfake_confidence", 0)

    for sig in schema:
        name = sig["name"]

        # ---- Explicit URL presence handling
        if name == "url_ml":
            if has_url is False:
                continue
            if has_url is True and name not in scores:
                continue

        # ---- Default skip if missing
        if name not in scores:
            continue

        p = _normalize_score(scores.get(name))
        c = _normalize_conf(confidences.get(name))

        # ---- OCR handling
        if name in ["ml_text", "llm"]:
            if discard_text_signals:
                continue
            if ocr_used:
                c *= (0.5 + 0.5 * ocr_quality)

        # ---- Stabilized confidence weighting
        w = sig["base_weight"] * (0.3 + 0.7 * (c ** gamma))

        if w > 0:
            weighted_scores.append(p)
            weights.append(w)

            # ---- Improved dominance metric
            dominance = max(dominance, p * (0.6 + 0.4 * c))

    if not weights:
        return 0.0

    # -----------------------
    # Fusion
    # -----------------------

    weighted_mean = _safe_div(
        sum(p * w for p, w in zip(weighted_scores, weights)),
        sum(weights)
    )

    max_weight = max(weights)
    max_signal = max(
        p * (0.5 + 0.5 * (w / max_weight))
        for p, w in zip(weighted_scores, weights)
    )

    # ---- Agreement (Gaussian)
    variance = _weighted_variance(weighted_scores, weights)
    agreement = math.exp(-4.0 * variance)

    # ---- Partial disagreement protection
    strong_signals = [p for p in weighted_scores if p > 0.7]
    if len(strong_signals) >= 2:
        agreement = max(agreement, 0.7)

    # ---- Balanced fusion
    eta = _clamp(0.5 + 0.4 * agreement, 0.5, 0.9)
    fused_score = eta * max_signal + (1 - eta) * weighted_mean

    # ---- Dominance override
    if dominance > 0.85:
        fused_score = max(fused_score, dominance)

    # -----------------------
    # Calibration
    # -----------------------

    params = {
        "email": (8.0, 0.55),
        "file":  (10.0, 0.60),
        "audio": (9.0, 0.58),
    }

    k, theta = params.get(context_type, (8.0, 0.55))
    base_risk = _logistic(fused_score, k, theta)

    # ---- Additive boost
    boost = 0.12 * agreement * (1.0 - base_risk) * fused_score
    final_score = _clamp(base_risk + boost, 0.0, 0.99)

    return round(final_score * 100, 2)