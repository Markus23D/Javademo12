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

    if any(p in text for p in ["clear chat", "forget our conversation", "reset conversation", "clear history"]):
        return "clear_chat"

    if any(p in text for p in ["what corrections", "what have you learned", "list corrections", "show corrections"]):
        return "normalizer_list"

    if any(p in text for p in ["remember that", "add app", "register app"]) and " is at " in text:
        return "register_app"

    if text.startswith("forget correction ") or text.startswith("forget that "):
        return "normalizer_forget"

    return "chat"