#!/usr/bin/env python3
"""Explain why a text reads as machine-written, with numbers and locations.

Compares the text with human and AI norms measured on LLMTrace (Sber 2025: ~19k RU + ~20k EN texts,
balanced by genre, 30+ generators incl. GPT-4.1, o3, Gemini 2.5, GigaChat, YandexGPT), lists
AI-favoured words/phrases in context, structural patterns, and a transparent style score.

Usage:
  python3 scan.py text.txt [--lang ru|en] [--voice my_sample.txt] [--json]
  cat text.txt | python3 scan.py -
No required dependencies. Optional: pip install pymorphy3 razdel (better Russian lemmas/sentences).
"""
import argparse
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textstats as ts  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
load = lambda n: json.load(open(os.path.join(DATA, n), encoding="utf-8"))

# Structural / phrasal patterns from the literature (Wikipedia "Signs of AI writing", Kobak 2025,
# Reinhart 2025 PNAS, Russian marker studies) plus corpus checks. (regex, label, advice key)
PATTERNS = {
    "en": [
        (r"\b(?:certainly|absolutely|of course|great question)[!,.]", "chatbot reply", "meta"),
        (r"\bI hope (?:this|that) helps\b|\blet me know if\b|\bfeel free to\b|\bhappy to help\b|\bhere(?:'|’)s (?:a|the|your) (?:breakdown|summary|rewrite|version)\b", "chatbot reply", "meta"),
        (r"\bin today(?:'|’)s (?:fast-paced|digital|modern|ever-changing) world\b|\bin an (?:era|age) (?:of|where)\b|\bin the ever-evolving\b|\bimagine a world\b", "stock opener", "open"),
        (r"\blet(?:'|’)s (?:dive|delve)\b|\bdelve into\b|\bwhen it comes to\b", "stock transition", "transition"),
        (r"\bin conclusion\b|\bin summary\b|\bto sum up\b|\bat the end of the day\b|\bthe key takeaway\b|^\s*overall,", "stock closer", "close"),
        (r"\bplays? an? (?:crucial|vital|pivotal|key|important) role\b|\bstands? as an? (?:testament|reminder)\b|\bserves? as an? (?:testament|reminder|beacon)\b|\ba testament to\b", "significance inflation", "inflation"),
        (r"\bunderscores? (?:the|its|their) (?:importance|need|significance)\b|\bhighlights? the importance\b|\bit is (?:worth|important to) not(?:e|ing)\b|\bit(?:'|’)s worth noting\b", "significance inflation", "inflation"),
        (r"\bnot (?:just|only|merely|simply)\b[^.!?]{0,80}\bbut(?: also)?\b|\b(?:it|this|that)(?:'|’)s not\b[^.!?]{0,60}[,;—–-]\s*(?:it|this|that)(?:'|’)s\b", "not X but Y", "negpar"),
        (r"\bno [^.,;!?]{1,30}, no [^.,;!?]{1,30}, (?:just|only)\b", "no X, no Y, just Z", "negpar"),
        (r"\b(?:experts|researchers|scientists|studies|observers|critics) (?:say|argue|agree|suggest|note|have noted|believe)\b|\bmany (?:believe|argue|experts)\b", "vague attribution", "vague"),
        (r"\bwhile specific (?:details|information) (?:is|are) (?:limited|scarce)\b|\bbased on (?:the )?available information\b|\bshould be treated as\b[^.]{0,60}\brather than\b", "hedging disclaimer", "meta"),
        (r"\?\s+(?:The answer|Simple|It(?:'|’)s simple|Because)\b|\bWhy does (?:this|that|it) matter\?", "rhetorical Q then answer", "rhetq"),
        (r"\b(?:serves|stands|functions) as\b|\bboasts\b", "copula avoidance (serves as / boasts)", "copula"),
        (r"(?:^|[.!?]\s+)(?:And that matters|That(?:'|’)s the point|That(?:'|’)s it|Here(?:'|’)s the thing|Here(?:'|’)s why)\.", "punchline fragment", "punch"),
        (r"\b(?:quietly|steady|dependable|multifaceted|leverage|prioritize|universally|echoed|nuanced|robust|seamless(?:ly)?|navigate|landscape|realm|tapestry|vibrant|intricate|pivotal|crucial|delve|showcas(?:e|ing))\b", "AI-era vocabulary (Wikipedia/Kobak lists)", "vocab"),
        (r"^\s*#{1,4} |\*\*[^*\n]+\*\*", "markdown headings/bold in prose", "format"),
        (r"^\s*(?:[-*•]|\d+[.)])\s+\*?\*?[A-Z][^:\n]{1,40}:\s", "inline-header list (**Label:** text)", "format"),
    ],
    "ru": [
        (r"(?:^|[\s«(])(?:Конечно|Безусловно|Отличный вопрос|Хороший вопрос)[!,.]", "ответ чат-бота", "meta"),
        (r"\bНадеюсь, (?:это|мой ответ) (?:поможет|был полезен)\b|\bЕсли у (?:вас|тебя) (?:есть|остались|возникнут) вопросы\b|\bОбращайтесь\b|\bВот (?:несколько|основные|ключевые)\b", "ответ чат-бота", "meta"),
        (r"\b[Дд]авай(?:те)? (?:разберёмся|разберемся|рассмотрим|погрузимся|поговорим)\b", "шаблонный переход", "transition"),
        (r"\b[Вв] (?:современном|нашем|сегодняшнем|быстро меняющемся|стремительно меняющемся) (?:мире|обществе)\b|\b[Вв] эпоху\b|\b[Вв] наше время\b|\b[Нн]а сегодняшний день\b|\b[Вв] последние годы\b", "шаблонное начало", "open"),
        (r"\b[Вв] заключение\b|\b[Пп]одводя итог(?:и)?\b|\b[Тт]аким образом,|\b[Вв] итоге можно сказать\b|^\s*Итак,", "шаблонный вывод", "close"),
        (r"\bигра(?:ет|ют|ть) (?:важную|ключевую|огромную|значительную) роль\b|\bявля(?:ется|ются) (?:важным|ключевым|неотъемлемой)\b|\bподч[её]ркива(?:ет|ют|я) (?:важность|значимость|значение)\b", "раздувание значимости", "inflation"),
        (r"\b(?:[Вв]ажно|[Сс]тоит|[Сс]ледует|[Нн]ельзя не) (?:отметить|подчеркнуть|помнить|учитывать)\b", "«важно отметить»", "inflation"),
        (r"\bне (?:просто|только|столько|лишь)\b[^.!?]{0,80}[,—–-]\s*(?:а|но и)\b|\bэто не\b[^.!?]{0,60}[,—–-]\s*(?:а|это)\b", "«не X, а Y»", "negpar"),
        (r"\b(?:[Оо]днако,? несмотря на)\b", "«однако, несмотря на»", "transition"),
        (r"\b(?:где каждый|мир,? где)\b", "«где каждый / мир, где»", "inflation"),
        (r"\b(?:[Ээ]ксперты|[Уу]ч[её]ные|[Ии]сследования|[Аа]налитики|[Сс]пециалисты) (?:считают|отмечают|показывают|утверждают|сходятся)\b|\b[Мм]ногие (?:считают|полагают|эксперты)\b", "размытая ссылка на авторитет", "vague"),
        (r"\?\s+(?:Потому что|Ответ прост|Всё просто|Все просто)\b|\b[Пп]очему это важно\?", "риторический вопрос + ответ", "rhetq"),
        (r"\b(?:осуществля(?:ть|ет|ется)|в рамках|данн(?:ый|ая|ое|ые|ого|ой)|в целях|с целью|в связи с этим|в настоящее время|вышеупомянут\w*)\b", "канцелярит", "kanc"),
        (r"\b(?:и это нормально|ты не одинок|это не слабость|ты не ошибаешься|позволь себе)\b", "псевдотерапевтический тон", "punch"),
        (r"\bи многое другое\b|\bи т\.\s?д\.\s*$", "«и многое другое»", "vocab"),
        (r"^\s*#{1,4} |\*\*[^*\n]+\*\*", "markdown в прозе", "format"),
    ],
}

ADVICE = {
    "rhythm": "Break the even rhythm: mix 3–6-word sentences with long ones; let one paragraph be a single line.",
    "nominal": "Turn nouns back into verbs (осуществление внедрения → внедрили; the implementation of → we implemented).",
    "wordlen": "Prefer short everyday words over Latinate/abstract ones.",
    "first": "Write from a position: who is speaking, what they did or think (I/we, я/мы) — only if true for the author.",
    "digits": "Replace generalities with specifics: numbers, dates, names, places, prices, quotes.",
    "parens": "Humans aside in brackets, dashes and ellipses more often than models do; asides are fine.",
    "triads": "Break lists of three: keep the one item that matters, or make it two, or four.",
    "negpar": "Say what it is directly instead of 'not X, but Y'.",
    "mattr": "Repeat the plain word instead of rotating synonyms (elegant variation is a model habit).",
    "lexicon": "Swap AI-favoured words (list below) for what a person in this genre would actually say.",
    "humanlex": "Natural connective tissue is missing (ну, вот, же, вообще, кстати / because, I think, a lot, probably) — use what fits the register.",
    "format": "Remove markdown, bold and list scaffolding from prose.",
    "meta": "Delete assistant talk (greetings, offers, 'hope this helps').",
    "open": "Start with the specific point, not a scene-setting cliché.",
    "close": "End on a concrete thought or detail; drop the summary paragraph.",
    "inflation": "Cut significance inflation; state the fact and let it stand.",
    "transition": "Drop stock transitions; ordinary connectors or none.",
    "vague": "Name the source or drop the claim.",
    "rhetq": "Don't ask a question just to answer it.",
    "copula": "Use is/are instead of serves as / stands as / boasts.",
    "punch": "Drop the dramatic one-line punchline or therapeutic reassurance.",
    "vocab": "Replace AI-era vocabulary with plain words.",
    "kanc": "Канцелярит: replace with plain verbs and words.",
    "dash": "English only: many em dashes are a weak, dated tell — keep one or two where they help. (Detectors normalise dashes; this is for human readers.)",
}

# features shown in the report: (name, direction where AI sits, advice key, human-friendly label)
SHOW = [
    ("sent_len_cv", "low", "rhythm", "sentence-length variation (CV)"),
    ("short_sent_share", "low", "rhythm", "share of short sentences (≤6 words)"),
    ("nominalizations", "high", "nominal", "nominalizations per 1000 words"),
    ("word_len", "high", "wordlen", "average word length"),
    ("first_person", "low", "first", "I/we per 1000 words"),
    ("digits", "low", "digits", "numbers per 1000 words"),
    ("parentheses", "low", "parens", "brackets per 1000 words"),
    ("triads", "high", "triads", "lists of three per 1000 words"),
    ("not_x_but_y", "high", "negpar", "'not X but Y' per 1000 words"),
    ("mattr", "high", "mattr", "lexical diversity (MATTR)"),
    ("em_dash", "high", "dash", "em dashes per 1000 words"),
]
# Not shown for Russian: em dashes and lexical diversity do not separate human from AI text there
# (AUC 0.51 and 0.53 on LLMTrace), and detectors normalise dashes anyway.
SKIP = {"ru": {"em_dash", "mattr"}, "en": set()}


def style_score(feat, model):
    z = model["intercept"]
    contrib = {}
    for c in model["features"]:
        v = (feat.get(c, 0.0) - model["mean"][c]) / (model["std"][c] or 1)
        z += model["weights"][c] * v
        contrib[c] = model["weights"][c] * v
    return ts.sigmoid(z), contrib


def lexicon_hits(text, lang, lex, key):
    terms = {x["term"]: x["ratio"] for x in lex[key]}
    hits = []
    for i, s in enumerate(ts.sentences(text, lang)):
        g = ts.lemma_grams(s, lang)
        found = sorted({t for t in terms if t in g}, key=lambda t: -terms[t])
        # prefer the longest n-gram when a shorter one is part of it
        found = [t for t in found if not any(t != u and t in u for u in found)]
        for t in found:
            hits.append({"sentence": i + 1, "term": t, "x_more_in_ai": terms[t], "context": s.strip()[:160]})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--lang", default="auto")
    ap.add_argument("--voice", help="a sample of the author's own writing to compare against")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    lang = ts.guess_lang(text) if a.lang == "auto" else a.lang
    key = "ru" if lang == "ru" else "eng"
    base, model = load("baselines.json")[key], load("style_model.json")[lang]
    f = ts.features(text, lang)
    g = ts.lemma_grams(text, lang)
    n = max(1.0, f["words"])
    lex_ai, lex_hu = load("lexicon_ai_favored.json"), load("lexicon_human_favored.json")
    f["ai_lexicon"] = 1000.0 * sum(1 for x in lex_ai[key] if x["term"] in g) / n
    f["human_lexicon"] = 1000.0 * sum(1 for x in lex_hu[key] if x["term"] in g) / n
    p, contrib = style_score(f, model)
    smodel = None
    if os.path.exists(os.path.join(DATA, "structure_model.json")):
        smodel = load("structure_model.json")[lang]
        ps, scontrib = style_score(f, smodel)
    else:
        ps, scontrib = None, {}

    flags = []
    for name, side, adv, label in SHOW:
        if name in SKIP[lang]:
            continue
        b = base.get(name)
        if not b:
            continue
        v = f[name]
        lo, hi = b["human_p25"], b["human_p75"]
        bad = (side == "low" and v < lo and b["ai_p50"] < b["human_p50"]) or (side == "high" and v > hi and b["ai_p50"] >= b["human_p50"])
        flags.append({"feature": label, "value": round(v, 3), "human_typical": f"{lo}–{hi}", "ai_median": b["ai_p50"], "ai_like": bool(bad), "advice": ADVICE[adv] if bad else ""})

    pats = []
    for rx, label, adv in PATTERNS[lang]:
        for m in re.finditer(rx, text, flags=re.M | re.I if lang == "en" else re.M):
            s = max(0, m.start() - 50)
            pats.append({"pattern": label, "match": m.group(0).strip()[:80], "context": text[s:m.end() + 60].replace("\n", " ").strip(), "advice": ADVICE[adv]})
    lex = lexicon_hits(text, lang, lex_ai, key)
    top = sorted(contrib.items(), key=lambda kv: -kv[1])[:5]

    voice = None
    if a.voice:
        vt = open(a.voice, encoding="utf-8").read()
        vf = ts.features(vt, ts.guess_lang(vt))
        voice = {k: {"yours": round(vf[k], 3), "this_text": round(f[k], 3)} for k in
                 ("sent_len_mean", "sent_len_cv", "short_sent_share", "first_person", "second_person", "nominalizations", "word_len",
                  "em_dash", "hyphen_as_dash", "three_dots", "parentheses", "exclamation", "question_sent_share", "contractions", "guillemets", "straight_quotes")}

    stop = sorted(scontrib.items(), key=lambda kv: -kv[1])[:5]
    res = {"lang": lang, "words": int(n), "style_score_ai": round(p, 3),
           "structure_score_ai": round(ps, 3) if ps is not None else None,
           "top_ai_signals": [k for k, v in top if v > 0.15] + [k for k, v in stop if v > 0.15 and k not in dict(top)],
           "metrics": flags, "patterns": pats, "lexicon": lex, "human_lexicon_per_1k": round(f["human_lexicon"], 2), "voice": voice}
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return

    v = lambda x: "machine-like" if x >= 0.7 else "mixed" if x >= 0.4 else "human-like"
    print(f"# Scan [{lang}, {int(n)} words]")
    print(f"Style score (words + structure): {p:.2f} — {v(p)}   [held-out AUC {model['heldout']['auc']}]")
    if ps is not None:
        print(f"Structure score (no word lists): {ps:.2f} — {v(ps)}   [held-out AUC {smodel['heldout']['auc']}]")
        if p < 0.4 <= ps:
            print("  ↳ Words look clean but the structure still reads as a model: fix rhythm, nominal style, person, specifics.")
    if n < 150:
        print("(Under ~150 words every statistic and detector is noisy.)")
    if lang == "ru" and (ts.razdel is None or ts._morph is None):
        print("(Russian scores are approximate: run `pip install pymorphy3 razdel` — the norms were measured with them.)")
    if res["top_ai_signals"]:
        print("Strongest machine signals: " + ", ".join(res["top_ai_signals"]))
    print("\n## Measurements vs human norms (LLMTrace, middle 50% of human texts)")
    for fl in flags:
        mark = "AI-LIKE" if fl["ai_like"] else "ok     "
        print(f"[{mark}] {fl['feature']}: {fl['value']} (humans {fl['human_typical']}, AI median {fl['ai_median']})" + (f"\n          → {fl['advice']}" if fl["ai_like"] else ""))
    print(f"[info ] natural connectors (ну/вот/же… · because/I think…) per 1000 words: {res['human_lexicon_per_1k']}")
    if pats:
        print(f"\n## Patterns ({len(pats)})")
        for x in pats[:40]:
            print(f"- {x['pattern']}: «{x['match']}» … {x['context'][:120]}")
    if lex:
        print(f"\n## AI-favoured words in context ({len(lex)}) — 'x' = how many times more common in AI texts of the same genre")
        for x in lex[:40]:
            print(f"- s{x['sentence']}: {x['term']} ({x['x_more_in_ai']}x) … {x['context'][:110]}")
    if voice:
        print("\n## Your voice vs this text")
        for k, v in voice.items():
            print(f"- {k}: yours {v['yours']}  | this text {v['this_text']}")


if __name__ == "__main__":
    main()
