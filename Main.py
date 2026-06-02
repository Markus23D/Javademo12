from voice.stt import listen
from voice.tts import speak
from core.Brain import brain, load_skills
from core.Executor import execute


load_skills()

speak("Jarvis skill system online")

while True:

    text = listen()
    print("Heard:", text)

    if not text:
        continue

    plan = brain(text)

    if not plan:
        speak("I didn't understand that")
        continue

    execute(plan)