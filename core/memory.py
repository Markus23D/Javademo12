import json
import os


class Memory:
    def __init__(self):
        self.file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "memory.json"
        )

        self.history = []
        self.facts = {}
        self.last_intent = None
        self.last_command = None
        self.last_response = None

        self.load()

    def load(self):
        if not os.path.exists(self.file_path):
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.history = data.get("history", [])
            self.facts = data.get("facts", {})
            self.last_intent = data.get("last_intent")
            self.last_command = data.get("last_command")
            self.last_response = data.get("last_response")

        except Exception as e:
            print("[MEMORY LOAD ERROR]", e)

    def save(self):
        data = {
            "history": self.history,
            "facts": self.facts,
            "last_intent": self.last_intent,
            "last_command": self.last_command,
            "last_response": self.last_response
        }

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("[MEMORY SAVE ERROR]", e)

    def remember_command(self, text, intent, plan):
        self.last_command = text
        self.last_intent = intent
        self.last_response = plan

        self.history.append({
            "text": text,
            "intent": intent,
            "plan": plan
        })

        if len(self.history) > 50:
            self.history.pop(0)

        self.save()

    def remember_fact(self, key, value):
        self.facts[key.lower()] = value
        self.save()

    def recall_fact(self, key):
        return self.facts.get(key.lower())


memory = Memory()


def update_memory(text, intent, plan):
    memory.remember_command(text, intent, plan)