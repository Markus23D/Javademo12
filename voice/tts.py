import asyncio
import numpy as np
import sounddevice as sd
import edge_tts
import queue
import threading
import time
from Congif import VOICE


voice_queue = queue.PriorityQueue()
stop_signal = False
lock = threading.Lock()


def speak(text, priority=1):
    print("Jarvis:", text)
    voice_queue.put((priority, time.time(), text))


def stop():
    global stop_signal
    stop_signal = True
    sd.stop()


def voice_worker():
    global stop_signal

    while True:
        _, _, text = voice_queue.get()

        stop_signal = False

        with lock:
            asyncio.run(_speak(text))


threading.Thread(target=voice_worker, daemon=True).start()


async def _speak(text):
    communicate = edge_tts.Communicate(text, VOICE)

    buffer = bytearray()

    async for chunk in communicate.stream():
        if stop_signal:
            return
        if chunk["type"] == "audio":
            buffer.extend(chunk["data"])

    audio = np.frombuffer(buffer, dtype=np.int16)

    sd.play(audio, samplerate=24000)
    sd.wait()