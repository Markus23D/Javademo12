from skills.base import Skill
from skills.registry import skill


@skill
class ScreenSkill(Skill):

    name = "screen"

    def can_handle(self, text):
        text = text.lower().strip()

        triggers = [
            "scroll down",
            "scroll up",
            "press enter",
            "press escape",
            "close tab",
            "new tab",
            "switch tab",
            "copy",
            "paste",
            "click"
        ]

        return 0.95 if any(t in text for t in triggers) else 0.0

    def handle(self, text, context):
        text = text.lower().strip()

        if "scroll down" in text:
            return [{"action": "scroll", "value": -5}], 0.95

        if "scroll up" in text:
            return [{"action": "scroll", "value": 5}], 0.95

        if "press enter" in text:
            return [{"action": "hotkey", "value": ["enter"]}], 0.95

        if "press escape" in text:
            return [{"action": "hotkey", "value": ["esc"]}], 0.95

        if "close tab" in text:
            return [{"action": "hotkey", "value": ["ctrl", "w"]}], 0.95

        if "new tab" in text:
            return [{"action": "hotkey", "value": ["ctrl", "t"]}], 0.95

        if "switch tab" in text:
            return [{"action": "hotkey", "value": ["ctrl", "tab"]}], 0.95

        if "copy" in text:
            return [{"action": "hotkey", "value": ["ctrl", "c"]}], 0.95

        if "paste" in text:
            return [{"action": "hotkey", "value": ["ctrl", "v"]}], 0.95

        if "click" in text:
            return [{"action": "click", "value": None}], 0.95

        return [], 0.0