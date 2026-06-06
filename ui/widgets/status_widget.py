from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt


class StatusWidget(QLabel):

    STATES = {
        "listening": ("Listening...", "#4fc3f7"),
        "thinking":  ("Thinking...",  "#ffb74d"),
        "speaking":  ("Speaking...",  "#81c784"),
        "standby":   ("Standby",      "#757575"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("font-size: 13px; font-weight: bold; letter-spacing: 1px;")
        self.set_state("listening")

    def set_state(self, state: str):
        label, color = self.STATES.get(state, ("...", "#ffffff"))
        self.setText(label.upper())
        self.setStyleSheet(
            f"font-size: 13px; font-weight: bold; letter-spacing: 2px; color: {color};"
        )
