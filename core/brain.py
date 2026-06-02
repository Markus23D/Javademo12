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


def normalize_step(step):
    """
    Ensures every skill returns a clean dict format:
    {"action": "...", "value": "..."}
    """

    if isinstance(step, tuple):
        return {
            "action": step[0],
            "value": step[1]
        }

    if isinstance(step, dict):
        return {
            "action": step.get("action"),
            "value": step.get("value")
        }

    return None


def brain(text, context):
    best_skill = None
    best_score = 0.0

    # -----------------------
    # PICK BEST SKILL
    # -----------------------
    for skill in SKILL_REGISTRY:
        score = skill.can_handle(text)

        if score > best_score:
            best_score = score
            best_skill = skill

    # -----------------------
    # NO MATCH
    # -----------------------
    if not best_skill or best_score < MIN_CONFIDENCE:
        return {
            "skill": None,
            "confidence": 0.0,
            "plan": None
        }

    # -----------------------
    # EXECUTE SKILL
    # -----------------------
    plan, score = best_skill.handle(text, context)

    # -----------------------
    # NORMALIZE PLAN
    # -----------------------
    fixed_plan = []

    for step in plan:
        normalized = normalize_step(step)
        if normalized:
            fixed_plan.append(normalized)

    return {
        "skill": best_skill.__class__.__name__,
        "confidence": score,
        "plan": fixed_plan
    }