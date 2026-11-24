"""
Audio Controller for Nexus Wheel.
Plays low-latency sci-fi sound effects using Windows multimedia audio APIs.
"""

import os
import winsound
from database.db import DatabaseManager

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")

class AudioController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioController, cls).__new__(cls)
            cls._instance._db = DatabaseManager()
        return cls._instance

    def _play(self, filename: str, setting_key: str):
        if not self._db.get_setting("audio_enabled", True):
            return
        if not self._db.get_setting(setting_key, True):
            return
            
        wav_path = os.path.join(SOUNDS_DIR, filename)
        if os.path.exists(wav_path):
            try:
                # Play asynchronously and don't block UI
                winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
            except Exception as e:
                print(f"Audio playback error: {e}")

    def play_open(self):
        self._play("wheel_open.wav", "sound_open")

    def play_close(self):
        self._play("wheel_close.wav", "sound_close")

    def play_select(self):
        self._play("segment_select.wav", "sound_select")

    def play_execute(self):
        self._play("action_execute.wav", "sound_execute")

    def play_error(self):
        self._play("error.wav", "sound_error")
