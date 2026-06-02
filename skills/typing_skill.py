from skills.base import Skill
from skills.registry import skill


@skill
class TypingSkill(Skill):

    name = "typing"

    def can_handle(self, text):

        if text.startswith("type "):
            return 1.0

        return 0.0

    def handle(self, text, context):

        text_to_type = text.replace("type ", "")

        return [
            ("type", text_to_type)
        ], 1.0