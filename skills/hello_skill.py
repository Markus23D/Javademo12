from skills.base import Skill
from skills.registry import skill


@skill
class HelloSkill(Skill):

    def can_handle(self, text: str) -> float:
        if "hello" in text.lower():
            return 0.9
        return 0.0

    def handle(self, text: str, context):
        return [{"action": "speak", "value": "Hello sir"}], 0.9
