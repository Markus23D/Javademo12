class Planner:

    SEPARATORS = [" and ", " then ", ","]

    # -----------------------
    # STEP 1: SPLIT COMMAND
    # -----------------------
    @classmethod
    def split_command(cls, text):

        commands = [text]

        for sep in cls.SEPARATORS:
            new_commands = []
            for cmd in commands:
                new_commands.extend(cmd.split(sep))
            commands = new_commands

        return [c.strip() for c in commands if c.strip()]

    # -----------------------
    # STEP 2: CONVERT TO EXECUTABLE PLAN
    # -----------------------
    @classmethod
    def build_plan(cls, text):

        steps = []
        parts = cls.split_command(text)

        for part in parts:
            part = part.lower()

            # OPEN APP
            if part.startswith("open "):
                app = part.replace("open ", "").strip()
                steps.append({
                    "action": "open_app",
                    "value": app
                })

            # OPEN URL / GO TO
            elif "youtube" in part or "go to" in part or "open website" in part:
                url = cls._extract_url(part)
                steps.append({
                    "action": "open_url",
                    "value": url
                })

            # TYPE TEXT
            elif part.startswith("type "):
                steps.append({
                    "action": "type",
                    "value": part.replace("type ", "")
                })

            # DEFAULT (fallback)
            else:
                steps.append({
                    "action": "open_url",
                    "value": f"https://www.google.com/search?q={part.replace(' ', '+')}"
                })

        return steps

    # -----------------------
    # HELPER
    # -----------------------
    @staticmethod
    def _extract_url(text):
        if "youtube" in text:
            return "https://youtube.com"

        if "google" in text:
            return "https://google.com"

        return "https://google.com"