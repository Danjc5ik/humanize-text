"""What actually separates human from LLM text? Measured on LLMTrace (Sber, 2025), RU + EN.

Balanced per domain (same number of human and AI texts in each genre), so genre mix can't fake a
difference. Outputs feature effect sizes (AUC), per-model profiles and over-/under-used n-grams.

Usage: python3 analyze_corpus.py <llmtrace.parquet> <out_dir>
"""
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
CAP = 1500
rng = np.random.default_rng(0)

import pymorphy3
import razdel

morph = pymorphy3.MorphAnalyzer()
_lemma_cache = {}


def lemma(w):
    r = _lemma_cache.get(w)
    if r is None:
        r = morph.parse(w)[0].normal_form
        _lemma_cache[w] = r
    return r


WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.UNICODE)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
EN_SENT = re.compile(r"(?<=[.!?…])[\"”’)]*\s+(?=[\"“‘(A-Z0-9])")

FIRST = {"eng": {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours"},
         "ru": {"я", "меня", "мне", "мной", "мой", "моя", "моё", "мое", "мои", "мы", "нас", "нам", "нами", "наш", "наша", "наше", "наши"}}
SECOND = {"eng": {"you", "your", "yours", "yourself"},
          "ru": {"ты", "тебя", "тебе", "тобой", "твой", "твоя", "твои", "вы", "вас", "вам", "вами", "ваш", "ваша", "ваше", "ваши"}}
NOMINAL = {"eng": re.compile(r"\w{3,}(?:tion|tions|ment|ments|ness|ity|ities|ance|ence|ances|ences)$"),
           "ru": re.compile(r"\w{2,}(?:ание|ения|ение|аний|ений|анию|ению|анием|ением|ость|ости|остью|ация|ации|аций|ство|ства|ству)$")}
NOT_X_BUT_Y = {"eng": re.compile(r"\bnot (?:just|only|merely|simply)\b[^.!?]{0,80}\bbut\b|\b(?:it|this|that)['’]?s not\b[^.!?]{0,60}[,;—–-]\s*(?:it|this|that)['’]?s\b|\bisn['’]t (?:just|about)\b[^.!?]{0,60}\bit['’]?s\b", re.I),
               "ru": re.compile(r"\bне (?:просто|только|столько|лишь)\b[^.!?]{0,80}[,—–-]\s*(?:а|но и|но)\b|\bэто не\b[^.!?]{0,60}[,—–-]\s*(?:а|это)\b", re.I)}
TRIAD = {"eng": re.compile(r"\b\w+(?: \w+)?, \w+(?: \w+)?,? (?:and|or) \w+", re.I),
         "ru": re.compile(r"\b\w+(?: \w+)?, \w+(?: \w+)?,? (?:и|или) \w+", re.I)}
CONTRACTION = re.compile(r"\b\w+['’](?:t|s|re|ve|ll|d|m)\b", re.I)
START_CONJ = {"eng": re.compile(r"^(?:And|But|So|Or|Because)\b"), "ru": re.compile(r"^(?:И|Но|А|Да|Ну|Вот|Так что)\b")}


def sentences(text, lang):
    if lang == "ru":
        return [s.text for s in razdel.sentenize(text) if s.text.strip()]
    return [s for s in EN_SENT.split(text) if s.strip()]


def mattr(tokens, w=50):
    if len(tokens) < w:
        return len(set(tokens)) / max(1, len(tokens))
    vals = [len(set(tokens[i:i + w])) / w for i in range(0, len(tokens) - w + 1, 5)]
    return float(np.mean(vals))


def features(text, lang):
    toks = [t.lower() for t in WORD.findall(text)]
    n = max(1, len(toks))
    per_k = lambda c: 1000.0 * c / n
    sents = sentences(text, lang)
    sl = np.array([len(WORD.findall(s)) for s in sents]) if sents else np.array([n])
    sl = sl[sl > 0] if (sl > 0).any() else np.array([n])
    paras = [p for p in re.split(r"\n\s*\n|\n", text) if p.strip()]
    pl = np.array([len(WORD.findall(p)) for p in paras]) if paras else np.array([n])
    lines = text.splitlines()
    cyr = len(re.findall(r"[а-яё]", text.lower())) or 1
    return {
        "em_dash": per_k(text.count("—")),
        "en_dash_spaced": per_k(text.count(" – ")),
        "hyphen_as_dash": per_k(text.count(" - ")),
        "colon": per_k(text.count(":")),
        "semicolon": per_k(text.count(";")),
        "exclamation": per_k(text.count("!")),
        "question_mark": per_k(text.count("?")),
        "ellipsis_char": per_k(text.count("…")),
        "three_dots": per_k(text.count("...")),
        "parentheses": per_k(text.count("(")),
        "guillemets": per_k(text.count("«")),
        "curly_quotes": per_k(text.count("“") + text.count("”")),
        "straight_quotes": per_k(text.count('"')),
        "curly_apostrophe": per_k(text.count("’")),
        "yo_per_1k_cyr": 1000.0 * text.lower().count("ё") / cyr if lang == "ru" else 0.0,
        "sent_len_mean": float(sl.mean()),
        "sent_len_sd": float(sl.std()),
        "sent_len_cv": float(sl.std() / sl.mean()) if sl.mean() else 0.0,
        "short_sent_share": float((sl <= 6).mean()),
        "long_sent_share": float((sl >= 30).mean()),
        "para_len_cv": float(pl.std() / pl.mean()) if len(pl) > 1 and pl.mean() else 0.0,
        "list_lines_share": sum(bool(re.match(r"\s*(?:[-*•–]|\d+[.)])\s+", l)) for l in lines) / max(1, len(lines)),
        "markdown": float(bool(re.search(r"\*\*[^*]+\*\*|^#{1,4} ", text, re.M))),
        "emoji": per_k(len(EMOJI.findall(text))),
        "first_person": per_k(sum(t in FIRST[lang] for t in toks)),
        "second_person": per_k(sum(t in SECOND[lang] for t in toks)),
        "contractions": per_k(len(CONTRACTION.findall(text))) if lang == "eng" else 0.0,
        "nominalizations": per_k(sum(bool(NOMINAL[lang].match(t)) for t in toks)),
        "digits": per_k(len(re.findall(r"\d+", text))),
        "mattr": mattr(toks),
        "word_len": float(np.mean([len(t) for t in toks])) if toks else 0.0,
        "not_x_but_y": per_k(len(NOT_X_BUT_Y[lang].findall(text))),
        "triads": per_k(len(TRIAD[lang].findall(text))),
        "starts_with_conj": float(np.mean([bool(START_CONJ[lang].match(s.strip())) for s in sents])) if sents else 0.0,
        "question_sent_share": float(np.mean([s.strip().endswith("?") for s in sents])) if sents else 0.0,
        "words": float(n),
    }


def grams(text, lang):
    toks = [t.lower() for t in WORD.findall(text)]
    base = [lemma(t) for t in toks] if lang == "ru" else toks
    g = set(base)
    g |= {" ".join(base[i:i + 2]) for i in range(len(base) - 1)}
    g |= {" ".join(toks[i:i + 3]) for i in range(len(toks) - 2)}  # trigrams on surface forms
    return g


df = pd.read_parquet(src)
df["nw"] = df.text.str.split().str.len()
df = df[(df.nw >= 60) & (df.nw <= 1200)]
parts = []
for (lang, dom), g in df.groupby(["lang", "data_type"]):
    h, a = g[g.label == "human"], g[g.label == "ai"]
    k = min(len(h), len(a), CAP)
    if k < 50:
        continue
    parts.append(h.sample(k, random_state=0))
    parts.append(a.sample(k, random_state=0))
bal = pd.concat(parts).reset_index(drop=True)
print(bal.groupby(["lang", "label"]).size(), flush=True)

report = {}
for lang in ["ru", "eng"]:
    sub = bal[bal.lang == lang].copy()
    feats = pd.DataFrame([features(t, lang) for t in sub.text])
    feats["label"] = (sub.label.values == "ai").astype(int)
    feats["model"] = sub.model.values
    feats["domain"] = sub.data_type.values
    feats.to_parquet(os.path.join(out, f"features_{lang}.parquet"))
    rows = []
    for c in feats.columns:
        if c in ("label", "model", "domain") or feats[c].std() == 0:
            continue
        h, a = feats.loc[feats.label == 0, c], feats.loc[feats.label == 1, c]
        auc = roc_auc_score(feats.label, feats[c])
        rows.append({"feature": c, "human_mean": round(h.mean(), 3), "ai_mean": round(a.mean(), 3),
                     "human_median": round(h.median(), 3), "ai_median": round(a.median(), 3),
                     "auc_ai_higher": round(auc, 3), "share_human_nonzero": round((h > 0).mean(), 3),
                     "share_ai_nonzero": round((a > 0).mean(), 3)})
    ft = pd.DataFrame(rows)
    ft["strength"] = (ft.auc_ai_higher - 0.5).abs()
    ft = ft.sort_values("strength", ascending=False)
    report[f"features_{lang}"] = ft.to_dict(orient="records")
    # per-domain AUC for the strongest features
    top = ft.feature.head(12).tolist()
    dom = {}
    for d, g in feats.groupby("domain"):
        dom[d] = {c: round(roc_auc_score(g.label, g[c]), 3) for c in top if g[c].std() > 0 and g.label.nunique() == 2}
    report[f"domain_auc_{lang}"] = dom
    # per-model profiles (models with >= 150 texts in the balanced set)
    prof = {}
    hm = feats[feats.label == 0][top].mean()
    for m, g in feats[feats.label == 1].groupby("model"):
        if len(g) >= 150:
            prof[m] = {c: round(float(g[c].mean()), 2) for c in top}
    prof["HUMAN"] = {c: round(float(hm[c]), 2) for c in top}
    report[f"models_{lang}"] = prof

    # n-grams: document frequency, two-proportion z-score
    dfh, dfa = Counter(), Counter()
    nh = na = 0
    for t, lab in zip(sub.text, sub.label):
        g = grams(t, lang)
        if lab == "ai":
            dfa.update(g); na += 1
        else:
            dfh.update(g); nh += 1
    res = []
    for term in set(dfa) | set(dfh):
        a, h = dfa.get(term, 0), dfh.get(term, 0)
        if a + h < 40:
            continue
        pa, ph = (a + 0.5) / (na + 1), (h + 0.5) / (nh + 1)
        p = (a + h) / (na + nh)
        se = math.sqrt(p * (1 - p) * (1 / na + 1 / nh)) or 1e-9
        res.append((term, a, h, round(pa / ph, 2), round((pa - ph) / se, 1)))
    res.sort(key=lambda x: -x[4])
    ai_fav = [r for r in res if r[3] >= 2.0][:400]
    hu_fav = sorted([r for r in res if r[3] <= 0.5], key=lambda x: x[4])[:400]
    report[f"ngrams_ai_{lang}"] = ai_fav
    report[f"ngrams_human_{lang}"] = hu_fav
    report[f"n_{lang}"] = {"human": nh, "ai": na}
    print(lang, "done", flush=True)

json.dump(report, open(os.path.join(out, "findings.json"), "w"), ensure_ascii=False, indent=1)
print("saved")
