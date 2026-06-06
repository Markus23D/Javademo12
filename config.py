VOICE = "en-GB-RyanNeural"

DEFAULT_CITY = "Helsinge"

WAKE_WORDS = ["jarvis", "hey jarvis", "hey"]

SAMPLE_RATE = 16000

# -----------------------
# STT — Whisper (faster-whisper)
# -----------------------

# Model size: "tiny", "base", "small", "medium", "large-v3"
# "base" is the recommended sweet spot — good accuracy, fast on CPU.
# Use "small" if you have a GPU or want better accent handling.
WHISPER_MODEL_SIZE = "base"

# "cpu" or "cuda" (if you have an Nvidia GPU with CUDA installed)
WHISPER_DEVICE = "cpu"

# RMS amplitude threshold to detect speech vs silence (0.0–1.0).
# Lower = more sensitive. Raise if background noise causes false triggers.
WHISPER_SILENCE_THRESHOLD = 0.01

# Seconds of silence after speech before the buffer is sent for transcription.
WHISPER_SILENCE_DURATION = 0.8

# Minimum number of words to forward (short fragments are usually noise).
WHISPER_MIN_WORDS = 2

# Single words that are always valid commands regardless of WHISPER_MIN_WORDS.
WHISPER_SINGLE_WORD_ALLOWLIST = {
    "yes", "no", "confirm", "cancel", "stop",
    "jarvis", "standby", "shutdown", "restart",
    "play", "pause", "skip", "mute", "unmute", "next", "back",
    "resume", "previous", "unpause", "continue", "Stop",
    # dismissal phrases
    "thanks", "thank you", "goodbye", "bye", "cheers",
    "that's all", "that will be all",
}

# Seconds to ignore new input after a command is accepted.
STT_COOLDOWN = 1.5

# -----------------------
# Wake word (openwakeword)
# -----------------------

# Confidence threshold for "hey_jarvis" detection (0.0–1.0).
# Lower = more sensitive (more false positives). 0.5 is a good starting point.
OWW_THRESHOLD = 0.5