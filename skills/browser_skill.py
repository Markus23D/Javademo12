from skills.base import Skill


class BrowserSkill(Skill):
    name = "browser"
    priority = 10

    def can_handle(self, text: str) -> float:
        score = 0.0

        if "chrome" in text:
            score += 0.6
        if "youtube" in text:
            score += 0.6
        if "google" in text:
            score += 0.5
        if "search" in text:
            score += 0.4

        return min(score, 1.0)

    def handle(self, text: str, context):

        confidence = self.can_handle(text)
        plan = []

        # OPEN CHROME
        if "chrome" in text:
            plan.append(("open_app", "chrome"))
            context.update("last_app", "chrome")

        # YOUTUBE
        elif "youtube" in text and "search" not in text:
            plan.append(("open_url", "https://youtube.com"))

        # YOUTUBE SEARCH WITH CONTEXT
        elif "search youtube" in text:

            query = text.replace("search youtube", "").strip()

            if context.get("last_app") == "chrome":
                plan.append(("open_url",
                             "https://youtube.com/results?search_query=" + query.replace(" ", "+")
                             ))
            else:
                plan.append(("open_url",
                             "https://youtube.com/results?search_query=" + query.replace(" ", "+")
                             ))

            context.update("last_query", query)

        return plan, confidence