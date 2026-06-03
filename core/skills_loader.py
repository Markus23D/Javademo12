import importlib
import os

def load_skills():
    skills_folder = "skills"

    for file in os.listdir(skills_folder):
        if not file.endswith(".py"):
            continue
        if file.startswith("__"):
            continue
        if file in ["registry.py", "base.py"]:
            continue

        importlib.import_module(f"skills.{file[:-3]}")