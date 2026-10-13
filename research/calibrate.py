"""Calibrate the local detector panel on held-out human/AI texts from LLMTrace (test split)."""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detect  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 150
df = pd.read_parquet(src)
df["nw"] = df.text.str.split().str.len()
df = df[(df.nw >= 120) & (df.nw <= 500) & (df.data_type != "poetry")]
rows = []
for lang, code in (("ru", "ru"), ("eng", "en")):
    for label in ("human", "ai"):
        g = df[(df.lang == lang) & (df.label == label)]
        per = max(1, N // g.data_type.nunique())
        s = pd.concat([x.sample(min(len(x), per), random_state=1) for _, x in g.groupby("data_type")])
        s = s.sample(min(N, len(s)), random_state=1)
        for _, r in s.iterrows():
            rows.append({"lang": code, "label": label, "model": r.model, "domain": r.data_type, "text": r.text})
print(len(rows), "texts", flush=True)
t0 = time.time()
for i, r in enumerate(rows):
    r.update(detect.run(r["text"], r["lang"]))
    if i % 50 == 0:
        print(i, round(time.time() - t0), "s", flush=True)
res = pd.DataFrame(rows)
res.drop(columns=["text"]).to_csv(os.path.join(out, "calibration_scores.csv"), index=False)

summary = {"binoculars_threshold": {}}
for lang in ("ru", "en"):
    s = res[res.lang == lang]
    y = (s.label == "ai").astype(int)
    for det in [c for c in ("ru-modernbert", "ru-frida", "en-desklib", "binoculars") if c in s and s[c].notna().any()]:
        x = s[det].astype(float)
        score = -x if det == "binoculars" else x
        auc = roc_auc_score(y, score)
        entry = {"auc": round(auc, 3)}
        if det == "binoculars":
            fpr, tpr, thr = roc_curve(y, score)
            ok = np.where(fpr <= 0.05)[0]
            k = ok[np.argmax(tpr[ok])]
            entry.update({"threshold_fpr5": round(float(-thr[k]), 4), "tpr_at_fpr5": round(float(tpr[k]), 3)})
            j = np.argmax(tpr - fpr)
            entry.update({"threshold_youden": round(float(-thr[j]), 4), "tpr_youden": round(float(tpr[j]), 3), "fpr_youden": round(float(fpr[j]), 3)})
            summary["binoculars_threshold"][lang] = entry["threshold_fpr5"]
        else:
            pred = x >= 0.5
            entry.update({"tpr@0.5": round(float(pred[y == 1].mean()), 3), "fpr@0.5": round(float(pred[y == 0].mean()), 3)})
        summary[f"{lang}:{det}"] = entry
json.dump(summary, open(os.path.join(out, "calibration.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
