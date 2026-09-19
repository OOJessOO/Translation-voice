# TraduVoix — maquette de traduction vocale continue

Prototype local de traduction **parole → parole** entre 3 langues :
**malgache (mg)**, **français (fr)** et **anglais (en)**.

Objectif de la future startup : chaque personne parle sa langue, écoute la
conversation dans sa langue, avec **la voix de l'émetteur conservée** (~80%+).
Cette maquette valide le pipeline de base ; la fidélité de la voix est la
phase 2 (voir [Perspectives](#perspectives)).

## Architecture

```
microphone ──▶ STT (faster-whisper, local)  →  texte source
     │
     ▼
traduction (Google endpoint gratuit, mg/fr/en)  →  texte cible
     │
     ▼
TTS : fr/en → Google TTS (naturel)
      mg    → Meta MMS-VITS "facebook/mms-tts-mlg" (local, offline)
     │
     ▼
lecture (ffplay)
```

## Installation

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Le 1er lancement télécharge les modèles (~600 Mo) :
- `Systran/faster-whisper-base` (reconnaissance vocale, CPU)
- `facebook/mms-tts-mlg` (voix malgache)

## Utilisation

```bash
# phrase tapée, sans micro
.venv/bin/python pipeline.py --text "Salama e, manao ahoana ianao?" --src mg --tgt fr --speak

# enregistrement au micro (démo complète)
.venv/bin/python pipeline.py --record --src fr --tgt mg --speak

# conversation interactive
.venv/bin/python pipeline.py

# autres modèles de reconnaissance :
.venv/bin/python pipeline.py --record --src mg --tgt en --model small   # + précis, + lent
```

## Qualité (honnête, aujourd'hui)

| Étape                    | Qualité actuelle                                     |
|--------------------------|------------------------------------------------------|
| Transcription malgache   | Correcte sur parole réelle, imparfaite sur voix synth. `--model small` aide |
| Traduction mg↔fr↔en      | Bonne (Google). Parfois simplifie les expressions    |
| Synthèse fr/en           | Naturelle (Google voice)                             |
| Synthèse malgache        | Fonctionnelle, voix unique (Meta MMS), pas clonée    |
| Fidélité de la voix      | **Non implémentée** — c'est la phase 2               |

## Limites connues

- Latence : ~2 s/phrase (whisper base, CPU), 25 s+ avec `small`.
- Whisper ne détecte pas toujours le malgache seul → la langue source est
  toujours fixée par l'utilisateur.
- Le micro nécessite un son réel ; la voix MMS synthétique dégrade la
  transcription.

## Perspectives (phase 2)

1. **Fidélité de la voix** : clonage cross-lingue via XTTS-v2 (fr/en) —
   nécessite une machine GPU plus puissante (≥6 Go VRAM). Le malgache reste
   un défi ouvert (voix clonée MG n'existe pas en open source).
2. **Traitement phrase par phrase** avec lecture des idiomes.
3. **Textes sous-titres** bilingues à l'écran.
4. **Université en ligne/flux continu**, plusieurs récepteurs.