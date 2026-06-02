from skills.base import Skill
from skills.registry import skill


@skill
class GameSkill(Skill):

    def can_handle(self, text: str) -> float:
        text = text.lower()

        games = [
            "chrome",  # optional overlap doesn't hurt
            "league", "lol",
            "wow", "warcraft",
            "overwatch",
            "riot",
            "zenless",
            "wuthering",
            "subnautica"
        ]

        return 0.9 if any(g in text for g in games) else 0.0

    def handle(self, text: str, context):
        text = text.lower()

        # League of Legends
        if "lol" in text or "league" in text:
            return (
                [{"action": "open_app", "value": "league of legends"}],
                0.95
            )

        # World of Warcraft
        if "wow" in text or "warcraft" in text:
            return (
                [{"action": "open_app", "value": "world of warcraft"}],
                0.95
            )

        # Overwatch
        if "overwatch" in text:
            return (
                [{"action": "open_app", "value": "overwatch"}],
                0.95
            )

        # Riot Client
        if "riot" in text:
            return (
                [{"action": "open_app", "value": "riot client"}],
                0.95
            )

        # Zenless Zone Zero
        if "zenless" in text:
            return (
                [{"action": "open_app", "value": "zenless zone zero"}],
                0.95
            )

        # Wuthering Waves
        if "wuthering" in text:
            return (
                [{"action": "open_app", "value": "wuthering waves"}],
                0.95
            )

        # fallback
        return ([], 0.0)