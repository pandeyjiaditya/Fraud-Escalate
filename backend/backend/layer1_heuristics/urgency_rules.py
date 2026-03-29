URGENCY_WORDS = [
    "urgent",
    "immediately",
    "within 24 hours",
    "act now",
    "limited time",
    "asap",
    "expire",
    "suspended"
]


def check_urgency(text):

    for word in URGENCY_WORDS:
        if word in text:
            return ["urgency"]

    return []