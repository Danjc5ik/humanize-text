#!/usr/bin/env python3
"""Local AI-text detector panel: score a text the way real detectors do, before anyone else does.

Detectors (all open, run on CPU, downloaded on first use to ~/.cache/humanize-detectors):
  ru-modernbert  toiletsandpaper/russian-ai-text-detector-modernbert  (RU classifier, trained on Sber's LLMTrace)
  ru-frida       toiletsandpaper/russian-ai-text-detector-mini-frida  (RU classifier, second opinion)
  en-desklib     desklib/ai-text-detector-v1.01  (EN, DeBERTa-v3-large, top open model on the RAID benchmark)
  binoculars     Qwen2.5-0.5B base vs instruct (zero-shot, any language; Hans et al., ICML 2024) — optional,
                 --binoculars; weak with models this small (AUC 0.87 RU / 0.73 EN on LLMTrace)
Calibration on held-out LLMTrace texts: ru-modernbert AUC 1.00 (FPR 3.6% at 0.5), ru-frida 0.98 (FPR 12.5%),
en-desklib 0.95 (FPR 18%: it flags some human text — treat 0.5–0.7 as uncertain).

Usage:
  python3 detect.py file.txt [more.txt ...] [--lang ru|en|auto] [--only ru-modernbert,binoculars] [--json]
  echo "text" | python3 detect.py - --lang ru
Install: pip install onnxruntime tokenizers huggingface_hub  (RU classifiers)
         pip install torch transformers sentencepiece protobuf  (en-desklib, binoculars)
"""
import argparse
import json
import math
import os
import re
import sys

CACHE = os.environ.get("HUMANIZE_DETECTORS_DIR", os.path.expanduser("~/.cache/humanize-detectors"))
RU_MODELS = {"ru-modernbert": "toiletsandpaper/russian-ai-text-detector-modernbert",
             "ru-frida": "toiletsandpaper/russian-ai-text-detector-mini-frida"}
BINO_OBSERVER, BINO_PERFORMER = "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct"
# Thresholds calibrated on 300 human + 300 AI texts per language from LLMTrace test split (see calibration.json).
BINO_THRESHOLD = {"ru": None, "en": None}
CALIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration.json")
if os.path.exists(CALIB):
    try:
        BINO_THRESHOLD.update(json.load(open(CALIB)).get("binoculars_threshold", {}))
    except Exception:
        pass


def fetch(repo, files):
    from huggingface_hub import hf_hub_download
    d = os.path.join(CACHE, repo.replace("/", "__"))
    for f in files:
        if not os.path.exists(os.path.join(d, f)):
            hf_hub_download(repo, f, local_dir=d)
    return d


def guess_lang(text):
    cyr = len(re.findall(r"[а-яёА-ЯЁ]", text))
    lat = len(re.findall(r"[a-zA-Z]", text))
    return "ru" if cyr > lat else "en"


# ---------------- RU ONNX classifiers ----------------
_ru = {}


def ru_classifier(name, text):
    import numpy as np
    import onnxruntime as ort
    from tokenizers import Tokenizer
    if name not in _ru:
        d = fetch(RU_MODELS[name], ["inference.json", "tokenizer.json", "model_int8.onnx"])
        cfg = json.load(open(os.path.join(d, "inference.json")))
        so = ort.SessionOptions()
        so.intra_op_num_threads = max(1, os.cpu_count() or 1)
        _ru[name] = (cfg, Tokenizer.from_file(os.path.join(d, "tokenizer.json")),
                     ort.InferenceSession(os.path.join(d, "model_int8.onnx"), so, providers=["CPUExecutionProvider"]))
    cfg, tok, sess = _ru[name]
    t = text
    for rule in cfg["normalize"]:  # the detector sees text exactly as its training pipeline did
        t = re.sub(rule["pattern"], rule["replacement"], t, flags=re.M)
    t = t.strip()[: cfg.get("max_chars", 100000)]
    ids = tok.encode(t, add_special_tokens=False).ids[: cfg["max_length"] - 2]
    ids = [cfg["cls_id"]] + ids + [cfg["sep_id"]]
    feed = {"input_ids": np.array([ids], dtype=np.int64), "attention_mask": np.ones((1, len(ids)), dtype=np.int64)}
    logits = sess.run([cfg["output"]], feed)[0][0]
    e = np.exp(logits - logits.max())
    return float(e[cfg["labels"].index("ai")] / e.sum())


# ---------------- EN desklib ----------------
_desk = {}


def en_desklib(text):
    import torch
    import torch.nn as nn
    from transformers import AutoConfig, AutoModel, AutoTokenizer
    if "m" not in _desk:
        from huggingface_hub import snapshot_download
        from safetensors.torch import load_file
        d = snapshot_download("desklib/ai-text-detector-v1.01", cache_dir=CACHE)
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        cfg = AutoConfig.from_pretrained(d)
        base = AutoModel.from_config(cfg)
        sd = load_file(os.path.join(d, "model.safetensors"))
        missing, _ = base.load_state_dict({k[len("model."):]: v for k, v in sd.items() if k.startswith("model.")}, strict=False)
        if len(missing) > 5:
            raise RuntimeError(f"desklib weights did not load ({len(missing)} missing)")
        head = nn.Linear(cfg.hidden_size, 1)
        head.load_state_dict({"weight": sd["classifier.weight"], "bias": sd["classifier.bias"]})
        _desk.update(tok=AutoTokenizer.from_pretrained(d), m=base.eval(), head=head.eval())
    enc = _desk["tok"](text, truncation=True, max_length=768, return_tensors="pt")
    with torch.no_grad():
        h = _desk["m"](input_ids=enc["input_ids"], attention_mask=enc["attention_mask"])[0]
        m = enc["attention_mask"].unsqueeze(-1).float()
        pooled = (h * m).sum(1) / m.sum(1).clamp(min=1e-9)
        return float(torch.sigmoid(_desk["head"](pooled)).item())


# ---------------- Binoculars (zero-shot) ----------------
_bino = {}


def binoculars(text):
    """Lower = more machine-like. log-perplexity / cross-perplexity of two sibling LMs."""
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if "obs" not in _bino:
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        _bino["tok"] = AutoTokenizer.from_pretrained(BINO_OBSERVER, cache_dir=CACHE)
        _bino["obs"] = AutoModelForCausalLM.from_pretrained(BINO_OBSERVER, cache_dir=CACHE, torch_dtype=torch.float32).eval()
        _bino["perf"] = AutoModelForCausalLM.from_pretrained(BINO_PERFORMER, cache_dir=CACHE, torch_dtype=torch.float32).eval()
    ids = _bino["tok"](text, return_tensors="pt", truncation=True, max_length=512)["input_ids"]
    if ids.shape[1] < 8:
        return float("nan")
    with torch.no_grad():
        lo = _bino["obs"](ids).logits[:, :-1].float()
        lp = _bino["perf"](ids).logits[:, :-1].float()
    tgt = ids[:, 1:]
    log_ppl = F.cross_entropy(lp.transpose(1, 2), tgt).item()
    x_ent = (-(F.softmax(lo, -1) * F.log_softmax(lp, -1)).sum(-1)).mean().item()
    return log_ppl / x_ent


def run(text, lang, only=None, bino=False):
    res = {}
    want = lambda k: (only is None and k != "binoculars") or (only is not None and k in only) or (k == "binoculars" and bino)
    if lang == "ru":
        for k in RU_MODELS:
            if want(k):
                try:
                    res[k] = round(ru_classifier(k, text), 3)
                except ImportError as e:
                    res[k] = f"missing: {e.name}"
    if lang == "en" and want("en-desklib"):
        try:
            res["en-desklib"] = round(en_desklib(text), 3)
        except ImportError as e:
            res["en-desklib"] = f"missing: {e.name}"
    if want("binoculars"):
        try:
            b = binoculars(text)
            res["binoculars"] = round(b, 4)
            th = BINO_THRESHOLD.get(lang)
            if th:
                res["binoculars_says_ai"] = b < th
        except ImportError as e:
            res["binoculars"] = f"missing: {e.name}"
    return res


def verdict(res, lang):
    votes = []
    for k, v in res.items():
        if k in RU_MODELS or k == "en-desklib":
            if isinstance(v, float):
                votes.append(v >= 0.5)
        elif k == "binoculars_says_ai":
            votes.append(bool(v))
    if not votes:
        return "no detector available"
    n = sum(votes)
    return f"{n}/{len(votes)} detectors say AI" + (" — reads as human to this panel" if n == 0 else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--lang", default="auto")
    ap.add_argument("--only")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--binoculars", action="store_true", help="also run the zero-shot Binoculars check (weak with small models: AUC 0.87 RU / 0.73 EN; +2 GB download)")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    out = []
    for f in a.files:
        text = sys.stdin.read() if f == "-" else open(f, encoding="utf-8").read()
        lang = guess_lang(text) if a.lang == "auto" else a.lang
        words = len(text.split())
        res = run(text, lang, only, a.binoculars)
        out.append({"file": f, "lang": lang, "words": words, "scores": res, "verdict": verdict(res, lang)})
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    for o in out:
        print(f"{o['file']}  [{o['lang']}, {o['words']} words]  {o['verdict']}")
        for k, v in o["scores"].items():
            print(f"   {k:20s} {v}")
        if o["words"] < 150:
            print("   note: under ~150 words every detector (and this panel) is unreliable")


if __name__ == "__main__":
    main()
