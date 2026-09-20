import re


def needs_weather(message: str) -> bool:
    text = message.lower()
    return any(word in text for word in ["weather", "forecast", "rain", "tomorrow", "next week", "indoor or outdoor"])


def needs_currency(message: str) -> bool:
    text = message.lower()
    return any(word in text for word in ["convert", "currency", "sgd", "inr", "usd", "budget"])


def needs_rag(message: str) -> bool:
    text = message.lower()
    keywords = [
        "singapore", "itinerary", "attraction", "neighbourhood", "neighborhood",
        "food", "family", "children", "transport", "mrt", "indoor", "outdoor",
        "culture", "visit", "plan", "trip", "sightseeing"
    ]
    return any(word in text for word in keywords)


def parse_days(message: str) -> int:
    text = message.lower()
    match = re.search(r"(\d+)\s*[- ]?day", text)
    if match:
        return max(1, min(int(match.group(1)), 7))
    if "three-day" in text or "three day" in text:
        return 3
    if "next week" in text:
        return 3
    return 3


def parse_currency_request(message: str) -> tuple[float, str, str] | None:
    text = message.upper().replace(",", "")
    currencies = "INR|SGD|USD|EUR|GBP"

    match = re.search(rf"({currencies})\s*(\d+(?:\.\d+)?)\s*(?:TO|INTO|IN)\s*({currencies})", text)
    if match:
        return float(match.group(2)), match.group(1), match.group(3)

    match = re.search(rf"(\d+(?:\.\d+)?)\s*({currencies})\s*(?:TO|INTO|IN)\s*({currencies})", text)
    if match:
        return float(match.group(1)), match.group(2), match.group(3)

    match = re.search(rf"({currencies})\s*(\d+(?:\.\d+)?)", text)
    if match:
        source = match.group(1)
        target = "SGD" if source != "SGD" else "INR"
        return float(match.group(2)), source, target

    if "BUDGET" in text:
        return 60000.0, "INR", "SGD"

    return None
