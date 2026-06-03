import importlib
import os

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

        print("[LOADING SKILL]", file)
        importlib.import_module(f"skills.{file[:-3]}")

    print("[REGISTERED SKILLS]", [s.__class__.__name__ for s in SKILL_REGISTRY])