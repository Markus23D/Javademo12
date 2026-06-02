class Skill:
    name = "base"
    priority = 0

    def can_handle(self, text: str) -> bool:
        return False

    def handle(self, text: str):
        return []