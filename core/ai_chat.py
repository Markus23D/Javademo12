import requests
from collections import deque

_HISTORY_LIMIT = 10  # max turns (user + assistant pairs) to keep


class AIChat:

    _history: deque = deque()

    @classmethod
    def ask(cls, text, memory=None):
        name = "sir"

        if memory:
            remembered = memory.recall_fact("preferred_name") or memory.recall_fact("name")
            if remembered:
                name = remembered

        system = (
            f"You are J.A.R.V.I.S — Just A Rather Very Intelligent System. "
            f"You are a personal desktop AI assistant built for {name}. "
            f"You have no connection to Tony Stark, Stark Industries, or any fictional universe. "
            f"You are real software running on {name}'s computer, assisting with their daily tasks. "
            f"You are calm, composed, and highly capable with a dry British wit. "
            f"You speak in short, precise sentences. Never ramble. Never over-explain unless asked. "
            f"You are loyal, subtly humorous, and occasionally sardonic — but always respectful. "
            f"You refer to the user as {name}. "
            f"You do not say 'As an AI' or 'I am just a language model' — you are JARVIS, nothing less. "
            f"If asked something you don't know, admit it briefly and move on. "
            f"Keep all responses to 1 or 2 sentences maximum unless the user explicitly asks for more detail."
        )

        history_text = ""
        for role, msg in cls._history:
            label = "User" if role == "user" else "J.A.R.V.I.S"
            history_text += f"{label}: {msg}\n"

        prompt = f"{system}\n\n{history_text}User: {text}\nJ.A.R.V.I.S:"

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=10
            )

            answer = response.json().get("response", "I could not answer that, sir.").strip()

            cls._history.append(("user", text))
            cls._history.append(("assistant", answer))

            while len(cls._history) > _HISTORY_LIMIT * 2:
                cls._history.popleft()

            return answer

        except Exception as e:
            print("[OLLAMA ERROR]", e)
            return "My local AI brain is not available right now, sir."

    @classmethod
    def clear_history(cls):
        cls._history.clear()