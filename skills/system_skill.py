from skills.base import Skill
from skills.registry import skill


@skill
class SystemSkill(Skill):

    name = "system"

    def can_handle(self, text):
        text = text.lower()

        if "shutdown" in text:
            return 1.0

        if "restart" in text:
            return 1.0

        if "standby" in text or "stand by" in text or "sleep" in text:
            return 1.0

        return 0.0

    def handle(self, text, context):
        text = text.lower()

        if "shutdown" in text:
            return [
                {"action": "shutdown", "value": None}
            ], 1.0

        if "restart" in text:
            return [
                {"action": "restart", "value": None}
            ], 1.0

        if "standby" in text or "stand by" in text or "sleep" in text:
            return [
                {"action": "standby", "value": None}
            ], 1.0

        return [], 0.0