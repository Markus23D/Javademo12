VOICE = "en-GB-RyanNeural"

WAKE_WORDS = ["jarvis", "hey jarvis", "hey"]

VOSK_MODEL_PATH = "model"

SAMPLE_RATE = 16000

# -----------------------
# STT FILTERING
# -----------------------

# Minimum average word confidence (0.0–1.0).
# Vosk scores every recognised word; results below this are discarded as noise.
# Raise toward 0.85 if you still get false triggers; lower toward 0.60 if
# genuine commands are being dropped.
STT_MIN_CONFIDENCE = 0.75

# Minimum number of words before a result is forwarded.
# Single-word fragments (coughs, background TV, etc.) are almost always noise.
# Words in STT_SINGLE_WORD_ALLOWLIST bypass this check.
STT_MIN_WORDS = 2

# Single words that are always valid on their own (commands that are one word).
STT_SINGLE_WORD_ALLOWLIST = {
    "yes", "no", "confirm", "cancel", "stop",
    "jarvis", "standby", "shutdown", "restart",
}

# Seconds to ignore new input after a command is processed.
# Prevents double-triggers when Jarvis is speaking and the mic picks himself up.
STT_COOLDOWN = 1.0