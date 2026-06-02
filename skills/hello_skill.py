from skills.base import Skill

class HelloSkill(Skill):

    def can_handle(self, text: str) -> float:
        if "hello" in text:
            return 0.9
        return 0.0

    def handle(self, text: str, context):
        return {
            "response": "Hello sir"
        }, 0.9