from core.brain import load_skills
from core.brain import brain

from core.context import context

from core.executor import execute
from skills.registry import SKILL_REGISTRY

from voice.stt import listen
from voice.tts import speak


load_skills()


speak("What can i do for you sir")

while True:

    text = listen()

    if not text:
        continue

    print("Heard:", text)

    plan = brain(text, context)

    if not plan:

        speak("I didn't understand that")

        continue

    execute(plan)

    context.remember(text)