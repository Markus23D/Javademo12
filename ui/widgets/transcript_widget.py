from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt


class TranscriptWidget(QWidget):

    MAX_PAIRS = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pair_count = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent;")

        self._inner = QWidget()
        self._inner.setStyleSheet("background: transparent;")
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(8, 4, 8, 4)
        self._inner_layout.setSpacing(2)
        self._inner_layout.addStretch()

        scroll.setWidget(self._inner)
        layout.addWidget(scroll)
        self._scroll = scroll

    def add_discord_line(self, text: str):
        label = QLabel(f"<span style='color:#7289da;'>Discord</span>  {text}")
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 12px; color: #aaaaaa; padding: 1px 0 4px 0;")
        label.setAlignment(Qt.AlignLeft)
        self._inner_layout.addWidget(label)
        self._pair_count += 1

        while self._pair_count > self.MAX_PAIRS:
            item = self._inner_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
            self._pair_count -= 1

        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )

    def add_entry(self, heard: str, response: str):
        user_label = QLabel(f"<span style='color:#4fc3f7;'>You</span>  {heard}")
        user_label.setWordWrap(True)
        user_label.setStyleSheet("font-size: 12px; color: #cccccc; padding: 1px 0;")
        user_label.setAlignment(Qt.AlignLeft)

        jarvis_label = QLabel(f"<span style='color:#81c784;'>Jarvis</span>  {response}")
        jarvis_label.setWordWrap(True)
        jarvis_label.setStyleSheet("font-size: 12px; color: #aaaaaa; padding: 1px 0 6px 0;")
        jarvis_label.setAlignment(Qt.AlignLeft)

        self._inner_layout.addWidget(user_label)
        self._inner_layout.addWidget(jarvis_label)
        self._pair_count += 1

        # Remove oldest pair (2 labels) if over limit
        while self._pair_count > self.MAX_PAIRS:
            for _ in range(2):
                item = self._inner_layout.takeAt(0)
                if item and item.widget():
                    item.widget().deleteLater()
            self._pair_count -= 1

        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )
