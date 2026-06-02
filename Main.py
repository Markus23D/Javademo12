from core.brain import brain, load_skills
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

    # stop speaking when user talks
    stop()

    # run brain ONCE
    result = brain(text, context)
    plan = result.get("plan")

    print("PLAN:", plan)

    if not plan:
        bus.push_tts("I didn't understand that")
        continue

    # execute plan
    executor.execute(plan)

    # remember context
    context.remember(text)