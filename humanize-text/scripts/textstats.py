"""Shared text statistics for scan.py, voice.py and the style model.

Feature definitions are identical to the corpus analysis behind data/baselines.json, so a text's
numbers can be compared with the measured human and AI norms directly. Pure Python; pymorphy3 and
razdel are optional (better Russian lemmas and sentence splitting when installed).
"""
import math
import re
from statistics import mean, pstdev

try:
    import razdel
except ImportError:
    razdel = None
try:
    import pymorphy3
    _morph = pymorphy3.MorphAnalyzer()
except Exception:
    _morph = None
_lemma_cache = {}

WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.UNICODE)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
EN_SENT = re.compile(r"(?<=[.!?…])[\"”’)]*\s+(?=[\"“‘(A-Z0-9])")
RU_SENT = re.compile(r"(?<=[.!?…])[\"»”)]*\s+(?=[\"«“(А-ЯЁA-Z0-9—–-])")

FIRST = {"en": {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours"},
         "ru": {"я", "меня", "мне", "мной", "мой", "моя", "моё", "мое", "мои", "мы", "нас", "нам", "нами", "наш", "наша", "наше", "наши"}}
SECOND = {"en": {"you", "your", "yours", "yourself"},
          "ru": {"ты", "тебя", "тебе", "тобой", "твой", "твоя", "твои", "вы", "вас", "вам", "вами", "ваш", "ваша", "ваше", "ваши"}}
NOMINAL = {"en": re.compile(r"\w{3,}(?:tion|tions|ment|ments|ness|ity|ities|ance|ence|ances|ences)$"),
           "ru": re.compile(r"\w{2,}(?:ание|ения|ение|аний|ений|анию|ению|анием|ением|ость|ости|остью|ация|ации|аций|ство|ства|ству)$")}
NOT_X_BUT_Y = {"en": re.compile(r"\bnot (?:just|only|merely|simply)\b[^.!?]{0,80}\bbut\b|\b(?:it|this|that)['’]?s not\b[^.!?]{0,60}[,;—–-]\s*(?:it|this|that)['’]?s\b|\bisn['’]t (?:just|about)\b[^.!?]{0,60}\bit['’]?s\b", re.I),
               "ru": re.compile(r"\bне (?:просто|только|столько|лишь)\b[^.!?]{0,80}[,—–-]\s*(?:а|но и|но)\b|\bэто не\b[^.!?]{0,60}[,—–-]\s*(?:а|это)\b", re.I)}
TRIAD = {"en": re.compile(r"\b\w+(?: \w+)?, \w+(?: \w+)?,? (?:and|or) \w+", re.I),
         "ru": re.compile(r"\b\w+(?: \w+)?, \w+(?: \w+)?,? (?:и|или) \w+", re.I)}
CONTRACTION = re.compile(r"\b\w+['’](?:t|s|re|ve|ll|d|m)\b", re.I)
START_CONJ = {"en": re.compile(r"^(?:And|But|So|Or|Because)\b"), "ru": re.compile(r"^(?:И|Но|А|Да|Ну|Вот|Так что)\b")}


def guess_lang(text):
    return "ru" if len(re.findall(r"[а-яёА-ЯЁ]", text)) > len(re.findall(r"[a-zA-Z]", text)) else "en"


def sentences(text, lang):
    if lang == "ru" and razdel:
        return [s.text for s in razdel.sentenize(text) if s.text.strip()]
    rx = RU_SENT if lang == "ru" else EN_SENT
    out = []
    for para in re.split(r"\n+", text):
        out += [s for s in rx.split(para) if s.strip()]
    return out


def lemma(w, lang):
    if lang != "ru":
        return w
    r = _lemma_cache.get(w)
    if r is None:
        r = _morph.parse(w)[0].normal_form if _morph else _crude_stem(w)
        _lemma_cache[w] = r
    return r


def _crude_stem(w):
    # fallback when pymorphy3 is missing: strip common inflections so lemma lists still match roughly
    for suf in ("иями", "ями", "ами", "ого", "его", "ому", "ему", "ыми", "ими", "ой", "ей", "ий", "ый", "ая", "яя", "ое", "ее",
                "ую", "юю", "ом", "ем", "ах", "ях", "ов", "ев", "ть", "ла", "ли", "ло", "ет", "ит", "ут", "ют", "ат", "ят", "ы", "и", "а", "я", "у", "ю", "е", "о"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def tokens(text):
    return [t.lower() for t in WORD.findall(text)]


def mattr(toks, w=50):
    if len(toks) < w:
        return len(set(toks)) / max(1, len(toks))
    vals = [len(set(toks[i:i + w])) / w for i in range(0, len(toks) - w + 1, 5)]
    return mean(vals)


def features(text, lang):
    toks = tokens(text)
    n = max(1, len(toks))
    per_k = lambda c: 1000.0 * c / n
    sents = sentences(text, lang)
    sl = [len(WORD.findall(s)) for s in sents]
    sl = [x for x in sl if x > 0] or [n]
    m = mean(sl)
    sd = pstdev(sl)
    lines = text.splitlines()
    cyr = len(re.findall(r"[а-яё]", text.lower())) or 1
    return {
        "em_dash": per_k(text.count("—")),
        "hyphen_as_dash": per_k(text.count(" - ")),
        "colon": per_k(text.count(":")),
        "semicolon": per_k(text.count(";")),
        "exclamation": per_k(text.count("!")),
        "question_mark": per_k(text.count("?")),
        "three_dots": per_k(text.count("...")),
        "parentheses": per_k(text.count("(")),
        "guillemets": per_k(text.count("«")),
        "curly_quotes": per_k(text.count("“") + text.count("”")),
        "straight_quotes": per_k(text.count('"')),
        "yo_per_1k_cyr": 1000.0 * text.lower().count("ё") / cyr if lang == "ru" else 0.0,
        "sent_len_mean": m,
        "sent_len_sd": sd,
        "sent_len_cv": sd / m if m else 0.0,
        "short_sent_share": sum(x <= 6 for x in sl) / len(sl),
        "long_sent_share": sum(x >= 30 for x in sl) / len(sl),
        "list_lines_share": sum(bool(re.match(r"\s*(?:[-*•–]|\d+[.)])\s+", l)) for l in lines) / max(1, len(lines)),
        "markdown": float(bool(re.search(r"\*\*[^*]+\*\*|^#{1,4} ", text, re.M))),
        "emoji": per_k(len(EMOJI.findall(text))),
        "first_person": per_k(sum(t in FIRST[lang] for t in toks)),
        "second_person": per_k(sum(t in SECOND[lang] for t in toks)),
        "contractions": per_k(len(CONTRACTION.findall(text))) if lang == "en" else 0.0,
        "nominalizations": per_k(sum(bool(NOMINAL[lang].match(t)) for t in toks)),
        "digits": per_k(len(re.findall(r"\d+", text))),
        "mattr": mattr(toks),
        "word_len": mean(len(t) for t in toks) if toks else 0.0,
        "not_x_but_y": per_k(len(NOT_X_BUT_Y[lang].findall(text))),
        "triads": per_k(len(TRIAD[lang].findall(text))),
        "starts_with_conj": mean(bool(START_CONJ[lang].match(s.strip())) for s in sents) if sents else 0.0,
        "question_sent_share": mean(s.strip().endswith("?") for s in sents) if sents else 0.0,
        "words": float(n),
    }


def lemma_grams(text, lang):
    """Set of unigram/bigram lemmas and surface trigrams, as used to build the lexicon."""
    toks = tokens(text)
    base = [lemma(t, lang) for t in toks]
    g = set(base)
    g |= {" ".join(base[i:i + 2]) for i in range(len(base) - 1)}
    g |= {" ".join(toks[i:i + 3]) for i in range(len(toks) - 2)}
    return g


def sigmoid(x):
    return 1 / (1 + math.exp(-x))
