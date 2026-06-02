import time
import webbrowser
import subprocess
import pyautogui
import os

from voice.tts import speak


class Executor:

    def __init__(self):

        self.actions = {
            "wait": self.wait,
            "open_url": self.open_url,
            "open_app": self.open_app,
            "youtube_search": self.youtube_search,
            "type": self.type_text,
            "shutdown": self.shutdown
        }

    # -----------------------
    # MAIN ENTRY
    # -----------------------
    def execute(self, plan):
        if not plan:
            return

        # 🔊 Jarvis response
        speak("Certainly sir")

        for action, value in plan:
            print("EXEC:", action, value)

            handler = self.actions.get(action)

            if handler:
                try:
                    handler(value)
                except Exception as e:
                    print(f"[EXEC ERROR] {action}: {e}")
            else:
                print(f"[UNKNOWN ACTION] {action}")

    # -----------------------
    # ACTIONS
    # -----------------------
    def wait(self, value):
        time.sleep(value)

    def open_url(self, value):
        webbrowser.open(value)

    def open_app(self, value):
        apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        }

        path = apps.get(value)

        if path:
            subprocess.Popen(path)
        else:
            print(f"[APP NOT FOUND] {value}")

    def youtube_search(self, value):
        query = value.replace(" ", "+")
        webbrowser.open(f"https://youtube.com/results?search_query={query}")

    def type_text(self, value):
        pyautogui.write(value)

    def shutdown(self, value=None):
        os.system("shutdown /s /t 5")