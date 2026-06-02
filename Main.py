from core.brain import load_skills, brain
from core.context import Context
from core.executor import Executor

from voice.audio_bus import AudioBus
from voice.stt import STT
from voice.tts import speak, stop

import threading


# -----------------------
# INIT
# -----------------------
load_skills()

bus = AudioBus()
context = Context()
executor = Executor()

stt = STT(bus)


# -----------------------
# THREADS
# -----------------------
threading.Thread(target=stt.start, daemon=True).start()

print("Jarvis online")

speak("What can I do for you sir")


# -----------------------
# MAIN LOOP
# -----------------------
while True:

    text = bus.get_stt()
    if not text:
        continue

    print("Heard:", text)

    # interrupt speech if user talks
    stop()

    result = brain(text, context)
    plan = result.get("plan")

    if not plan:
        bus.push_tts("I didn't understand that")
        continue

    executor.execute(plan)
    context.remember(text)