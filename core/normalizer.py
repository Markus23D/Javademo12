import json
import os


class Normalizer:

    DEFAULT_REPLACEMENTS = {
        # YouTube
        "you too": "youtube",
        "you tube": "youtube",

        # Standby
        "stand by": "standby",
        "go idle": "standby",

        # Browser / tabs
        "close tap": "close tab",
        "new tap": "new tab",
        "switch tap": "switch tab",
        "next tap": "next tab",
        "previous tap": "previous tab",

        # Keys
        "press inter": "press enter",
        "press in her": "press enter",

        # Search
        "search for": "search",
        "look up": "search",

        # Apps / websites
        "face book": "facebook",
        "git hub": "github",
        "net flicks": "netflix",
        "open crow": "open chrome",
        "open crumb": "open chrome",

        # Discord mishearings
        "this cord": "discord",
        "this code": "discord",
        "disk cord": "discord",
        "disk code": "discord",
        "disco rd": "discord",
        "this cord.": "discord",
        "this code.": "discord",

        "switch to over both": "switch to overwatch",
        "switch to overwatch": "switch to overwatch",

        "switch to spotify premium": "switch to spotify",
        "switch spotify": "switch to spotify",
        "put on": "play",
        "might play ": "play ",
        "my play ": "play ",
        "mate play ": "play ",
    }

    FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "normalizer_memory.json"
    )

    _memory_cache: dict = None  # cached learned replacements

    @classmethod
    def load_memory(cls) -> dict:
        if not os.path.exists(cls.FILE_PATH):
            return {}

        try:
            with open(cls.FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def _get_memory(cls) -> dict:
        """Return cached learned memory, loading from disk on first access."""
        if cls._memory_cache is None:
            cls._memory_cache = cls.load_memory()
        return cls._memory_cache

    @classmethod
    def save_memory(cls, data: dict):
        with open(cls.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def learn(cls, wrong: str, correct: str):
        wrong = wrong.lower().strip()
        correct = correct.lower().strip()

        memory = cls._get_memory()
        memory[wrong] = correct
        cls._memory_cache = memory  # update cache
        cls.save_memory(memory)

        print(f"[NORMALIZER LEARNED] {wrong} -> {correct}")

    @classmethod
    def forget(cls, wrong: str) -> bool:
        wrong = wrong.lower().strip()
        memory = cls._get_memory()

        if wrong not in memory:
            return False

        del memory[wrong]
        cls._memory_cache = memory
        cls.save_memory(memory)
        print(f"[NORMALIZER FORGOT] {wrong}")
        return True

    @classmethod
    def list_learned(cls) -> dict:
        return dict(cls._get_memory())

    @classmethod
    def clean(cls, text: str) -> str:
        import re
        text = text.lower().strip()
        text = re.sub(r"[.!?,;]+", "", text).strip()

        replacements = {}
        replacements.update(cls.DEFAULT_REPLACEMENTS)
        replacements.update(cls._get_memory())

        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)

        return text