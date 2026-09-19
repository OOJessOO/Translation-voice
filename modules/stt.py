from pathlib import Path

from faster_whisper import WhisperModel


class STT:
    def __init__(self, model_size="small", device="cpu"):
        compute_type = "int8" if device == "cpu" else "float16"
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, wav_path, language=None):
        """Transcribe audio file. Returns (text, detected_language)."""
        segments, info = self.model.transcribe(
            wav_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text, info.language

    def recognize(self, audio_path, language=None):
        return self.transcribe(audio_path, language=language)