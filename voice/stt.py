import re
import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

import voice.tts as tts
from core.logger import log_stt_drop
from config import (
    SAMPLE_RATE,
    STT_COOLDOWN,
    WHISPER_MODEL_SIZE,
    WHISPER_DEVICE,
    WHISPER_SILENCE_THRESHOLD,
    WHISPER_SILENCE_DURATION,
    WHISPER_MIN_WORDS,
    WHISPER_SINGLE_WORD_ALLOWLIST,
    OWW_THRESHOLD,
)

# openwakeword chunk size: 1280 samples = 80ms at 16kHz
_OWW_CHUNK = 1280


class STT:

    def __init__(self, bus, mic_device=None):
        self.bus = bus
        self.mic_device = mic_device
        self._last_accepted = 0.0
        self.standby = False

        print(f"[STT] Loading Whisper model '{WHISPER_MODEL_SIZE}' on {WHISPER_DEVICE}...")
        self.model = WhisperModel(WHISPER_MODEL_SIZE, device=WHISPER_DEVICE, compute_type="int8")
        print("[STT] Model ready.")

        print("[STT] Loading openwakeword model 'hey_jarvis'...")
        try:
            from openwakeword.model import Model as OWWModel
            self._oww = OWWModel(wakeword_models=["hey_jarvis"], inference_framework="onnx")
            print("[STT] Wake word model ready.")
        except Exception as e:
            print(f"[STT] openwakeword unavailable ({e}) — falling back to Whisper-based wake detection")
            self._oww = None

    # -----------------------
    # MAIN LOOP
    # -----------------------
    def start(self):
        print(f"[STT] Listening — silence threshold={WHISPER_SILENCE_THRESHOLD}, "
              f"silence duration={WHISPER_SILENCE_DURATION}s, cooldown={STT_COOLDOWN}s")

        while True:
            try:
                self._listen_loop()
            except Exception as e:
                print(f"[STT CRASH] {e} — restarting in 2s...")
                time.sleep(2)

    def _listen_loop(self):
        chunk_samples = _OWW_CHUNK  # 80ms — works for both VAD and openwakeword
        chunk_duration = chunk_samples / SAMPLE_RATE

        buffer = np.array([], dtype=np.float32)
        silent_duration = 0.0
        recording = False

        with sd.InputStream(
            device=self.mic_device,
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=chunk_samples,
        ) as stream:
            while True:
                chunk, _ = stream.read(chunk_samples)
                chunk = chunk.flatten()

                # --------------------------------------------------
                # STANDBY: route audio to openwakeword, skip Whisper
                # --------------------------------------------------
                if self.standby:
                    if self._oww is not None:
                        chunk_int16 = (chunk * 32767).astype(np.int16)
                        prediction = self._oww.predict(chunk_int16)
                        if any(v >= OWW_THRESHOLD for v in prediction.values()):
                            print("[STT] Wake word detected (openwakeword)")
                            self._oww.reset()
                            self.bus.push_stt("__wake__")
                    else:
                        # Fallback: Whisper-based standby (original behaviour)
                        amplitude = float(np.abs(chunk).mean())
                        is_loud = amplitude > WHISPER_SILENCE_THRESHOLD

                        if is_loud:
                            recording = True
                            silent_duration = 0.0
                            buffer = np.concatenate([buffer, chunk])
                        elif recording:
                            buffer = np.concatenate([buffer, chunk])
                            silent_duration += chunk_duration
                            if silent_duration >= WHISPER_SILENCE_DURATION:
                                audio_copy = buffer.copy()
                                threading.Thread(
                                    target=self._process_standby_fallback,
                                    args=(audio_copy,),
                                    daemon=True,
                                ).start()
                                buffer = np.array([], dtype=np.float32)
                                silent_duration = 0.0
                                recording = False
                    continue

                # --------------------------------------------------
                # ACTIVE: normal VAD + Whisper pipeline
                # --------------------------------------------------
                amplitude = float(np.abs(chunk).mean())
                is_loud = amplitude > WHISPER_SILENCE_THRESHOLD

                if is_loud:
                    recording = True
                    silent_duration = 0.0
                    buffer = np.concatenate([buffer, chunk])

                elif recording:
                    buffer = np.concatenate([buffer, chunk])
                    silent_duration += chunk_duration

                    if silent_duration >= WHISPER_SILENCE_DURATION:
                        audio_copy = buffer.copy()
                        threading.Thread(target=self._process, args=(audio_copy,), daemon=True).start()
                        buffer = np.array([], dtype=np.float32)
                        silent_duration = 0.0
                        recording = False

    # -----------------------
    # TRANSCRIBE + FILTER (active mode)
    # -----------------------

    INTERRUPT_WORDS = {"stop", "cancel", "quiet", "silence", "shut up",
                       "thanks", "thank you", "goodbye", "bye", "cheers", "that's all"}

    def _process(self, audio: np.ndarray):
        if time.time() - self._last_accepted < STT_COOLDOWN:
            print("[STT] ✗ dropped — cooldown")
            return

        segments, _ = self.model.transcribe(
            audio,
            language="en",
            beam_size=5,
            vad_filter=True,
        )

        text = " ".join(seg.text.strip() for seg in segments).strip()

        if not text:
            log_stt_drop("empty")
            print("[STT] ✗ dropped — empty")
            return

        text_lower = text.lower()
        words = text.split()

        if tts.is_speaking:
            # Any real speech interrupts Jarvis — stop speaking and process the command
            print(f"[STT] Interrupted by: {text!r}")
            tts.stop()
            tts.clear_queue()

        text_clean = re.sub(r"[.!?,;]+", "", text_lower).strip()
        if len(words) < WHISPER_MIN_WORDS and text_clean not in WHISPER_SINGLE_WORD_ALLOWLIST:
            log_stt_drop("too short", text)
            print(f"[STT] ✗ dropped — too short ({text!r})")
            return

        print(f"[STT] ✓ {text!r}")
        self._last_accepted = time.time()
        self.bus.push_stt(text)

    def _process_standby_fallback(self, audio: np.ndarray):
        """Whisper-based wake detection used only when openwakeword is unavailable."""
        segments, _ = self.model.transcribe(audio, language="en", beam_size=3, vad_filter=True)
        text = " ".join(seg.text.strip() for seg in segments).strip().lower()
        if "jarvis" in text:
            print("[STT] Wake word detected (Whisper fallback)")
            self._last_accepted = time.time()
            self.bus.push_stt("__wake__")
        else:
            log_stt_drop("standby", text)
            print(f"[STT] ✗ standby — ignored ({text!r})")
