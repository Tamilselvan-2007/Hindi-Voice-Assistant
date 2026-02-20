# assistant_core.py

from datetime import datetime

def detect_intent(text):
    text = text.strip()

    if any(word in text for word in ["समय", "टाइम", "घड़ी"]):
        return "TIME_QUERY"

    elif any(word in text for word in ["मौसम", "तापमान"]):
        return "WEATHER_QUERY"

    elif any(word in text for word in ["नमस्ते", "हैलो"]):
        return "GREETING"

    else:
        return "UNKNOWN"


def generate_response(intent):
    if intent == "TIME_QUERY":
        now = datetime.now()
        return f"अभी समय है {now.hour} बजकर {now.minute} मिनट"

    elif intent == "WEATHER_QUERY":
        return "आज का मौसम साफ और सुहावना है"

    elif intent == "GREETING":
        return "नमस्ते, मैं आपकी कैसे सहायता कर सकती हूँ"

    else:
        return "माफ कीजिए, मैं समझ नहीं पाई"
