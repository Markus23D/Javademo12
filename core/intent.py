def detect_intent(text: str) -> str:

    text = text.lower()

    if any(w in text for w in ["youtube", "watch videos", "play videos"]):
        return "youtube"

    if any(w in text for w in ["open", "launch", "start"]):
        return "app"

    if any(w in text for w in ["no thanks", "stop", "standby", "sleep"]):
        return "standby"

    if any(w in text for w in ["how are you", "tell me", "what can you do"]):
        return "chat"

    return "unknown"