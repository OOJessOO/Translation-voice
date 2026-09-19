import subprocess
import tempfile
from pathlib import Path

from gtts import gTTS

_MG_MODEL = None
_MG_TOKENIZER = None
MG_MODEL_NAME = "facebook/mms-tts-mlg"  # Meta MMS, voix malgache (local, offline)


def _mg_synthesize(text, out_path):
    """Synthèse locale en malgache via Meta MMS TTS (VITS)."""
    global _MG_MODEL, _MG_TOKENIZER
    if _MG_MODEL is None:
        import torch
        from transformers import VitsModel, VitsTokenizer

        _MG_TOKENIZER = VitsTokenizer.from_pretrained(MG_MODEL_NAME)
        _MG_MODEL = VitsModel.from_pretrained(MG_MODEL_NAME)

    inputs = _MG_TOKENIZER(text, return_tensors="pt")
    import torch

    with torch.no_grad():
        waveform = _MG_MODEL(**inputs).waveform[0]

    sr = _MG_MODEL.config.sampling_rate
    pcm = (waveform.numpy().clip(-1, 1) * 32767).astype("int16")
    import wave

    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    return out_path


def synthesize(text, lang, out_path=None):
    """Synthèse vocale: fr/en via Google TTS, mg via Meta MMS (local).

    Returns the path of the generated audio file.
    """
    out_path = Path(out_path) if out_path else Path(tempfile.mkstemp(suffix=".mp3")[1])
    if lang == "mg":
        return _mg_synthesize(text, out_path.with_suffix(".wav"))
    gTTS(text=text, lang=lang).save(str(out_path))
    return out_path


def play(path):
    """Play an audio file (any format ffplay supports)."""
    subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", str(path)],
        check=False,
    )