def detect_intent(text: str) -> str:
    text = text.lower().strip()

    if text in ["yes", "yeah", "yep", "confirm", "do it"]:
        return "confirm"

    if text in ["no", "nope", "cancel", "don't", "stop"]:
        return "cancel"

    if any(w in text for w in ["standby", "stand by", "sleep", "go idle", "go to sleep"]):
        return "standby"

    if text.startswith("type "):
        return "typing"

    if any(w in text for w in ["shutdown", "restart"]):
        return "system"

    if any(w in text for w in ["youtube", "you too", "you tube", "watch videos"]):
        return "youtube"

    if any(w in text for w in ["open", "launch", "start"]):
        return "app"

    if any(w in text for w in ["my name is", "remember that", "call me"]):
        return "memory"

    if any(w in text for w in ["what is my", "who am i", "what do you remember"]):
        return "recall"

    return "chat"