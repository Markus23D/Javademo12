import math
import voice.tts as tts

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QLinearGradient, QBrush, QPen, QFont
from PySide6.QtWidgets import QWidget


class OrbWidget(QWidget):

    def __init__(self):
        super().__init__()
        self._angle = 0.0
        self._pulse = 0.0       # 0..2π breathing cycle
        self._wave = 0.0        # waveform phase when speaking
        self.setMinimumSize(320, 320)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

    def tick(self):
        self._angle += 0.4
        self._pulse += 0.035
        if tts.is_speaking:
            self._wave += 0.18
        self.update()

    # ------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        speaking = tts.is_speaking

        # Breathing scale — subtle size pulse when idle
        breath = 1.0 + (0.03 * math.sin(self._pulse)) if not speaking else 1.0
        R = 80 * breath  # core radius

        # ── 1. DEEP BACKGROUND GLOW ───────────────────────────────────
        bg = QRadialGradient(cx, cy, R * 3.2)
        bg.setColorAt(0.0, QColor(0, 60, 120, 60))
        bg.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(bg))
        p.drawEllipse(int(cx - R * 3.2), int(cy - R * 3.2), int(R * 6.4), int(R * 6.4))

        # ── 2. OUTER TICK RING ────────────────────────────────────────
        for i in range(0, 360, 15):
            rad = math.radians(i + self._angle * 0.5)
            is_major = (i % 45 == 0)
            length = 14 if is_major else 7
            alpha = 180 if is_major else 60
            r_inner = R + 55
            r_outer = r_inner + length
            x1 = cx + math.cos(rad) * r_inner
            y1 = cy + math.sin(rad) * r_inner
            x2 = cx + math.cos(rad) * r_outer
            y2 = cy + math.sin(rad) * r_outer
            p.setPen(QPen(QColor(0, 180, 255, alpha), 1.5 if is_major else 1))
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # ── 3. ROTATING DASHED OUTER RING ────────────────────────────
        pen = QPen(QColor(0, 200, 255, 70), 1)
        pen.setStyle(Qt.DashLine)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        ro = R + 48
        p.drawEllipse(int(cx - ro), int(cy - ro), int(ro * 2), int(ro * 2))

        # ── 4. COUNTER-ROTATING ARC SEGMENTS ────────────────────────
        for i, (gap, alpha, width, offset) in enumerate([
            (30, 200, 2.5,  0),
            (45, 100, 1.5, 15),
        ]):
            rm = R + 28 + i * 14
            p.save()
            p.translate(cx, cy)
            p.rotate(-self._angle * (1 + i * 0.5) + offset)
            p.translate(-cx, -cy)
            pen = QPen(QColor(0, 220, 255, alpha), width)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            angle = 0
            while angle < 360:
                start = int(angle * 16)
                span = int((gap * 0.6) * 16)
                p.drawArc(int(cx - rm), int(cy - rm), int(rm * 2), int(rm * 2), start, span)
                angle += gap
            p.restore()

        # ── 5. WAVEFORM / PULSE RING (speaking indicator) ────────────
        if speaking:
            pts = 120
            for i in range(pts):
                frac = i / pts
                base_angle = math.radians(frac * 360)
                amp = 8 * math.sin(self._wave + frac * math.pi * 8)
                r1 = R + 8 + amp
                r2 = R + 8
                x1 = cx + math.cos(base_angle) * r1
                y1 = cy + math.sin(base_angle) * r1
                x2 = cx + math.cos(base_angle) * r2
                y2 = cy + math.sin(base_angle) * r2
                alpha = int(180 + 75 * math.sin(self._wave + frac * math.pi * 4))
                p.setPen(QPen(QColor(0, 255, 220, alpha), 1.5))
                p.drawLine(int(x1), int(y1), int(x2), int(y2))
        else:
            # Thin static ring when idle
            p.setPen(QPen(QColor(0, 180, 255, 80), 1))
            p.setBrush(Qt.NoBrush)
            ri = R + 8
            p.drawEllipse(int(cx - ri), int(cy - ri), int(ri * 2), int(ri * 2))

        # ── 6. CORE GLOW ──────────────────────────────────────────────
        core_color = QColor(0, 255, 220) if speaking else QColor(0, 200, 255)

        glow = QRadialGradient(cx, cy, R)
        glow.setColorAt(0.00, QColor(200, 255, 255, 220))
        glow.setColorAt(0.25, QColor(core_color.red(), core_color.green(), core_color.blue(), 180))
        glow.setColorAt(0.60, QColor(0, 80, 160, 100))
        glow.setColorAt(1.00, QColor(0, 20, 60, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(int(cx - R), int(cy - R), int(R * 2), int(R * 2))

        # ── 7. INNER NUCLEUS ──────────────────────────────────────────
        nucleus_r = 28 + (4 * math.sin(self._pulse)) if not speaking else 32
        nucleus = QRadialGradient(cx, cy, nucleus_r)
        nucleus.setColorAt(0.0, QColor(255, 255, 255, 230))
        nucleus.setColorAt(0.4, QColor(120, 230, 255, 160))
        nucleus.setColorAt(1.0, QColor(0, 100, 200, 0))
        p.setBrush(QBrush(nucleus))
        p.drawEllipse(int(cx - nucleus_r), int(cy - nucleus_r),
                      int(nucleus_r * 2), int(nucleus_r * 2))

        # ── 8. CROSSHAIR LINES ────────────────────────────────────────
        for angle_deg in [0, 90, 180, 270]:
            rad = math.radians(angle_deg + self._angle * 0.3)
            for dist in [R * 0.35, R * 0.65]:
                lx = cx + math.cos(rad) * dist
                ly = cy + math.sin(rad) * dist
                p.setPen(QPen(QColor(180, 240, 255, 60), 1))
                p.drawLine(int(lx - 4), int(ly), int(lx + 4), int(ly))
                p.drawLine(int(lx), int(ly - 4), int(lx), int(ly + 4))

        # ── 9. J.A.R.V.I.S LABEL ─────────────────────────────────────
        font = QFont("Segoe UI")
        font.setBold(True)
        font.setPointSize(13)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 8)
        p.setFont(font)

        # Glow shadow
        p.setPen(QColor(0, 200, 255, 60))
        p.drawText(self.rect().adjusted(2, 2, 2, 2), Qt.AlignCenter, "J.A.R.V.I.S")
        p.setPen(QColor(210, 245, 255, 255))
        p.drawText(self.rect(), Qt.AlignCenter, "J.A.R.V.I.S")
