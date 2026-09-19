import wave

import numpy as np
import sounddevice as sd

from config import SAMPLE_RATE, SILENCE_GAP_SECONDS, SILENCE_THRESHOLD

CHUNK_S = 0.1


def record(max_seconds=8.0, sample_rate=SAMPLE_RATE, silence_gap=SILENCE_GAP_SECONDS, threshold=SILENCE_THRESHOLD):
    """Record speech from the microphone and stop on a silence gap.

    Waits until something is heard, then captures until `silence_gap`
    of near-silence or `max_seconds` of speech elapsed. Returns float32 mono.
    """
    block_len = int(sample_rate * CHUNK_S)
    frames = []
    start = sd.time()
    first_voice = None
    last_voice = None

    with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32") as stream:
        while True:
            block, _ = stream.read(block_len)
            now = sd.time()
            rms = float(np.sqrt(np.mean(block**2)))
            if first_voice is None:
                if rms > threshold:
                    first_voice = last_voice = now
                elif now - start > max_seconds:
                    break  # nothing was heard in time
                frames.append(block[:, 0])
                continue
            if rms > threshold:
                last_voice = now
            frames.append(block[:, 0])
            if now - first_voice > 0.5 and now - last_voice > silence_gap:
                break
            if now - first_voice >= max_seconds:
                break

    audio = np.concatenate(frames) if frames else np.zeros(0, dtype=np.float32)
    return trim_silence(audio, sample_rate, threshold), len(audio) / sample_rate


def trim_silence(audio, sample_rate=SAMPLE_RATE, threshold=SILENCE_THRESHOLD):
    if len(audio) < sample_rate:
        return audio
    base = int(0.15 * sample_rate)
    usable = len(audio) // base * base
    rms = np.sqrt(np.mean(np.square(audio[:usable].reshape(-1, base)), axis=1))
    voiced = np.where(rms > threshold)[0]
    if voiced.size == 0:
        return audio
    start = max(0, int(voiced[0] * base - 0.2 * sample_rate))
    end = min(len(audio), int((voiced[-1] + 1) * base + 0.2 * sample_rate))
    return audio[start:end]


def save_wav(audio, path, sample_rate=SAMPLE_RATE):
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return path