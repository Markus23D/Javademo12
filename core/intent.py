def detect_intent(text: str) -> str:

    text = text.lower().strip()

    if any(w in text for w in ["youtube", "watch videos", "play videos", "you too", "you tube"]):
        return "youtube"

    if any(w in text for w in ["no thanks", "stop", "standby", "stand by", "sleep", "go idle", "go to sleep"]):
        return "standby"

    if text.startswith("type "):
        return "typing"

    if any(w in text for w in ["open", "launch", "start"]):
        return "app"

    if any(w in text for w in ["how are you", "tell me", "what can you do"]):
        return "chat"

    return "unknown"