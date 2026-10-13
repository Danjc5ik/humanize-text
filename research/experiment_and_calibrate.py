"""Score the before/after experiment texts with the detector panel (models loaded once)."""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detect  # noqa: E402

rows = []
for v in ("original", "cosmetic", "skill"):
    for p in sorted(glob.glob(f"experiment/{v}/*.txt")):
        t = open(p).read()
        lang = "ru" if "_ru_" in p else "en"
        r = {"variant": v, "file": os.path.basename(p), "lang": lang, "words": len(t.split())}
        r.update(detect.run(t, lang))
        rows.append(r)
        print(v, os.path.basename(p), {k: r[k] for k in r if k not in ("variant", "file")}, flush=True)
json.dump(rows, open("experiment/detector_scores.json", "w"), ensure_ascii=False, indent=1)
print("experiment done", flush=True)
