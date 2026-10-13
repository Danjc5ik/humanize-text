#!/usr/bin/env python3
"""Fingerprint an author's own writing so a rewrite can match it.

Give it one or more samples the person really wrote (messages, old essays, posts — 300+ words in
total is good, 1000+ is better). It prints a "voice card": rhythm, punctuation habits, how they
start sentences, their connectors and fillers, person, formality — as concrete targets.

Usage: python3 voice.py sample1.txt [sample2.txt ...] [--json]
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textstats as ts  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = "\n\n".join(open(f, encoding="utf-8").read() for f in a.files)
    lang = ts.guess_lang(text)
    key = "ru" if lang == "ru" else "eng"
    f = ts.features(text, lang)
    sents = ts.sentences(text, lang)
    lens = sorted(len(ts.WORD.findall(s)) for s in sents if ts.WORD.findall(s))
    q = lambda p: lens[min(len(lens) - 1, int(p * len(lens)))] if lens else 0
    openers = Counter()
    for s in sents:
        w = ts.WORD.findall(s)
        if w:
            openers[w[0].lower()] += 1
    hum = json.load(open(os.path.join(DATA, "lexicon_human_favored.json"), encoding="utf-8"))[key]
    g = ts.lemma_grams(text, lang)
    connectors = [x["term"] for x in hum if x["term"] in g][:25]
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    plens = [len(ts.WORD.findall(p)) for p in paras]
    habits = {
        "dash style": "em dash —" if f["em_dash"] > f["hyphen_as_dash"] else ("hyphen ' - ' as dash" if f["hyphen_as_dash"] > 0 else "rarely uses dashes"),
        "quotes": "«ёлочки»" if f["guillemets"] > max(f["straight_quotes"], f["curly_quotes"]) else ('straight "quotes"' if f["straight_quotes"] > 0 else ("curly “quotes”" if f["curly_quotes"] > 0 else "rarely quotes")),
        "ellipsis ...": round(f["three_dots"], 1),
        "brackets ( )": round(f["parentheses"], 1),
        "exclamations !": round(f["exclamation"], 1),
        "questions (share of sentences)": round(f["question_sent_share"], 2),
        "ё used": (f["yo_per_1k_cyr"] > 0.5) if lang == "ru" else None,
        "starts sentences with And/But/И/Но/А (share)": round(f["starts_with_conj"], 2),
    }
    card = {
        "lang": lang,
        "words": int(f["words"]),
        "sentence_length": {"median": q(0.5), "p10": q(0.1), "p90": q(0.9), "cv": round(f["sent_len_cv"], 2),
                            "short_share": round(f["short_sent_share"], 2)},
        "paragraph_words_median": sorted(plens)[len(plens) // 2] if plens else None,
        "person_per_1k": {"first": round(f["first_person"], 1), "second": round(f["second_person"], 1)},
        "contractions_per_1k": round(f["contractions"], 1) if lang == "en" else None,
        "nominalizations_per_1k": round(f["nominalizations"], 1),
        "avg_word_len": round(f["word_len"], 2),
        "punctuation_and_habits": habits,
        "frequent_sentence_openers": [w for w, _ in openers.most_common(10)],
        "natural_connectors_used": connectors,
    }
    if a.json:
        print(json.dumps(card, ensure_ascii=False, indent=1))
        return
    print(f"# Voice card [{lang}, {card['words']} words of samples]")
    if card["words"] < 300:
        print("(Small sample — treat these as hints, not targets.)")
    sl = card["sentence_length"]
    print(f"- Sentences: median {sl['median']} words, range {sl['p10']}–{sl['p90']}, variation CV {sl['cv']}, short (≤6) {int(sl['short_share'] * 100)}%")
    if card["paragraph_words_median"]:
        print(f"- Paragraphs: ~{card['paragraph_words_median']} words")
    print(f"- Person: I/we {card['person_per_1k']['first']} per 1000 words, you {card['person_per_1k']['second']}")
    if lang == "en":
        print(f"- Contractions: {card['contractions_per_1k']} per 1000 words")
    print(f"- Formality: nominalizations {card['nominalizations_per_1k']} per 1000 words, average word {card['avg_word_len']} letters")
    for k, v in habits.items():
        if v is not None:
            print(f"- {k}: {v}")
    print(f"- Opens sentences with: {', '.join(card['frequent_sentence_openers'])}")
    if connectors:
        print(f"- Connectors/fillers they use: {', '.join(connectors)}")
    print("\nMatch these in the rewrite: rhythm and sentence range first, then punctuation habits, person, connectors.")


if __name__ == "__main__":
    main()
