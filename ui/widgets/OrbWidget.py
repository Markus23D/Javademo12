from PySide6.QtCore import Qt, QTimer, Property
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QBrush, QPen, QFont
from PySide6.QtWidgets import QWidget
import math


class OrbWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._angle = 0
        self._glow = 1.0
        self._radius = 90

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

        self.setMinimumSize(400, 400)

    def tick(self):
        self._angle += 0.6
        self.update()

    # ---------------- DRAW ----------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # =========================================================
        # 1. OUTER DIGITAL SPHERE (GRID FEEL)
        # =========================================================
        for i in range(0, 360, 10):
            rad = math.radians(i + self._angle)

            x1 = cx + math.cos(rad) * (self._radius + 80)
            y1 = cy + math.sin(rad) * (self._radius + 80)

            x2 = cx + math.cos(rad) * (self._radius + 95)
            y2 = cy + math.sin(rad) * (self._radius + 95)

            p.setPen(QPen(QColor(0, 200, 255, 40), 1))
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # =========================================================
        # 2. ROTATING HUD RINGS (MAIN FEATURE)
        # =========================================================
        p.save()
        p.translate(cx, cy)
        p.rotate(self._angle)
        p.translate(-cx, -cy)

        for i in range(3):
            radius = self._radius + (i * 25)

            pen = QPen(QColor(0, 220, 255, 120 - i * 30), 2)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)

            p.drawEllipse(int(cx - radius),
                          int(cy - radius),
                          int(radius * 2),
                          int(radius * 2))

        p.restore()

        # =========================================================
        # 3. HUD ARC SEGMENTS
        # =========================================================
        pen = QPen(QColor(0, 255, 255, 180), 3)
        p.setPen(pen)

        for i in range(0, 360, 20):
            start_angle = (i + self._angle) * 16
            span = 8 * 16

            p.drawArc(int(cx - self._radius - 20),
                      int(cy - self._radius - 20),
                      int((self._radius + 20) * 2),
                      int((self._radius + 20) * 2),
                      start_angle,
                      span)

        # =========================================================
        # 4. CORE ENERGY ORB (REPLACED WITH GLOW CORE)
        # =========================================================
        glow = QRadialGradient(cx, cy, self._radius * 0.9)

        # bright energetic center (no solid white disk anymore)
        glow.setColorAt(0.0, QColor(180, 255, 255, 200))
        glow.setColorAt(0.2, QColor(0, 255, 240, 160))
        glow.setColorAt(0.5, QColor(0, 140, 255, 120))
        glow.setColorAt(1.0, QColor(0, 80, 150, 0))

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(int(cx - self._radius),
                      int(cy - self._radius),
                      int(self._radius * 2),
                      int(self._radius * 2))

        # subtle inner pulse (soft nucleus instead of solid orb)
        inner = QRadialGradient(cx, cy, 40)
        inner.setColorAt(0.0, QColor(255, 255, 255, 120))
        inner.setColorAt(1.0, QColor(255, 255, 255, 0))

        p.setBrush(QBrush(inner))
        p.drawEllipse(int(cx - 40), int(cy - 40), 80, 80)

        # =========================================================
        # 5. J.A.R.V.I.S TEXT
        # =========================================================
        font = QFont("Segoe UI")
        font.setBold(True)
        font.setPointSize(16)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 6)

        p.setFont(font)
        p.setPen(QColor(220, 255, 255, 255))

        p.drawText(self.rect(), Qt.AlignCenter, "J.A.R.V.I.S")