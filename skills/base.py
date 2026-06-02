class Skill:
    name = "base"
    priority = 0

    def can_handle(self, text: str) -> float:
        """
        Return confidence (0.0 → 1.0)
        """
        return 0.0

    def handle(self, text: str, context):
        """
        Returns:
            (plan, confidence)
        """
        return None, 0.0