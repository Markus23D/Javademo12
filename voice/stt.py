import queue
import json
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import scipy.signal  # optional but you already installed it earlier


# -----------------------
# AUTO MIC PICKER (SAFE)
# -----------------------
def find_mic():
    devices = sd.query_devices()

    for i, d in enumerate(devices):
        if "Arctis Nova Pro Wireless" in d["name"] and d["max_input_channels"] > 0:
            return i

    # fallback
    return sd.default.device[0]


# -----------------------
# STT CLASS
# -----------------------
class STT:
    def __init__(self, bus, mic_device=None):

        self.bus = bus
        self.audio_queue = queue.Queue()

        self.model = Model("model")  # <-- keep your VOSK_MODEL_PATH if different

        self.mic_device = mic_device if mic_device is not None else find_mic()

        device_info = sd.query_devices(self.mic_device, "input")
        self.samplerate = int(device_info["default_samplerate"])

        self.recognizer = KaldiRecognizer(self.model, 16000)

        self.stream = sd.InputStream(
            device=self.mic_device,
            samplerate=self.samplerate,
            dtype="int16",
            channels=1,
            callback=self.callback
        )

    # -----------------------
    # AUDIO CALLBACK
    # -----------------------
    def callback(self, indata, frames, time, status):
        if status:
            print("[AUDIO STATUS]", status)

        self.audio_queue.put(np.frombuffer(indata, dtype=np.int16))

    # -----------------------
    # MAIN LOOP
    # -----------------------
    def start(self):
        self.stream.start()
        print(f"[STT] Started on device {self.mic_device} @ {self.samplerate}Hz")

        while True:
            audio = self.audio_queue.get()

            # -----------------------
            # RESAMPLE → 16k for Vosk
            # -----------------------
            resampled = scipy.signal.resample_poly(
                audio,
                16000,
                self.samplerate
            ).astype(np.int16)

            # -----------------------
            # SPEECH TO TEXT
            # -----------------------
            if self.recognizer.AcceptWaveform(resampled.tobytes()):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()

                if text:
                    print("[STT]", text)
                    self.bus.push_stt(text.lower())