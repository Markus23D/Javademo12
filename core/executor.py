import time
import webbrowser
import subprocess
import pyautogui
import os


def execute(plan):

    for action, value in plan:

        print("EXEC:", action, value)

        if action == "wait":
            time.sleep(value)

        elif action == "open_url":
            webbrowser.open(value)

        elif action == "open_app":

            if value == "chrome":
                subprocess.Popen(
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                )

        elif action == "youtube_search":

            query = value.replace(" ", "+")

            webbrowser.open(
                f"https://youtube.com/results?search_query={query}"
            )

        elif action == "type":
            pyautogui.write(value)

        elif action == "shutdown":
            os.system("shutdown /s /t 5")