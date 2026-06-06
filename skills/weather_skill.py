import requests
from skills.base import Skill
from skills.registry import skill
from config import DEFAULT_CITY


@skill
class WeatherSkill(Skill):

    name = "weather"

    TRIGGERS = ["weather", "temperature", "will it rain", "is it cold", "is it hot", "how hot", "how cold"]

    def can_handle(self, text: str) -> float:
        text = text.lower()
        if any(t in text for t in self.TRIGGERS):
            return 0.97
        return 0.0

    def handle(self, text: str, context):
        text = text.lower().strip()

        location = DEFAULT_CITY
        for prefix in ["weather in ", "weather for ", "temperature in ", "weather at "]:
            if prefix in text:
                location = text.split(prefix, 1)[1].strip()
                break

        try:
            response = requests.get(
                f"https://wttr.in/{requests.utils.quote(location)}?format=j1",
                timeout=8
            )
            data = response.json()
            current = data["current_condition"][0]

            temp_c = current["temp_C"]
            feels_c = current["FeelsLikeC"]
            desc = current["weatherDesc"][0]["value"]
            humidity = current["humidity"]

            msg = (
                f"Currently {desc} in {location.title()} sir. "
                f"{temp_c} degrees Celsius, feels like {feels_c}. "
                f"Humidity is {humidity} percent."
            )

        except Exception as e:
            print("[WEATHER ERROR]", e)
            msg = "I couldn't fetch the weather right now sir."

        return [{"action": "speak", "value": msg}], 0.97
