from skills.base import Skill
from skills.registry import skill


@skill
class DesktopSkill(Skill):

    name = "desktop"

    SWITCH_PREFIXES = ["switch to ", "go to ", "focus ", "bring up ", "show "]
    FIXED_TRIGGERS = [
        "what app am i in",
        "what window am i in",
        "current window",
        "close current window",
        "close window",
        "switch back",
        "search that again",
        "repeat last search",
        "list windows",
        "list open windows",
        "what windows are open",
    ]

    def can_handle(self, text: str) -> float:
        text = text.lower().strip()

        if any(t in text for t in self.FIXED_TRIGGERS):
            return 0.95

        if any(text.startswith(p) for p in self.SWITCH_PREFIXES):
            return 0.95

        return 0.0

    def handle(self, text: str, context):
        text = text.lower().strip()

        # ACTIVE WINDOW
        if any(t in text for t in ["what app am i in", "what window am i in", "current window"]):
            return [
                {"action": "speak", "value": "Checking active window sir"},
                {"action": "active_window", "value": None},
            ], 0.95

        # CLOSE WINDOW
        if "close current window" in text or "close window" in text:
            return [
                {"action": "speak", "value": "Closing the window sir"},
                {"action": "hotkey", "value": ["alt", "f4"]},
            ], 0.95

        # SWITCH TO <APP>
        for prefix in self.SWITCH_PREFIXES:
            if text.startswith(prefix):
                app = text[len(prefix):].strip()
                return [
                    {"action": "speak", "value": f"Switching to {app} sir"},
                    {"action": "switch_window", "value": app},
                ], 0.95

        # SWITCH BACK
        if "switch back" in text:
            return [
                {"action": "speak", "value": "Switching back sir"},
                {"action": "switch_back", "value": None},
            ], 0.95

        # REPEAT SEARCH
        if "search that again" in text or "repeat last search" in text:
            return [
                {"action": "speak", "value": "Repeating last search sir"},
                {"action": "repeat_last_search", "value": None},
            ], 0.95

        # LIST WINDOWS
        if any(t in text for t in ["list windows", "list open windows", "what windows are open"]):
            return [
                {"action": "speak", "value": "Listing open windows sir"},
                {"action": "list_windows", "value": None},
            ], 0.95

        return [], 0.0
