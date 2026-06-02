class Skill:

    name = "base"

    def can_handle(self, text):
        return 0.0

    def handle(self, text, context):
        return [], 0.0