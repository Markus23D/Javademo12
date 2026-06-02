from skills.base import Skill
from skills.registry import skill


@skill
class BrowserSkill(Skill):

    name = "browser"

    def can_handle(self, text):

        score = 0

        if "chrome" in text:
            score += 0.5

        if "youtube" in text:
            score += 0.5

        return min(score, 1.0)

    def handle(self, text, context):

        plan = []

        if "chrome" in text:
            plan.append(("open_app", "chrome"))

        if "youtube" in text:
            plan.append(("open_url", "https://youtube.com"))

        return plan, self.can_handle(text)