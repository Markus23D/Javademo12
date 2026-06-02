import subprocess
import webbrowser
import json
import queue
import os
import time
import asyncio
import tempfile
import random

import sounddevice as sd
from vosk import Model, KaldiRecognizer
import edge_tts

import pyautogui


# =========================
# CONFIG
# =========================

VOICE = "en-GB-RyanNeural"
WAKE_WORDS = ["jarvis", "hey jarvis", "hey"]

model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

audio_queue = queue.Queue()

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.4


# =========================
# MEMORY SYSTEM
# =========================

memory = {
    "last_command": None,
    "last_plan": None,
    "history": []
}


def save_memory(command, plan):
    memory["last_command"] = command
    memory["last_plan"] = plan
    memory["history"].append(command)


# =========================
# NATURAL RESPONSES
# =========================

responses = [
    "Got it",
    "On it",
    "Okay",
    "Done",
    "Right away",
    "Sure"
]


def natural_reply():
    return random.choice(responses)


# =========================
# TEXT TO SPEECH
# =========================

def speak(text):
    print("Jarvis:", text)
    asyncio.run(_speak(text))


async def _speak(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        path = f.name

    comm = edge_tts.Communicate(text, VOICE)
    await comm.save(path)

    subprocess.run(
        ["powershell", "-c", f'(New-Object Media.SoundPlayer "{path}").PlaySync();'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    os.remove(path)


# =========================
# AUDIO INPUT
# =========================

def callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))


stream = sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback
)

stream.start()

print("Jarvis 4.4 online...")


# =========================
# LISTEN
# =========================

def listen():
    while True:
        data = audio_queue.get()

        if recognizer.AcceptWaveform(data):
            text = json.loads(recognizer.Result()).get("text", "").strip()
            if text:
                print("Heard:", text)
                return text.lower()


# =========================
# WAKE WORD
# =========================

def is_wake(text):
    return any(w in text for w in WAKE_WORDS)


def clean(text):
    for w in WAKE_WORDS:
        text = text.replace(w, "")
    return text.strip()


# =========================
# DESKTOP ACTIONS
# =========================

def type_text(text):
    pyautogui.write(text, interval=0.05)


def click():
    pyautogui.click()


def press(keys):
    pyautogui.hotkey(*keys)


# =========================
# SYSTEM ACTIONS
# =========================

def shutdown_pc():
    os.system("shutdown /s /t 5")


def restart_pc():
    os.system("shutdown /r /t 5")


# =========================
# 🧠 BRAIN (WORKFLOW PLANNER)
# =========================

def brain(text):
    text = text.lower()

    # =========================
    # YOUTUBE WORKFLOW MODE
    # =========================
    if "youtube" in text and "search" in text:
        query = text.split("search")[-1].strip()

        return [
            {"action": "open_url", "value": "https://youtube.com"},
            {"action": "wait", "value": 3},
            {"action": "click_search"},
            {"action": "type", "value": query},
            {"action": "press", "value": ["enter"]}
        ]

    # =========================
    # SIMPLE COMMANDS
    # =========================
    plan = []

    if "chrome" in text:
        plan.append(("open_app", "chrome"))

    if "notepad" in text:
        plan.append(("open_app", "notepad"))

    if "youtube" in text and "search" not in text:
        plan.append(("open_url", "https://youtube.com"))

    if text.startswith("type "):
        plan.append(("type", text.replace("type", "").strip()))

    if "click" in text:
        plan.append(("click", None))

    if "shutdown" in text:
        plan.append(("shutdown", None))

    if "restart" in text:
        plan.append(("restart", None))

    return plan


# =========================
# ⚙️ EXECUTION ENGINE
# =========================

def execute(plan):
    reply = natural_reply()
    speak(reply)

    for step in plan:

        # -------------------------
        # WORKFLOW MODE
        # -------------------------
        if isinstance(step, dict):

            if step["action"] == "open_url":
                speak("Opening website")
                webbrowser.open(step["value"])

            elif step["action"] == "wait":
                time.sleep(step["value"])

            elif step["action"] == "type":
                speak("Typing")
                type_text(step["value"])

            elif step["action"] == "press":
                pyautogui.hotkey(*step["value"])

            elif step["action"] == "click_search":
                speak("Clicking search bar")
                pyautogui.click(800, 150)


        # -------------------------
        # LEGACY MODE
        # -------------------------
        else:
            action, value = step

            if action == "open_app":
                if value == "chrome":
                    speak("Opening Chrome")
                    subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

                elif value == "notepad":
                    speak("Opening Notepad")
                    subprocess.Popen("notepad.exe")

            elif action == "open_url":
                speak("Opening website")
                webbrowser.open(value)

            elif action == "type":
                speak("Typing")
                type_text(value)

            elif action == "click":
                speak("Clicking")
                click()

            elif action == "shutdown":
                speak("Are you sure?")
                confirm = listen()
                if "yes" in confirm:
                    speak("Shutting down")
                    shutdown_pc()
                else:
                    speak("Cancelled")

            elif action == "restart":
                speak("Are you sure?")
                confirm = listen()
                if "yes" in confirm:
                    speak("Restarting")
                    restart_pc()
                else:
                    speak("Cancelled")


    # Save memory after execution
    save_memory(" | ".join([str(step) for step in plan]), plan)


# =========================
# MAIN LOOP
# =========================

running = True

while running:
    heard = listen()

    if not heard:
        continue

    print("Heard:", heard)

    if not is_wake(heard):
        continue

    command = clean(heard)

    if not command:
        speak("Yes?")
        command = listen()

    plan = brain(command)

    if not plan:
        speak(natural_reply())
        continue

    execute(plan)

    memory["last_command"] = command
    memory["last_plan"] = plan
    memory["history"].append(command)

    if len(memory["history"]) > 20:
        memory["history"] = memory["history"][-20:]