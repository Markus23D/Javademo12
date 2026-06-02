memory = {
    "history": [],
    "last_command": None,
    "last_plan": None
}


MAX_HISTORY = 5


def update_memory(command, plan):
    memory["history"].append((command, plan))

    if len(memory["history"]) > MAX_HISTORY:
        memory["history"] = memory["history"][-MAX_HISTORY:]