from queue import Queue
import threading

class AudioBus:
    def __init__(self):
        self.stt_queue = Queue()
        self.tts_queue = Queue()
        self.stop_signal = False

    # -----------------------
    # STT OUTPUT → brain input
    # -----------------------
    def push_stt(self, text: str):
        self.stt_queue.put(text)

    def get_stt(self):
        return self.stt_queue.get()

    # -----------------------
    # brain → TTS output
    # -----------------------
    def push_tts(self, text: str):
        self.tts_queue.put(text)

    def get_tts(self):
        return self.tts_queue.get()

    # -----------------------
    # interrupt system
    # -----------------------
    def stop_speaking(self):
        self.stop_signal = True

    def reset_stop(self):
        self.stop_signal = False