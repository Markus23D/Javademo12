import importlib
import os

SKILLS = []


def load_skills():
    global SKILLS

    skill_folder = "skills"

    for file in os.listdir(skill_folder):
        if file.endswith(".py") and file not in ["__init__.py", "base.py"]:

            module_name = f"skills.{file[:-3]}"
            module = importlib.import_module(module_name)

            for obj in dir(module):
                cls = getattr(module, obj)

                if hasattr(cls, "can_handle"):
                    try:
                        SKILLS.append(cls())
                    except:
                        pass


def brain(text):
    text = text.lower()

    best_skill = None
    best_priority = -1
    best_plan = None

    for skill in SKILLS:

        if skill.can_handle(text):

            plan = skill.handle(text)

            if plan and skill.priority > best_priority:
                best_skill = skill
                best_priority = skill.priority
                best_plan = plan

    return best_plan