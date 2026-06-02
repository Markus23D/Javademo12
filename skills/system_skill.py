import os
from skills.base import Skill


class SystemSkill(Skill):
    name = "system"
    priority = 8

    def can_handle(self, text):
        return "shutdown" in text or "restart" in text

    def handle(self, text):

        if "shutdown" in text:
            return [("shutdown", None)]

        if "restart" in text:
            return [("restart", None)]

        return []