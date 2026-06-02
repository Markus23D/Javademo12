import importlib
import os
from skills.registry import SKILL_REGISTRY

MIN_CONFIDENCE = 0.35


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
    best_score = 0.0

    for skill in SKILL_REGISTRY:
        score = skill.can_handle(text)

        if score > best_score:
            best_score = score
            best_skill = skill

    if best_skill and best_score >= MIN_CONFIDENCE:
        plan, score = best_skill.handle(text, context)

        return {
            "skill": best_skill.__class__.__name__,
            "confidence": score,
            "plan": plan
        }

    return {
        "skill": None,
        "confidence": 0.0,
        "plan": None
    }