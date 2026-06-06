import asyncio
import re
import edge_tts
import sounddevice as sd
import numpy as np
import io
from pydub import AudioSegment
import threading
import queue

from config import VOICE

speech_queue = queue.Queue()
is_speaking = False


# -----------------------
# PUBLIC API
# -----------------------
def speak(text: str):
    # Split on sentence boundaries so the first sentence starts playing
    # immediately while later sentences are buffered behind it.
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    for s in sentences:
        s = s.strip()
        if s:
            speech_queue.put(s)


def stop():
    global is_speaking
    is_speaking = False
    sd.stop()


def clear_queue():
    """Drain all pending speech so an interrupt feels immediate."""
    while not speech_queue.empty():
        try:
            speech_queue.get_nowait()
        except queue.Empty:
            break


# -----------------------
# WORKER THREAD
# -----------------------
def voice_worker():
    while True:
        text = speech_queue.get()
        try:
            asyncio.run(_speak(text))
        except Exception as e:
            print("[TTS ERROR]", e)


_worker_started = False


def start_tts_worker():
    global _worker_started
    if not _worker_started:
        threading.Thread(target=voice_worker, daemon=True).start()
        _worker_started = True


# -----------------------
# CORE TTS ENGINE
# -----------------------
async def _speak(text: str):
    global is_speaking
    is_speaking = True

    communicate = edge_tts.Communicate(text, VOICE)

    audio_bytes = bytearray()

    try:
        async for chunk in communicate.stream():
            if not is_speaking:
                break

            if chunk["type"] == "audio":
                audio_bytes.extend(chunk["data"])

        if not audio_bytes or not is_speaking:
            return

        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        samples = np.array(audio.get_array_of_samples(), dtype=np.int16)

        sd.play(samples, samplerate=audio.frame_rate, blocking=True)

    except Exception as e:
        print("[TTS ERROR]", e)

    finally:
        is_speaking = False