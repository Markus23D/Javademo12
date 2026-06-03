import json
import time
import webbrowser
import pyautogui
import os
import subprocess


class Executor:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        apps_path = os.path.join(base_dir, "commands.json")

        with open(apps_path, "r", encoding="utf-8") as f:
            self.apps = json.load(f)

        self.actions = {
            "wait": self.wait,
            "open_url": self.open_url,
            "open_app": self.open_app,
            "youtube_search": self.youtube_search,
            "type": self.type_text,
            "shutdown": self.shutdown,
            "standby": self.standby,
        }

    def execute(self, plan):
        for step in plan:
            action = step.get("action")
            value = step.get("value")

            func = self.actions.get(action)

            if not func:
                print(f"[UNKNOWN ACTION] {action}")
                continue

            func(value)

    def open_app(self, value):
        key = value.lower().strip()
        path = None

        for app_name, data in self.apps.items():
            aliases = data.get("aliases", [])

            if key == app_name.lower() or key in [a.lower() for a in aliases]:
                path = os.path.expandvars(data.get("path"))
                break

        if not path:
            print(f"[APP NOT FOUND] {value}")
            return

        print("[LAUNCHING]", path)

        try:
            subprocess.Popen(path, shell=True)
        except Exception as e:
            print(f"[ERROR OPENING APP] {value}: {e}")

    def wait(self, value):
        time.sleep(value or 1)

    def open_url(self, value):
        webbrowser.open(value)

    def youtube_search(self, value):
        query = value.replace(" ", "+")
        webbrowser.open(f"https://youtube.com/results?search_query={query}")

    def type_text(self, value):
        pyautogui.write(value or "")

    def shutdown(self, value=None):
        os.system("shutdown /s /t 5")

    def standby(self, value=None):
        print("[EXECUTOR] standby")