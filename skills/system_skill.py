from skills.base import Skill
from skills.registry import skill


@skill
class SystemSkill(Skill):

    name = "system"

    def can_handle(self, text):

        if "shutdown" in text:
            return 1.0

        if "restart" in text:
            return 1.0

        return 0.0

    def handle(self, text, context):

        if "shutdown" in text:
            return [("shutdown", None)], 1.0

        if "restart" in text:
            return [("restart", None)], 1.0

        return [], 0.0