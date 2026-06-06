from core.intent import detect_intent
from core.planner import Planner
from core.normalizer import Normalizer
from skills.registry import SKILL_REGISTRY
from core.ai_chat import AIChat


def brain(text, context, memory, dialogue):
    text = text.lower().strip()
    intent = detect_intent(text)

    print("[INTENT]", intent)

    # -----------------------
    # NORMALIZER LEARNING
    # -----------------------
    if text.startswith("when i say ") and " you mean " in text:
        wrong = text.split("when i say ", 1)[1].split(" you mean ", 1)[0].strip()
        correct = text.split(" you mean ", 1)[1].strip()


        Normalizer.learn(wrong, correct)

        return {
            "skill": "normalizer",
            "confidence": 1.0,
            "plan": [
                {"action": "speak", "value": f"Understood sir. When you say {wrong}, I will treat it as {correct}."}
            ]
        }

    # -----------------------
    # CONFIRMATION MODE
    # -----------------------
    if dialogue.state == "confirming":
        if intent == "confirm":
            plan = dialogue.confirm()
            return {
                "skill": "confirmation",
                "confidence": 1.0,
                "plan": plan
            }

        if intent == "cancel":
            dialogue.cancel()
            return {
                "skill": "confirmation",
                "confidence": 1.0,
                "plan": [
                    {"action": "speak", "value": "Cancelled sir."}
                ]
            }

        return {
            "skill": "confirmation",
            "confidence": 1.0,
            "plan": [
                {"action": "speak", "value": "Please say yes or no sir."}
            ]
        }

    # NOTE: standby is handled by SystemSkill (score 1.0) via the skills loop below.

    # -----------------------
    # DANGEROUS SYSTEM COMMANDS (shutdown/restart need confirmation)
    # -----------------------
    if intent == "system":
        dangerous_plan = Planner.build_plan(text)
        dialogue.ask_confirmation(dangerous_plan)

        return {
            "skill": "system",
            "confidence": 1.0,
            "plan": [
                {"action": "speak", "value": "Are you sure sir?"}
            ]
        }

    # -----------------------
    # MEMORY SAVE
    # -----------------------
    if intent == "memory":
        if "my name is" in text:
            name = text.split("my name is", 1)[1].strip()
            memory.remember_fact("name", name)

            return {
                "skill": "memory",
                "confidence": 1.0,
                "plan": [
                    {"action": "speak", "value": f"I'll remember your name is {name}, sir."}
                ]
            }

        if "call me" in text:
            name = text.split("call me", 1)[1].strip()
            memory.remember_fact("preferred_name", name)

            return {
                "skill": "memory",
                "confidence": 1.0,
                "plan": [
                    {"action": "speak", "value": f"Understood. I will call you {name}."}
                ]
            }

    # -----------------------
    # CLEAR CHAT HISTORY
    # -----------------------
    if intent == "clear_chat":
        AIChat.clear_history()
        return {
            "skill": "clear_chat",
            "confidence": 1.0,
            "plan": [{"action": "speak", "value": "Conversation cleared sir. Fresh start."}]
        }

    # -----------------------
    # REGISTER APP
    # Example: "remember that notepad is at C:\Windows\notepad.exe"
    # -----------------------
    if intent == "register_app":
        import json, os

        try:
            # strip leading phrase
            raw = text
            for prefix in ["remember that ", "add app ", "register app "]:
                if raw.startswith(prefix):
                    raw = raw[len(prefix):]
                    break

            name_part, path_part = raw.split(" is at ", 1)
            name = name_part.strip()
            path = path_part.strip()

            commands_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "commands.json")

            with open(commands_path, "r", encoding="utf-8") as f:
                commands = json.load(f)

            commands[f"open {name}"] = {
                "type": "app",
                "path": path,
                "aliases": [name]
            }

            with open(commands_path, "w", encoding="utf-8") as f:
                json.dump(commands, f, indent=2)

            return {
                "skill": "register_app",
                "confidence": 1.0,
                "plan": [{"action": "speak", "value": f"Done sir, I've added {name} to my app list."}]
            }

        except Exception as e:
            print("[REGISTER APP ERROR]", e)
            return {
                "skill": "register_app",
                "confidence": 1.0,
                "plan": [{"action": "speak", "value": "I had trouble registering that app sir. Please try again."}]
            }

    # -----------------------
    # NORMALIZER LIST / FORGET
    # -----------------------
    if intent == "normalizer_list":

        learned = Normalizer.list_learned()

        if not learned:
            msg = "I have no learned corrections sir."
        else:
            items = ", ".join(f"{w} means {c}" for w, c in learned.items())
            msg = f"I have learned the following corrections sir: {items}."

        return {
            "skill": "normalizer",
            "confidence": 1.0,
            "plan": [{"action": "speak", "value": msg}]
        }

    if intent == "normalizer_forget":

        raw = text
        for prefix in ["forget correction ", "forget that "]:
            if raw.startswith(prefix):
                raw = raw[len(prefix):]
                break

        wrong = raw.split(" means ")[0].strip() if " means " in raw else raw.strip()
        success = Normalizer.forget(wrong)

        msg = f"Done sir, I will no longer correct {wrong}." if success else f"I don't have a correction for {wrong} sir."

        return {
            "skill": "normalizer",
            "confidence": 1.0,
            "plan": [{"action": "speak", "value": msg}]
        }

    # -----------------------
    # MEMORY RECALL
    # -----------------------
    if intent == "recall":
        name = memory.recall_fact("preferred_name") or memory.recall_fact("name")

        if name:
            return {
                "skill": "memory",
                "confidence": 1.0,
                "plan": [
                    {"action": "speak", "value": f"You are {name}, sir."}
                ]
            }

        return {
            "skill": "memory",
            "confidence": 1.0,
            "plan": [
                {"action": "speak", "value": "I do not know yet, sir."}
            ]
        }

    # -----------------------
    # PLAY COMMANDS
    # Must happen before BrowserSkill.
    # Example: play bones on youtube
    # -----------------------
    if text.startswith("play "):
        return {
            "skill": "planner",
            "confidence": 1.0,
            "plan": Planner.build_plan(text)
        }

    # -----------------------
    # SEARCH PLANNER
    # Must happen before BrowserSkill.
    # -----------------------
    if (
            text.startswith("search ")
            or text.startswith("google ")
            or text.startswith("look up ")
            or " search " in text
    ):
        return {
            "skill": "planner",
            "confidence": 1.0,
            "plan": Planner.build_plan(text)
        }

    # -----------------------
    # MULTI-COMMAND PLANNER
    # Must happen before skills.
    # Example: open chrome and search facebook
    # Only route here when the split actually yields multiple commands.
    # -----------------------
    if " and " in text or " then " in text or "," in text:
        parts = Planner.split_command(text)

        if len(parts) > 1:
            plan = Planner.build_plan(text)

            if plan:
                return {
                    "skill": "planner",
                    "confidence": 1.0,
                    "plan": plan
                }

    # -----------------------
    # SKILLS SYSTEM
    # -----------------------
    best_skill = None
    best_score = 0.0
    best_plan = []

    for skill in SKILL_REGISTRY:
        score = skill.can_handle(text)

        if score <= best_score:
            continue

        plan, confidence = skill.handle(text, context)

        if plan:
            best_skill = skill
            best_score = score
            best_plan = plan

    if best_skill and best_score >= 0.45:
        return {
            "skill": best_skill.__class__.__name__,
            "confidence": best_score,
            "plan": best_plan
        }

    # -----------------------
    # FALLBACK PLANNER
    # -----------------------
    plan = Planner.build_plan(text)

    if plan:
        return {
            "skill": "planner",
            "confidence": 0.6,
            "plan": plan
        }

    # -----------------------
    # AI CHAT FALLBACK
    # -----------------------
    answer = AIChat.ask(text, memory)

    return {
        "skill": "ai_chat",
        "confidence": 1.0,
        "plan": [
            {"action": "speak", "value": answer}
        ]
    }