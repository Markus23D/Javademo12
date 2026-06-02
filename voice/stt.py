import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from Congif import VOSK_MODEL_PATH, SAMPLE_RATE

audio_queue = queue.Queue()

model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)


def callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))


stream = sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback
)

stream.start()


def listen():
    while True:
        data = audio_queue.get()

        if recognizer.AcceptWaveform(data):
            text = json.loads(recognizer.Result()).get("text", "")
            if text:
                return text.lower()