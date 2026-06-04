import queue
import json
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from config import (
    VOSK_MODEL_PATH,
    SAMPLE_RATE,
    STT_MIN_CONFIDENCE,
    STT_MIN_WORDS,
    STT_SINGLE_WORD_ALLOWLIST,
    STT_COOLDOWN,
)


class STT:

    def __init__(self, bus, mic_device=None):
        self.bus = bus
        self.audio_queue = queue.Queue()
        self.mic_device = mic_device

        self.model = Model(VOSK_MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.recognizer.SetWords(True)  # enable per-word confidence scores

        self._last_accepted = 0.0  # timestamp of last forwarded result

        self.stream = sd.InputStream(
            device=self.mic_device,
            samplerate=SAMPLE_RATE,
            dtype="int16",
            channels=1,
            callback=self.callback
        )

    # -----------------------
    # AUDIO CALLBACK
    # -----------------------
    def callback(self, indata, frames, time_info, status):
        if status:
            print("[STT STATUS]", status)
        self.audio_queue.put(bytes(indata))

    # -----------------------
    # RESULT FILTERING
    # -----------------------
    def _should_accept(self, result: dict) -> tuple[bool, str]:
        """
        Return (accept, reason) for a Vosk result dict.

        Filters applied in order:
          1. Cooldown  — ignore input too soon after the last accepted command
          2. Empty     — Vosk returned no text
          3. Min words — discard short fragments (unless in the allow-list)
          4. Confidence— discard low-confidence transcriptions
        """
        # 1. Cooldown
        if time.time() - self._last_accepted < STT_COOLDOWN:
            return False, "cooldown"

        text = result.get("text", "").strip()

        # 2. Empty result
        if not text:
            return False, "empty"

        words = text.split()

        # 3. Minimum word count (single known commands are exempt)
        if len(words) < STT_MIN_WORDS:
            if text.lower() not in STT_SINGLE_WORD_ALLOWLIST:
                return False, f"too short ({text!r})"

        # 4. Per-word confidence (only available when SetWords(True) is set)
        word_results = result.get("result", [])
        if word_results:
            avg_conf = sum(w.get("conf", 1.0) for w in word_results) / len(word_results)
            if avg_conf < STT_MIN_CONFIDENCE:
                return False, f"low confidence {avg_conf:.2f} ({text!r})"

        return True, "ok"

    # -----------------------
    # MAIN LOOP
    # -----------------------
    def start(self):
        print("[STT] Listening started...")
        print(f"[STT] Filters: confidence≥{STT_MIN_CONFIDENCE}  "
              f"min_words={STT_MIN_WORDS}  cooldown={STT_COOLDOWN}s")

        self.stream.start()

        while True:
            data = self.audio_queue.get()

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                accept, reason = self._should_accept(result)

                if accept:
                    text = result["text"].strip()
                    print(f"[STT] ✓ {text!r}")
                    self._last_accepted = time.time()
                    self.bus.push_stt(text)
                else:
                    print(f"[STT] ✗ dropped — {reason}")
