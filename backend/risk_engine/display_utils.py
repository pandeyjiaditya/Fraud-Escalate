"""
Display utilities - All frontend presentation logic calculated on backend
"""


def get_risk_level(score: float) -> str:
    """
    Convert risk score to risk level label.

    Args:
        score: Risk score (0-100)

    Returns:
        str: Risk level (CRITICAL, HIGH, MEDIUM, LOW)
    """
    if score >= 70:
        return "CRITICAL"
    elif score >= 40:
        return "HIGH"
    elif score >= 20:
        return "MEDIUM"
    else:
        return "LOW"


def get_risk_color(score: float) -> str:
    """
    Convert risk score to color indicator.

    Args:
        score: Risk score (0-100)

    Returns:
        str: Color code (red, orange, green)
    """
    if score >= 70:
        return "red"
    elif score >= 40:
        return "orange"
    else:
        return "green"


def format_risk_display(score: float) -> dict:
    """
    Format all risk display properties at once.

    Args:
        score: Risk score (0-100)

    Returns:
        dict with level, color, and severity_indicator
    """
    return {
        "level": get_risk_level(score),
        "color": get_risk_color(score),
        "severity_indicator": "🚨" if score >= 70 else ("⚠️" if score >= 40 else "✓")
    }
