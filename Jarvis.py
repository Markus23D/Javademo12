import subprocess
import webbrowser
from datetime import datetime
import queue
import json
import os
import asyncio
import tempfile
import re

import sounddevice as sd
from vosk import Model, KaldiRecognizer
import edge_tts


# =========================
# CONFIG
# =========================

VOICE = "en-GB-RyanNeural"
WAKE_WORDS = ["jarvis", "hey jarvis", "hey"]

MODEL_PATH = "vosk-model-small-en-us-0.15"

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

audio_queue = queue.Queue()

MEMORY_FILE = "jarvis_memory.json"


# =========================
# MEMORY SYSTEM
# =========================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)


memory = load_memory()


# =========================
# TTS (CLEAN + FAST)
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

print("Jarvis 2.0 online...")


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


def clean_command(text):
    for w in WAKE_WORDS:
        text = text.replace(w, "")
    return text.strip()


# =========================
# NLP (LIGHTWEIGHT INTENT PARSER)
# =========================

def parse_command(text):
    """
    Converts natural language into structured actions
    """

    actions = []

    # OPEN APP
    if "open chrome" in text:
        actions.append({"action": "open_app", "app": "chrome"})

    if "open notepad" in text:
        actions.append({"action": "open_app", "app": "notepad"})

    if "open youtube" in text:
        actions.append({"action": "open_url", "url": "https://youtube.com"})

    # TIME
    if "time" in text:
        actions.append({"action": "tell_time"})

    # WEB SEARCH STYLE COMMAND
    search_match = re.search(r"search (for )?(.*)", text)
    if search_match:
        query = search_match.group(2)
        actions.append({"action": "web_search", "query": query})

    # MEMORY
    if "remember" in text:
        actions.append({"action": "remember", "text": text})

    return actions


# =========================
# EXECUTION ENGINE
# =========================

def run_action(action):
    act = action["action"]

    if act == "open_app":
        app = action["app"]

        if app == "chrome":
            speak("Opening Chrome")
            subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

        elif app == "notepad":
            speak("Opening Notepad")
            subprocess.Popen("notepad.exe")

    elif act == "open_url":
        speak("Opening website")
        webbrowser.open(action["url"])

    elif act == "tell_time":
        now = datetime.now().strftime("%I:%M %p")
        speak(f"It is {now}")

    elif act == "web_search":
        speak(f"Searching for {action['query']}")
        webbrowser.open(f"https://www.google.com/search?q={action['query']}")

    elif act == "remember":
        key = str(len(memory))
        memory[key] = action["text"]
        save_memory(memory)
        speak("I will remember that")


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

    command = clean_command(heard)

    if not command:
        speak("Yes?")
        command = listen()

    actions = parse_command(command)

    if not actions:
        speak("I didn't understand that")
        continue

    for action in actions:
        run_action(action)

    # shutdown condition
    if any("shutdown" in heard for _ in [1]):
        speak("Goodbye")
        running = False