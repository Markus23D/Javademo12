from skills.base import Skill
from skills.registry import skill


@skill
class WeatherSkill(Skill):

    name = "Weather"

    def can_handle(self, text):
        return 1.0 if "weather" in text.lower() else 0.0

    def handle(self, text, context):
        return [], 1.0