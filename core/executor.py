import subprocess
import webbrowser
import os
import pyautogui


def execute(plan):

    if not plan:
        return

    for action, value in plan:

        if action == "open_app":
            if value == "chrome":
                subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

        elif action == "open_url":
            webbrowser.open(value)

        elif action == "type":
            pyautogui.write(value, interval=0.03)

        elif action == "shutdown":
            os.system("shutdown /s /t 5")

        elif action == "restart":
            os.system("shutdown /r /t 5")