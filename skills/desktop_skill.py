from skills.base import Skill
from skills.registry import skill


@skill
class DesktopSkill(Skill):

    name = "desktop"

    def can_handle(self, text):
        text = text.lower().strip()

        triggers = [
            "what app am i in",
            "what window am i in",
            "current window",
            "close current window",
            "close window",
            "switch to chrome",
            "switch to discord",
            "switch to spotify",
            "switch back",
            "search that again",
            "repeat last search",
            "list windows",
        ]

        return 0.95 if any(t in text for t in triggers) else 0.0

    def handle(self, text, context):
        text = text.lower().strip()

        # -----------------------
        # ACTIVE WINDOW
        # -----------------------
        if (
                "what app am i in" in text
                or "what window am i in" in text
                or "current window" in text
        ):
            return [
                {"action": "active_window", "value": None}
            ], 0.95

        # -----------------------
        # CLOSE WINDOW
        # -----------------------
        if "close current window" in text or "close window" in text:
            return [
                {"action": "hotkey", "value": ["alt", "f4"]}
            ], 0.95

        # -----------------------
        # SWITCH TO APPS
        # -----------------------
        if text.startswith("switch to "):
            app = text.replace("switch to ", "", 1).strip()

            return [
                {"action": "switch_window", "value": app}
            ], 0.95

        # -----------------------
        # SWITCH BACK
        # -----------------------
        if "switch back" in text:
            return [
                {"action": "switch_back", "value": None}
            ], 0.95

        # -----------------------
        # REPEAT SEARCH
        # -----------------------
        if "search that again" in text or "repeat last search" in text:
            return [
                {"action": "repeat_last_search", "value": None}
            ], 0.95

        # -----------------------
        # LIST WINDOWS
        # -----------------------
        if "list windows" in text:
            return [
                {"action": "list_windows", "value": None}
            ], 0.95



        return [], 0.0
