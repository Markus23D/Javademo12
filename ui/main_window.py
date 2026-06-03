import threading

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer

from ui.widgets.OrbWidget import OrbWidget

from core.brain import brain
from core.context import Context
from core.executor import Executor
from core.intent import detect_intent
from core.dialogue import DialogueManager
from core.memory import memory, update_memory
from core.skills_loader import load_skills
from core.normalizer import Normalizer
from voice.audio_bus import AudioBus
from voice.stt import STT
from voice.tts import speak, stop


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Jarvis")
        self.resize(500, 500)

        self.setStyleSheet("""
            QWidget {
                background-color: #111111;
                color: white;
                font-size: 18px;
            }
        """)

        layout = QVBoxLayout()

        self.status = QLabel("Listening...")
        self.status.setAlignment(Qt.AlignCenter)

        self.orb = OrbWidget()

        layout.addStretch()
        layout.addWidget(self.orb)
        layout.addWidget(self.status)
        layout.addStretch()

        self.setLayout(layout)

        self.mode = "active"

        load_skills()

        self.bus = AudioBus()
        self.context = Context()
        self.dialogue = DialogueManager()
        self.executor = Executor(self.context)
        self.stt = STT(self.bus)


        threading.Thread(target=self.run_stt, daemon=True).start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_stt)
        self.timer.start(100)

        speak("What can I do for you sir")

    def enter_standby_mode(self):
        print("[UI] ENTERING STANDBY MODE")
        self.mode = "standby"
        stop()
        self.hide()

    def wake_up(self):
        print("[UI] WAKING UP")
        self.mode = "active"
        self.show()
        self.raise_()
        self.activateWindow()
        speak("I'm back online sir")

    def run_stt(self):
        try:
            print("[THREAD] STT starting...")
            self.stt.start()
        except Exception as e:
            print("[STT CRASH]", e)

    def respond(self, result):
        plan = result.get("plan", [])

        if not plan:
            speak("I didn't understand that sir")
            return

        for step in plan:
            action = step.get("action")
            value = step.get("value")

            if action == "open_app":
                speak(f"Certainly sir, opening {value}")

            elif action == "open_url":
                speak("Opening it now sir")

            elif action == "shutdown":
                speak("Shutting down system")

            elif action == "type":
                speak("Typing now sir")

            elif action == "standby":
                speak("Going idle sir")
                QTimer.singleShot(2000, self.enter_standby_mode)

            elif action == "speak":
                speak(value)

            else:
                speak("Done sir")

    def poll_stt(self):
        text = self.bus.get_stt()


        if not text:
            return

        print("[MAIN RECEIVED]", text)
        raw_text = text
        text = Normalizer.clean(text)

        if raw_text != text:
            print(f"[NORMALIZED] {raw_text} -> {text}")

        if self.mode == "standby":
            if "jarvis" in text.lower():
                self.wake_up()
            else:
                print("[IGNORED - STANDBY MODE]")
            return

        self.status.setText(text)

        stop()

        intent = detect_intent(text)

        result = brain(text, self.context, memory, self.dialogue)
        plan = result.get("plan", [])

        update_memory(text, intent, plan)

        print("[INTENT]", intent)
        print("[BRAIN RESULT]", result)
        print("[PLAN]", plan)

        self.respond(result)

        if plan:
            print("[EXECUTING PLAN]")
            self.executor.execute(plan)
            self.context.remember(text)