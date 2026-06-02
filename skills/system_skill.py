from skills.base import Skill


class SystemSkill(Skill):

    def can_handle(self, text: str) -> float:
        score = 0.0
        if "shutdown" in text:
            score += 1.0
        if "restart" in text:
            score += 1.0
        return min(score, 1.0)

    def handle(self, text, context):

        confidence = self.can_handle(text)

        if "shutdown" in text:
            return [("shutdown", None)], confidence

        if "restart" in text:
            return [("restart", None)], confidence

        return [], 0.0