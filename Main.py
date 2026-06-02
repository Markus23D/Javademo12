from voice.stt import listen
from voice.tts import speak
from core.brain import brain, load_skills
from core.executor import execute
from core.context import context


load_skills()

speak("Jarvis context engine online")

while True:

    text = listen()
    print("Heard:", text)

    if not text:
        continue

    plan = brain(text)

    if not plan:
        speak("I’m not sure what you mean")
        continue

    execute(plan)

    context.update("last_command", text)