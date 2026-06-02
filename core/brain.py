import importlib
import os

from core.context import context

SKILLS = []


def load_skills():
    global SKILLS

    for file in os.listdir("skills"):
        if file.endswith(".py") and file not in ["__init__.py", "base.py"]:

            module = importlib.import_module(f"skills.{file[:-3]}")

            for obj in dir(module):
                cls = getattr(module, obj)

                if hasattr(cls, "handle") and hasattr(cls, "can_handle"):
                    try:
                        SKILLS.append(cls())
                    except:
                        pass


def brain(text):

    best_plan = None
    best_confidence = 0.0

    for skill in SKILLS:

        confidence = skill.can_handle(text)

        if confidence > best_confidence:

            plan, conf = skill.handle(text, context)

            if conf > best_confidence:
                best_plan = plan
                best_confidence = conf

    return best_plan