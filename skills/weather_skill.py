from urllib.parse import quote_plus

from skills.base import Skill
from skills.registry import skill


@skill
class WeatherSkill(Skill):

    name = "Weather"

    def can_handle(self, text: str) -> float:
        return 1.0 if "weather" in text.lower() else 0.0

    def handle(self, text: str, context):
        text = text.lower().strip()

        # Try to extract a location from the query
        location = None
        for prefix in ["weather in ", "weather for ", "weather at "]:
            if prefix in text:
                location = text.split(prefix, 1)[1].strip()
                break

        if location:
            url = f"https://www.google.com/search?q={quote_plus('weather ' + location)}"
        else:
            url = "https://www.google.com/search?q=weather+today"

        return [
            {"action": "speak", "value": "Looking up the weather for you sir."},
            {"action": "open_url", "value": url},
        ], 1.0
