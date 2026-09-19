LANGUAGES = {
    "mg": {
        "name": "Malgache",
        "whisper": "mg",
        "google": "mg",
        "gtts": "mg",
    },
    "fr": {
        "name": "Français",
        "whisper": "fr",
        "google": "fr",
        "gtts": "fr",
    },
    "en": {
        "name": "English",
        "whisper": "en",
        "google": "en",
        "gtts": "en",
    },
}

DEFAULT_LANGS = ("mg", "fr", "en")

STT_MODEL = "small"
STT_DEVICE = "cpu"

SAMPLE_RATE = 16000
RECORD_MAX_SECONDS = 12.0
SILENCE_GAP_SECONDS = 1.6
SILENCE_THRESHOLD = 0.010

OUTPUT_DIR = "outputs"