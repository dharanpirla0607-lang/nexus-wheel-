"""
Audio Feedback Page for Nexus Wheel Dashboard.
Configures procedural sci-fi audio sound effects, volume, and playback toggles.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSlider, QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal
from database.db import DatabaseManager
from windows.audio_controller import AudioController

class AudioFeedbackPage(QWidget):
    audio_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self._audio = AudioController()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Audio Feedback")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Crisp mechanical ticks, sci-fi sweeps, and confirmation chimes for actions.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 4px;")
        layout.addWidget(desc)

        # 1. Master Audio & Volume Card
        c1 = QFrame()
        c1.setObjectName("card")
        l1 = QVBoxLayout(c1)
        l1.setSpacing(14)

        h1 = QLabel("Master Sound Controls")
        h1.setObjectName("card_header")
        l1.addWidget(h1)

        self.cb_master = QCheckBox("Enable Audio Feedback & Sound Effects")
        self.cb_master.setChecked(self._db.get_setting("audio_enabled", True))
        self.cb_master.toggled.connect(lambda v: self._save("audio_enabled", v))
        l1.addWidget(self.cb_master)

        # Volume Slider
        vol_pct = int(float(self._db.get_setting("audio_volume", 0.80)) * 100)
        self.lbl_vol = QLabel(f"Master Sound Volume: {vol_pct}%")
        self.lbl_vol.setStyleSheet("font-weight: 600; color: #FFFFFF;")
        
        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(vol_pct)
        self.slider_vol.valueChanged.connect(self._on_volume_changed)

        l1.addWidget(self.lbl_vol)
        l1.addWidget(self.slider_vol)
        layout.addWidget(c1)

        # 2. Individual Sound Effects Card
        c2 = QFrame()
        c2.setObjectName("card")
        l2 = QVBoxLayout(c2)
        l2.setSpacing(12)

        h2 = QLabel("Sound Triggers")
        h2.setObjectName("card_header")
        l2.addWidget(h2)

        triggers = [
            ("Wheel Opening Sound", "sound_open", self._audio.play_open),
            ("Wheel Closing Sound", "sound_close", self._audio.play_close),
            ("Segment Selection Tick", "sound_select", self._audio.play_select),
            ("Action Execution Chime", "sound_execute", self._audio.play_execute),
            ("Error Notification Buzz", "sound_error", self._audio.play_error)
        ]

        for name, key, test_fn in triggers:
            row = QHBoxLayout()
            cb = QCheckBox(name)
            cb.setChecked(self._db.get_setting(key, True))
            cb.toggled.connect(lambda v, k=key: self._save(k, v))

            btn_test = QPushButton("▶ Test")
            btn_test.setObjectName("secondary_btn")
            btn_test.setFixedWidth(70)
            btn_test.clicked.connect(test_fn)

            row.addWidget(cb, 1)
            row.addWidget(btn_test)
            l2.addLayout(row)

        layout.addWidget(c2)
        layout.addStretch()

    def _on_volume_changed(self, v):
        self.lbl_vol.setText(f"Master Sound Volume: {v}%")
        self._db.set_setting("audio_volume", v / 100.0)
        self.audio_changed.emit()

    def _save(self, key, val):
        self._db.set_setting(key, val)
        self.audio_changed.emit()
