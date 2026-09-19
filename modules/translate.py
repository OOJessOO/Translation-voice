import json
import urllib.parse
import urllib.request

_BASE = "https://translate.googleapis.com/translate_a/single"
_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) TraduVoix/0.1"}


def translate(text, src, tgt):
    """Translate via Google Translate free endpoint (no API key needed).

    Supports Malagasy (mg), French (fr), English (en). Returns the text.
    """
    if src == tgt or not text.strip():
        return text
    query = urllib.parse.urlencode(
        {"client": "gtx", "sl": src, "tl": tgt, "dt": "t", "q": text}
    )
    req = urllib.request.Request(_BASE + "?" + query, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.load(resp)
    return "".join(part[0] for part in payload[0] if part and part[0]).strip()


def translate_nllb(text, src, tgt):
    """Offline fallback using Meta NLLB-200 (optional; requires transformers).

    Install separately:  pip install transformers
    """
    from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

    model_name = "facebook/nllb-200-distilled-600M"
    tok = M2M100Tokenizer.from_pretrained(model_name)
    tok.src_lang = src
    model = M2M100ForConditionalGeneration.from_pretrained(model_name)

    encoded = tok(text, return_tensors="pt")
    generated = model.generate(
        **encoded, forced_bos_token_id=tok.convert_tokens_to_ids(tgt)
    )
    return tok.batch_decode(generated, skip_special_tokens=True)[0]