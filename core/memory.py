memory = {
    "history": [],
    "last_intent": None,
    "last_command": None,
    "last_response": None
}

def update_memory(text, intent, plan):
    memory["last_command"] = text
    memory["last_intent"] = intent
    memory["last_response"] = plan

    memory["history"].append({
        "text": text,
        "intent": intent,
        "plan": plan
    })

    if len(memory["history"]) > 20:
        memory["history"] = memory["history"][-20:]