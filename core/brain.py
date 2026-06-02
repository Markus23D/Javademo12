import os
import importlib

import confidence

from skills.registry import SKILL_REGISTRY



def load_skills():

    skills_folder = "skills"

    for file in os.listdir(skills_folder):

        if not file.endswith(".py"):
            continue

        if file.startswith("__"):
            continue

        if file in ["registry.py", "base.py"]:
            continue

        module_name = f"skills.{file[:-3]}"

        importlib.import_module(module_name)


def brain(text, context):

    best_skill = None
    best_confidence = 0

    for skill in SKILL_REGISTRY:

        confidence = skill.can_handle(text)

        if confidence > best_confidence:

            best_confidence = confidence
            best_skill = skill

    if best_skill:

        plan, confidence = best_skill.handle(text, context)

        return plan

    return []

