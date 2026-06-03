from skills.base import Skill
from skills.registry import skill


@skill
class BrowserSkill(Skill):

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def can_handle(self, text: str) -> float:

        text = self._normalize(text)

        # -----------------------
        # YOUTUBE INTENT (FIXED)
        # -----------------------
        youtube_triggers = [
            "youtube",
            "watch videos",
            "play videos",
            "show videos",
            "video",
            "yt",
            "you too",
            "you tube"
        ]

        if any(t in text for t in youtube_triggers):
            return 0.95

        # -----------------------
        # GOOGLE
        # -----------------------
        if "google" in text or "search" in text:
            return 0.75

        # -----------------------
        # CHROME / BROWSER
        # -----------------------
        chrome_keywords = [
            "chrome",
            "browser",
            "open chrome",
            "start chrome",
            "launch chrome"
        ]

        if any(k in text for k in chrome_keywords):
            return 0.85

        # -----------------------
        # WEAK GENERIC FALLBACK
        # -----------------------
        if "open" in text and any(w in text for w in ["internet", "browse", "web"]):
            return 0.6

        return 0.0

    def handle(self, text: str, context):

        text = self._normalize(text)

        # -----------------------
        # YOUTUBE
        # -----------------------
        if any(t in text for t in [
            "youtube",
            "watch videos",
            "play videos",
            "show videos",
            "video",
            "yt",
            "you too",
            "you tube"
        ]):
            return (
                [{"action": "open_url", "value": "https://youtube.com"}],
                0.95
            )

        # -----------------------
        # GOOGLE
        # -----------------------
        if "google" in text or "search" in text:
            return (
                [{"action": "open_url", "value": "https://google.com"}],
                0.75
            )

        # -----------------------
        # CHROME
        # -----------------------
        chrome_keywords = ["chrome", "browser"]

        if any(k in text for k in chrome_keywords):
            return (
                [{"action": "open_app", "value": "chrome"}],
                0.85
            )

        return ([], 0.0)