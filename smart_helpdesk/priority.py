"""
priority.py
-----------
Converts urgency and impact into a numeric score and a priority label.
"""

# Simple mapping that is easy to remember and explain.
LEVEL_SCORES = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
}


def calculate_priority(urgency, impact):
    """
    Return (priority_label, priority_score).

    Formula:
        priority_score = urgency_score + impact_score

    Mapping:
        2-3 -> LOW
        4   -> MEDIUM
        5   -> HIGH
        6   -> CRITICAL

    Example:
        High urgency (3) + High impact (3) = 6 -> CRITICAL
    """
    if urgency not in LEVEL_SCORES:
        raise ValueError("Please select a valid urgency (Low, Medium, or High).")
    if impact not in LEVEL_SCORES:
        raise ValueError("Please select a valid impact (Low, Medium, or High).")

    urgency_score = LEVEL_SCORES[urgency]
    impact_score = LEVEL_SCORES[impact]
    priority_score = urgency_score + impact_score

    if priority_score <= 3:
        priority_label = "LOW"
    elif priority_score == 4:
        priority_label = "MEDIUM"
    elif priority_score == 5:
        priority_label = "HIGH"
    else:
        priority_label = "CRITICAL"

    return priority_label, priority_score
