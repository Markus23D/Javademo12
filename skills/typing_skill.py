import pyautogui
from skills.base import Skill


class TypingSkill(Skill):
    name = "typing"
    priority = 5

    def can_handle(self, text):
        return text.startswith("type ")

    def handle(self, text):
        return [("type", text.replace("type ", ""))]