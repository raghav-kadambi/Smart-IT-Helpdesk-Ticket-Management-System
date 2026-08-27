"""
classifier.py
-------------
Rule-based (keyword) ticket category classification.

This is NOT machine learning or AI.
It only counts how many keywords from each category appear in the description.
"""

# Keywords are stored in lowercase so matching is case-insensitive.
CATEGORY_KEYWORDS = {
    "Network": ["wifi", "wi-fi", "internet", "router", "network", "connection", "lan", "vpn"],
    "Hardware": ["keyboard", "mouse", "screen", "laptop", "printer", "monitor", "cpu", "battery"],
    "Software": ["software", "application", "install", "installation", "program", "update", "license"],
    "Security": ["virus", "malware", "phishing", "password", "hacked", "security", "otp", "unauthorized"],
}

# Fixed order is used only when two categories have the same keyword count.
CATEGORY_ORDER = ["Network", "Hardware", "Software", "Security"]


def classify_ticket(description):
    """
    Return one category: Network, Hardware, Software, Security, or Other.

    Algorithm (easy to explain in an interview):
    1. Convert the description to lowercase.
    2. For each category, count how many of its keywords appear in the text.
    3. Choose the category with the highest count.
    4. If the highest count is 0, return "Other".
    5. If there is a tie, pick the first category in CATEGORY_ORDER.
    """
    if not description:
        return "Other"

    text = description.lower()
    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        match_count = 0
        for keyword in keywords:
            if keyword in text:
                match_count += 1
        scores[category] = match_count

    highest_score = max(scores.values())
    if highest_score == 0:
        return "Other"

    for category in CATEGORY_ORDER:
        if scores[category] == highest_score:
            return category

    return "Other"


def get_match_details(description):
    """
    Optional helper for debugging / interview explanation.
    Returns the keyword score for every category.
    """
    text = (description or "").lower()
    details = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [word for word in keywords if word in text]
        details[category] = matched
    return details
