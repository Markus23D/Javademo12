from skills.base import Skill
from skills.registry import skill


@skill
class BrowserSkill(Skill):

    def can_handle(self, text: str) -> float:
        text = text.lower()

        # stronger intent detection (handles STT noise)
        if "youtube" in text:
            return 0.95

        if "google" in text:
            return 0.75

        chrome_keywords = [
            "chrome",
            "browser",
            "open chrome",
            "start chrome",
            "launch chrome"
        ]

        if any(k in text for k in chrome_keywords):
            return 0.85

        # weak generic open intent fallback
        if "open" in text and ("browse" in text or "internet" in text):
            return 0.6

        return 0.0

    def handle(self, text: str, context):

        text = text.lower()

        # YouTube
        if "youtube" in text:
            return (
                [{"action": "open_url", "value": "https://youtube.com"}],
                0.95
            )

        # Google
        if "google" in text:
            return (
                [{"action": "open_url", "value": "https://google.com"}],
                0.75
            )

        # Chrome / browser (MAIN FIX)
        chrome_keywords = ["chrome", "browser", "open chrome", "start chrome", "launch chrome"]

        if any(k in text for k in chrome_keywords):
            return (
                [{"action": "open_app", "value": "chrome"}],
                0.85
            )

        return ([], 0.0)