import json
import time
import webbrowser
import pyautogui
import os


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
            "shutdown": self.shutdown
        }

    # -----------------------
    # MAIN EXECUTION ENGINE
    # -----------------------
    def execute(self, plan):

        if not plan:
            print("[EMPTY PLAN]")

            if isinstance(data, dict):
                aliases = data.get("aliases", [])

                if key in aliases or key in app_name:
                    path = data.get("path")
                    break

    if not os.path:
        print(f"[APP NOT FOUND] {value}")
        return

    print("[LAUNCHING]", os.path)

    try:
        os.startfile(os.path)
    except Exception as e:
        print(f"[ERROR OPENING APP] {value}: {e}")

def wait(self, value):
    time.sleep(value)

def open_url(self, value):
    webbrowser.open(value)

def youtube_search(self, value):
    query = value.replace(" ", "+")
    webbrowser.open(f"https://youtube.com/results?search_query={query}")

def type_text(self, value):
    pyautogui.write(value)

def shutdown(self, value=None):
    os.system("shutdown /s /t 5")