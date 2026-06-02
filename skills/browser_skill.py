import webbrowser
from skills.base import Skill


class BrowserSkill(Skill):
    name = "browser"
    priority = 10

    def can_handle(self, text):
        return "youtube" in text or "open google" in text or "chrome" in text

    def handle(self, text):

        if "youtube" in text and "search" in text:
            query = text.replace("search youtube", "").strip()

            return [
                ("open_url", "https://youtube.com/results?search_query=" + query)
            ]

        if "youtube" in text:
            return [("open_url", "https://youtube.com")]

        if "google" in text:
            return [("open_url", "https://google.com")]

        if "chrome" in text:
            return [("open_app", "chrome")]

        return []