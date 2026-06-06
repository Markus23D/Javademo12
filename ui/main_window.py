import threading
import random

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu, QApplication
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor

from ui.widgets.OrbWidget import OrbWidget
from ui.widgets.status_widget import StatusWidget
from ui.widgets.transcript_widget import TranscriptWidget

from core.brain import brain
from core.context import Context
from core.executor import Executor
from core.dialogue import DialogueManager
from core.memory import memory, update_memory
from core.skills_loader import load_skills
from core.normalizer import Normalizer
from core.logger import log_heard, log_command
from voice.audio_bus import AudioBus
from voice.stt import STT
from voice.loopback_stt import LoopbackSTT
from voice.tts import speak, stop, clear_queue, start_tts_worker
import voice.tts as tts


class MainWindow(QWidget):

    _set_state_signal = Signal(str)
    _add_entry_signal = Signal(str, str)
    _set_heard_signal = Signal(str)
    _add_discord_signal = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Jarvis")
        self.resize(500, 600)

        # Frameless transparent window — orb floats on the desktop
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool  # hides from taskbar
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setStyleSheet("""
            QWidget {
                background: transparent;
                color: white;
                font-size: 18px;
            }
        """)

        self._drag_pos = None
        self._snap_to_top_right()

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.orb = OrbWidget()
        self.state_label = StatusWidget()
        self.heard_label = QLabel("")
        self.heard_label.setAlignment(Qt.AlignCenter)
        self.heard_label.setStyleSheet("font-size: 13px; color: #aaaaaa; font-style: italic; background: transparent;")
        self.heard_label.setWordWrap(True)

        self.transcript = TranscriptWidget()
        self.transcript.setFixedHeight(160)

        layout.addStretch()
        layout.addWidget(self.orb, alignment=Qt.AlignCenter)
        layout.addWidget(self.state_label)
        layout.addWidget(self.heard_label)
        layout.addSpacing(8)
        layout.addWidget(self.transcript)

        self.setLayout(layout)

        self.mode = "active"

        # Connect signals so background threads can safely update the UI
        self._set_state_signal.connect(self.state_label.set_state)
        self._add_entry_signal.connect(self.transcript.add_entry)
        self._set_heard_signal.connect(self.heard_label.setText)
        self._add_discord_signal.connect(self.transcript.add_discord_line)

        start_tts_worker()
        load_skills()

        self._setup_tray()

        self.bus = AudioBus()
        self.context = Context()
        self.dialogue = DialogueManager()
        self.executor = Executor(self.context)
        self.stt = STT(self.bus)
        self.loopback = LoopbackSTT(self.bus, self.stt.model)

        threading.Thread(target=self.run_stt, daemon=True).start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_stt)
        self.timer.start(100)

        self.discord_timer = QTimer()
        self.discord_timer.timeout.connect(self.poll_discord)
        self.discord_timer.start(200)

        # Poll TTS state to keep the status label in sync
        self.tts_timer = QTimer()
        self.tts_timer.timeout.connect(self._sync_tts_state)
        self.tts_timer.start(150)

        speak("What can I do for you sir")

    # -----------------------
    # STATE SYNC
    # -----------------------
    def _sync_tts_state(self):
        if self.mode == "standby":
            self.state_label.set_state("standby")
        elif tts.is_speaking:
            self.state_label.set_state("speaking")
        else:
            self.state_label.set_state("listening")

    # -----------------------
    # STANDBY
    # -----------------------
    def enter_standby_mode(self):
        print("[UI] ENTERING STANDBY MODE")
        self.mode = "standby"
        self.stt.standby = True
        stop()
        self.hide()

    def wake_up(self):
        print("[UI] WAKING UP")
        self.mode = "active"
        self.stt.standby = False
        self._snap_to_top_right()
        self.show()
        self.raise_()
        self.activateWindow()
        speak("I'm back online sir")

    # -----------------------
    # SYSTEM TRAY
    # -----------------------
    def _setup_tray(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#00bfff"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 28, 28)
        painter.end()

        self.tray = QSystemTrayIcon(QIcon(pixmap), self)
        self.tray.setToolTip("Jarvis — right-click for options")

        menu = QMenu()
        toggle_action = menu.addAction("Show / Hide")
        toggle_action.triggered.connect(self._tray_toggle)
        menu.addSeparator()
        self._discord_action = menu.addAction("Discord Listening: OFF")
        self._discord_action.triggered.connect(self._toggle_discord)
        menu.addSeparator()
        quit_action = menu.addAction("Quit Jarvis")
        quit_action.triggered.connect(QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _snap_to_top_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 12
        x = screen.right() - self.width() - margin
        y = screen.top() + margin
        self.move(x, y)

    def _tray_toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._tray_toggle()

    def _toggle_discord(self):
        if self.loopback.active:
            self.loopback.disable()
            self._discord_action.setText("Discord Listening: OFF")
            speak("Discord listening disabled, sir.")
        else:
            self.loopback.enable()
            self._discord_action.setText("Discord Listening: ON")
            speak("Now listening to your Discord call, sir.")

    # Drag to reposition
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # -----------------------
    # STT THREAD
    # -----------------------
    def run_stt(self):
        print("[THREAD] STT starting...")
        self.stt.start()  # STT now has its own internal restart loop

    # -----------------------
    # RESPOND (UI side-effects only)
    # -----------------------
    def respond(self, result):
        plan = result.get("plan", [])

        if not plan:
            speak("I didn't understand that sir")
            return

        for step in plan:
            if step.get("action") == "standby":
                self.stt.standby = True
                speak("Going idle sir")
                QTimer.singleShot(2000, self.enter_standby_mode)

    # -----------------------
    # POLL STT BUS
    # -----------------------
    def poll_stt(self):
        text = self.bus.get_stt()

        if not text:
            return

        print("[MAIN RECEIVED]", text)
        raw_text = text
        text = Normalizer.clean(text)

        log_heard(raw_text, text)
        if raw_text != text:
            print(f"[NORMALIZED] {raw_text} -> {text}")

        if text == "__wake__":
            self.wake_up()
            return

        for prefix in ["hey jarvis ", "ok jarvis ", "jarvis ", "hey jarvis", "ok jarvis", "jarvis"]:
            if text.lower().startswith(prefix):
                text = text[len(prefix):]
                break

        FILLERS = ["now ", "please ", "can you ", "could you ", "would you ", "just ", "hey ", "go ahead and "]
        changed = True
        while changed:
            changed = False
            for filler in FILLERS:
                if text.lower().startswith(filler):
                    text = text[len(filler):]
                    changed = True
                    break

        # Dismissal — go back to hidden standby mode
        DISMISSAL = {"thanks", "thank you", "that's all", "that will be all", "goodbye", "bye", "cheers"}
        cleaned = text.lower().strip().rstrip(".!?,;")
        if cleaned in DISMISSAL:
            speak("Of course sir")
            QTimer.singleShot(2000, self.enter_standby_mode)
            return

        self._set_heard_signal.emit(f'"{text}"')
        stop()
        clear_queue()

        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    # -----------------------
    # THINKING ACKNOWLEDGMENTS
    # -----------------------
    _THINKING_PHRASES = [
        "Right away, sir.",
        "On it.",
        "Of course.",
        "One moment.",
        "Certainly, sir.",
        "Consider it done.",
        "Leave it with me.",
        "Understood.",
    ]

    _CHAT_THINKING_PHRASES = [
        "Let me think on that.",
        "Interesting question.",
        "Give me a moment.",
        "One second.",
        "Processing.",
    ]

    # -----------------------
    # POLL DISCORD BUS
    # -----------------------
    def poll_discord(self):
        text = self.bus.get_discord()
        if not text:
            return

        self._add_discord_signal.emit(text)

        # If someone in the call says "Jarvis", treat it as a command
        text_lower = text.lower()
        for prefix in ["hey jarvis ", "ok jarvis ", "jarvis "]:
            if prefix in text_lower:
                idx = text_lower.index(prefix) + len(prefix)
                command = text[idx:].strip()
                if command:
                    print(f"[LOOPBACK] Command from Discord: {command!r}")
                    threading.Thread(target=self._process, args=(command,), daemon=True).start()
                break

    # -----------------------
    # PROCESS (background thread)
    # -----------------------
    def _process(self, text):
        self._set_state_signal.emit("thinking")

        # Quick intent peek — if it's going to hit the AI (slow), acknowledge first
        from core.intent import detect_intent
        intent_hint = detect_intent(text.lower().strip())
        if intent_hint == "chat":
            speak(random.choice(self._CHAT_THINKING_PHRASES))

        result = brain(text, self.context, memory, self.dialogue)
        plan = result.get("plan", [])
        intent = result.get("skill", "unknown")

        update_memory(text, intent, plan)

        log_command(intent, result.get("skill", "unknown"), plan)
        print("[SKILL]", intent)
        print("[BRAIN RESULT]", result)
        print("[PLAN]", plan)

        spoken = next(
            (s["value"] for s in plan if s.get("action") == "speak" and s.get("value")),
            "..."
        )
        self._add_entry_signal.emit(text, spoken)
        self.respond(result)

        if plan:
            print("[EXECUTING PLAN]")
            self.executor.execute(plan)
            self.context.remember(text)
