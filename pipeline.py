"""TraduVoix — maquette locale de traduction vocale continue.

Traduction parole->parole entre le malgache (mg), le français (fr) et
l'anglais (en), favorisant la fidélité de la voix (phase 2 voie clonée).

Usage:
  python pipeline.py --text "Bonjour" --src fr --tgt mg [--speak]
  python pipeline.py --record --src fr --tgt mg [--speak]
  python pipeline.py          # mode conversation interactif
"""
import argparse
import sys
from pathlib import Path

from config import (
    LANGUAGES,
    OUTPUT_DIR,
    RECORD_MAX_SECONDS,
    STT_DEVICE,
    STT_MODEL,
)
from modules import audio, translate, tts

recognizer = None


def _label(code):
    return LANGUAGES[code]["name"]


def _valid(code):
    return code in LANGUAGES


def ask(source_prompt, default=None):
    while True:
        answer = input(f"{source_prompt} [{', '.join(LANGUAGES)}]: ").strip().lower()
        if not answer and default:
            answer = default
        if _valid(answer):
            return answer
        print(f"Langue invalide. Choisissez parmi: {', '.join(LANGUAGES)}")


def process(text, src, tgt, speak, recorded_path=None):
    detected = src
    if src is None and recorded_path is not None:
        _, detected = recognizer.transcribe(str(recorded_path))
        if detected not in LANGUAGES:
            print(f"(langue détectée non supportée: {detected})")
            detected = "mg"

    translated = translate.translate(text, src or detected, tgt)
    print("\n" + "─" * 46)
    print(f"🗣  {_label(src or detected)}  : {text}")
    print(f"🌍  {_label(tgt)} : {translated}")
    print("─" * 46)

    if speak and translated:
        out = Path(OUTPUT_DIR) / f"{tgt}.mp3"
        out.parent.mkdir(exist_ok=True)
        tts.synthesize(translated, tgt, out)
        tts.play(out)


def record_and_process(src, tgt, speak=True):
    print(f"🎤 Parlez maintenant ({RECORD_MAX_SECONDS}s max, pause = fin)...")
    audio_data, _ = audio.record(max_seconds=RECORD_MAX_SECONDS)
    if len(audio_data) < 0.3 * audio.SAMPLE_RATE:
        print("(rien entendu)")
        return None

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    wav = Path(OUTPUT_DIR) / "capture.wav"
    audio.save_wav(audio_data, wav)

    print("⏳ Transcription...")
    text, detected = recognizer.transcribe(str(wav), language=src)
    if not text:
        print("(aucune parole reconnue)")
        return None

    print(f"(langue détectée: {_label(detected) if detected in LANGUAGES else detected})")
    process(text, detected if detected in LANGUAGES else src, tgt, speak, recorded_path=wav)
    return text


def interactive():
    global recognizer
    print("=== TraduVoix — conversation multilingue ===")
    print("Langues: mg = Malgache, fr = Français, en = English")
    src = ask("Votre langue")
    tgt = ask("Langue de l'interlocuteur")
    print("⏳ Chargement du modèle de reconnaissance...")
    from modules.stt import STT
    recognizer = STT(model_size=STT_MODEL, device=STT_DEVICE)
    while True:
        print()
        record_and_process(src, tgt)
        print("\n[Entrée] pour continuer, 'q' + Entrée pour quitter, "
              "'t' pour taper une phrase.")
        cmd = input("> ").strip().lower()
        if cmd == "q":
            break
        if cmd == "t":
            phrase = input(f"Phrase ({_label(src)}): ").strip()
            if phrase:
                process(phrase, src, tgt, speak=True)


def main():
    global recognizer
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text", help="phrase à traduire (mode texte)")
    ap.add_argument("--src", default=None, choices=list(LANGUAGES), help="langue source (auto si non précisé)")
    ap.add_argument("--tgt", default=None, choices=list(LANGUAGES), help="langue cible")
    ap.add_argument("--record", action="store_true", help="capturer au micro")
    ap.add_argument("--speak", action="store_true", help="lire la traduction à haute voix")
    ap.add_argument("--model", default=STT_MODEL, help="modèle whisper (tiny/base/small/medium)")
    ap.add_argument("--device", default=STT_DEVICE, help="cpu ou cuda")
    args = ap.parse_args()

    if not args.record and not args.text:
        interactive()
        return

    if not args.tgt:
        print("Précisez --tgt (langue cible).")
        sys.exit(1)

    if args.record or not args.text:
        print(f"⏳ Chargement du modèle de reconnaissance ({args.model}, {args.device})...")
        from modules.stt import STT
        recognizer = STT(model_size=args.model, device=args.device)

    if args.text:
        src = args.src
        if src is None:
            src = ask("Langue source")
        process(args.text, src, args.tgt, args.speak)
    else:
        record_and_process(args.src, args.tgt, args.speak)


if __name__ == "__main__":
    main()