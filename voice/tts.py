import asyncio
import edge_tts
import sounddevice as sd
import numpy as np
import io
from pydub import AudioSegment
import threading
import queue

VOICE = "en-GB-RyanNeural"

speech_queue = queue.Queue()
is_speaking = False


# -----------------------
# PUBLIC API
# -----------------------
def speak(text: str):
    speech_queue.put(text)


def stop():
    global is_speaking
    is_speaking = False
    sd.stop()


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


threading.Thread(target=voice_worker, daemon=True).start()


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

        if not audio_bytes:
            return

        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        samples = np.array(audio.get_array_of_samples(), dtype=np.int16)

        sd.play(samples, samplerate=audio.frame_rate, blocking=True)

    except Exception as e:
        print("[TTS ERROR]", e)

    finally:
        is_speaking = False