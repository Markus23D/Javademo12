import requests


class AIChat:

    @staticmethod
    def ask(text, memory=None):
        name = "sir"

        if memory:
            remembered = memory.recall_fact("preferred_name") or memory.recall_fact("name")
            if remembered:
                name = remembered

        prompt = f"""
You are J.A.R.V.I.S, a calm desktop AI assistant.
Answer in 1 or 2 short sentences.
Do not explain too much unless asked.
Address the user as {name}.

User: {text}
J.A.R.V.I.S:
"""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            data = response.json()
            return data.get("response", "I could not answer that, sir.").strip()

        except Exception as e:
            print("[OLLAMA ERROR]", e)
            return "My local AI brain is not available right now, sir."