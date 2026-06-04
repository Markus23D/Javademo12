from queue import Queue


class AudioBus:

    def __init__(self):
        self.stt_queue = Queue()
        self.tts_queue = Queue()

    # -----------------------
    # STT INPUT
    # -----------------------
    def push_stt(self, text: str):
        print("[BUS] push_stt →", text)
        self.stt_queue.put(text)

    def get_stt(self):
        if self.stt_queue.empty():
            return None
        text = self.stt_queue.get()
        print("[BUS] get_stt →", text)
        return text

    # -----------------------
    # TTS
    # -----------------------
    def push_tts(self, text: str):
        print(f"[BUS] push_tts → {text}")
        self.tts_queue.put(text)

    def get_tts(self):
        if self.tts_queue.empty():
            return None
        return self.tts_queue.get()
