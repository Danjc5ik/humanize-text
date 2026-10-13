"""Train the transparent style model (logistic regression over interpretable features).

Train on LLMTrace validation split, evaluate on the test split (disjoint), per language.
Writes <skill>/data/style_model.json with feature means/stds/weights and held-out metrics.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

SKILL = sys.argv[1]
sys.path.insert(0, os.path.join(SKILL, "scripts"))
import textstats as ts  # noqa: E402

LEX_AI = json.load(open(os.path.join(SKILL, "data", "lexicon_ai_favored.json")))
LEX_HU = json.load(open(os.path.join(SKILL, "data", "lexicon_human_favored.json")))
FEATS = ["sent_len_cv", "short_sent_share", "long_sent_share", "nominalizations", "word_len", "mattr", "first_person",
         "second_person", "digits", "parentheses", "three_dots", "exclamation", "semicolon",
         "triads", "not_x_but_y", "starts_with_conj", "question_sent_share", "markdown", "list_lines_share"]
EXTRA = {"en": ["contractions"], "ru": ["yo_per_1k_cyr"]}


def vec(text, lang, key):
    f = ts.features(text, lang)
    g = ts.lemma_grams(text, lang)
    n = max(1.0, f["words"])
    f["ai_lexicon"] = 1000.0 * sum(1 for x in LEX_AI[key] if x["term"] in g) / n
    f["human_lexicon"] = 1000.0 * sum(1 for x in LEX_HU[key] if x["term"] in g) / n
    return f


def sample(path, lang_code, cap, seed):
    df = pd.read_parquet(path)
    df["nw"] = df.text.str.split().str.len()
    df = df[(df.lang == lang_code) & (df.nw >= 80) & (df.nw <= 1200)]
    parts = []
    for _, g in df.groupby("data_type"):
        h, a = g[g.label == "human"], g[g.label == "ai"]
        k = min(len(h), len(a), cap)
        parts += [h.sample(k, random_state=seed), a.sample(k, random_state=seed)]
    return pd.concat(parts)


out = {}
STRUCT = len(sys.argv) > 4 and sys.argv[4] == "structure"
for lang, code, key in (("ru", "ru", "ru"), ("en", "eng", "eng")):
    cols = FEATS + EXTRA[lang] + ([] if STRUCT else ["ai_lexicon", "human_lexicon"])
    tr = sample(sys.argv[2], code, 700, 1)
    te = sample(sys.argv[3], code, 300, 2)
    Xtr = pd.DataFrame([vec(t, lang, key) for t in tr.text])[cols]
    Xte = pd.DataFrame([vec(t, lang, key) for t in te.text])[cols]
    ytr, yte = (tr.label == "ai").astype(int).values, (te.label == "ai").astype(int).values
    mu, sd = Xtr.mean(), Xtr.std().replace(0, 1)
    clf = LogisticRegression(C=0.5, max_iter=2000).fit((Xtr - mu) / sd, ytr)
    p = clf.predict_proba((Xte - mu) / sd)[:, 1]
    auc = roc_auc_score(yte, p)
    acc = float(((p >= 0.5) == yte).mean())
    fpr = float((p[yte == 0] >= 0.5).mean())
    tpr = float((p[yte == 1] >= 0.5).mean())
    w = dict(zip(cols, clf.coef_[0].round(4)))
    out[lang] = {"features": cols, "mean": mu.round(5).to_dict(), "std": sd.round(5).to_dict(), "weights": w,
                 "intercept": round(float(clf.intercept_[0]), 4),
                 "heldout": {"n": int(len(yte)), "auc": round(auc, 3), "accuracy@0.5": round(acc, 3), "tpr@0.5": round(tpr, 3), "fpr@0.5": round(fpr, 3)},
                 "train_n": int(len(ytr))}
    print(lang, out[lang]["heldout"], flush=True)
    print("  strongest weights:", sorted(w.items(), key=lambda kv: -abs(kv[1]))[:12], flush=True)
json.dump(out, open(os.path.join(SKILL, "data", "structure_model.json" if STRUCT else "style_model.json"), "w"), indent=1)
print("saved")
