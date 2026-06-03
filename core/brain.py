from core.intent import detect_intent

def brain(text, context, memory, dialogue):

    text = text.lower().strip()
    intent = detect_intent(text)

    print("[INTENT]", intent)

    # -----------------------
    # STANDBY STATE
    # -----------------------
    if intent == "standby":
        dialogue.set_state("standby")

        return {
            "skill": "system",
            "confidence": 1.0,
            "plan": [
                {"action": "standby", "value": None}
            ]
        }

    # -----------------------
    # CHAT MODE
    # -----------------------
    if intent == "chat":

        return {
            "skill": "chat",
            "confidence": 1.0,
            "plan": [
                {"action": "speak", "value": "I'm here sir."}
            ]
        }

    # -----------------------
    # YOUTUBE MODE (no skills needed anymore)
    # -----------------------
    if intent == "youtube":

        return {
            "skill": "youtube",
            "confidence": 1.0,
            "plan": [
                {"action": "open_url", "value": "https://youtube.com"}
            ]
        }

    # -----------------------
    # FALLBACK → skills system
    # -----------------------
    best_skill = None
    best_score = 0.0
    best_plan = []

    for skill in SKILL_REGISTRY:

        score = skill.can_handle(text)

        if score < 0.45:
            continue

        if score <= best_score:
            continue

        plan, _ = skill.handle(text, context)

        if plan:
            best_skill = skill
            best_score = score
            best_plan = plan

    if not best_skill:
        return {
            "skill": None,
            "confidence": 0.0,
            "plan": []
        }

    return {
        "skill": best_skill.__class__.__name__,
        "confidence": best_score,
        "plan": best_plan
    }