import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer


class STT:

    def __init__(self, bus, mic_device=None):

        self.bus = bus
        self.audio_queue = queue.Queue()

        self.model = Model("model")  # your Vosk model path

        self.mic_device = mic_device if mic_device is not None else None

        device_info = sd.query_devices(self.mic_device, "input")
        self.samplerate = int(device_info["default_samplerate"])

        self.recognizer = KaldiRecognizer(self.model, 16000)

        self.stream = sd.InputStream(
            device=self.mic_device,
            samplerate=16000,
            dtype="int16",
            channels=1,
            callback=self.callback
        )

    # -----------------------
    # AUDIO CALLBACK
    # -----------------------
    def callback(self, indata, frames, time, status):
        if status:
            print(status)

        self.audio_queue.put(bytes(indata))

    # -----------------------
    # MAIN LOOP
    # -----------------------
    def start(self):

        print("[STT] Listening started...")

        self.stream.start()

        while True:

            data = self.audio_queue.get()

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "")

                if text:
                    print(f"[STT RAW] → {text}")

                    # 🔥 THIS IS THE MISSING PART
                    self.bus.push_stt(text)