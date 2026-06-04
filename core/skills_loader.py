import importlib
import os

from skills.registry import SKILL_REGISTRY

# Absolute path to the skills folder — works regardless of working directory
_SKILLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills")


def load_skills():
    for file in os.listdir(_SKILLS_DIR):
        if not file.endswith(".py"):
            continue
        if file.startswith("__"):
            continue
        if file in ["registry.py", "base.py"]:
            continue

        print("[LOADING SKILL]", file)
        importlib.import_module(f"skills.{file[:-3]}")

    print("[REGISTERED SKILLS]", [s.__class__.__name__ for s in SKILL_REGISTRY])
